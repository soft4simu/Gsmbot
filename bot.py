#!/usr/bin/env python3
"""
FirmwareShop Bot - Professional Telegram Bot for selling Firmwares, Solutions & Source Codes
Supports: Multi-language, Credits System, M-Pesa, Binance, and more
"""

import os
import json
import logging
import asyncio
from datetime import datetime
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, KeyboardButton
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, filters, ContextTypes
)
from database import Database
from language_detector import detect_language, get_text
from payment_handler import PaymentHandler
from config import BOT_TOKEN, ADMIN_IDS

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# States
SEARCH, SELECT_PRODUCT, SELECT_PAYMENT, CONFIRM_PAYMENT, ENTER_AMOUNT = range(5)

db = Database()
payment = PaymentHandler()


# ─────────────────────────────────────────────
# START COMMAND
# ─────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    lang = db.get_user_language(user.id) or "en"
    
    # Register user if new
    is_new = db.register_user(
        user_id=user.id,
        username=user.username or "",
        full_name=user.full_name,
        language=lang
    )
    
    credits = db.get_credits(user.id)
    
    welcome_msg = get_text("welcome", lang).format(
        name=user.first_name,
        credits=credits,
        new_badge="🎁 " + get_text("new_user_bonus", lang) if is_new else ""
    )
    
    keyboard = [
        [
            InlineKeyboardButton("🔍 " + get_text("search", lang), callback_data="search"),
            InlineKeyboardButton("📦 " + get_text("categories", lang), callback_data="categories")
        ],
        [
            InlineKeyboardButton("💳 " + get_text("buy_credits", lang), callback_data="buy_credits"),
            InlineKeyboardButton("👤 " + get_text("my_account", lang), callback_data="my_account")
        ],
        [
            InlineKeyboardButton("🌍 " + get_text("change_language", lang), callback_data="change_language"),
            InlineKeyboardButton("📞 " + get_text("support", lang), callback_data="support")
        ]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if update.message:
        await update.message.reply_text(
            welcome_msg,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )
    else:
        await update.callback_query.edit_message_text(
            welcome_msg,
            reply_markup=reply_markup,
            parse_mode="HTML"
        )


# ─────────────────────────────────────────────
# SEARCH HANDLER
# ─────────────────────────────────────────────
async def handle_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lang = db.get_user_language(query.from_user.id) or "en"
    
    await query.answer()
    await query.edit_message_text(
        get_text("search_prompt", lang),
        parse_mode="HTML"
    )
    context.user_data["state"] = "searching"


async def process_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    lang = db.get_user_language(user.id) or "en"
    
    # Auto-detect language from message
    detected_lang = detect_language(text)
    if detected_lang and detected_lang != lang:
        db.update_user_language(user.id, detected_lang)
        lang = detected_lang
    
    state = context.user_data.get("state", "")
    
    if state == "searching":
        await search_products(update, context, text, lang)
    elif state == "awaiting_mpesa_code":
        await verify_mpesa(update, context, text, lang)
    elif state == "awaiting_binance_txid":
        await verify_binance(update, context, text, lang)
    else:
        # Default: try to search
        await search_products(update, context, text, lang)


async def search_products(update: Update, context: ContextTypes.DEFAULT_TYPE, query: str, lang: str):
    results = db.search_products(query)
    
    if not results:
        # Try fuzzy match
        suggestions = db.get_suggestions(query, limit=5)
        
        if suggestions:
            msg = get_text("not_found_suggestions", lang).format(query=query) + "\n\n"
            keyboard = []
            for s in suggestions:
                price_label = f"FREE" if s['price'] == 0 else f"{s['price']} Credits"
                keyboard.append([InlineKeyboardButton(
                    f"📦 {s['name']} - {price_label}",
                    callback_data=f"product_{s['id']}"
                )])
            keyboard.append([InlineKeyboardButton("🔙 " + get_text("back", lang), callback_data="main_menu")])
            await update.message.reply_text(
                msg,
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text(
                get_text("not_found", lang).format(query=query),
                parse_mode="HTML"
            )
        return
    
    # Show results
    msg = get_text("search_results", lang).format(count=len(results), query=query) + "\n\n"
    keyboard = []
    
    for product in results[:10]:
        price_label = get_text("free", lang) if product['price'] == 0 else f"{product['price']} Credits"
        badge = "🆓" if product['price'] == 0 else "💎"
        keyboard.append([InlineKeyboardButton(
            f"{badge} {product['name']} [{product['category']}] - {price_label}",
            callback_data=f"product_{product['id']}"
        )])
    
    keyboard.append([InlineKeyboardButton("🔙 " + get_text("back", lang), callback_data="main_menu")])
    
    await update.message.reply_text(
        msg,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )
    context.user_data["state"] = ""


# ─────────────────────────────────────────────
# PRODUCT DETAIL
# ─────────────────────────────────────────────
async def show_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    product_id = int(query.data.split("_")[1])
    user = query.from_user
    lang = db.get_user_language(user.id) or "en"
    product = db.get_product(product_id)
    
    if not product:
        await query.edit_message_text(get_text("product_not_found", lang))
        return
    
    credits = db.get_credits(user.id)
    can_afford = credits >= product['price']
    
    price_display = get_text("free", lang) if product['price'] == 0 else f"{product['price']} Credits"
    
    msg = f"""
<b>📦 {product['name']}</b>
━━━━━━━━━━━━━━━━━━━━
🏷️ <b>{get_text('category', lang)}:</b> {product['category']}
💰 <b>{get_text('price', lang)}:</b> {price_display}
📝 <b>{get_text('description', lang)}:</b>
{product['description']}

🌟 <b>{get_text('version', lang)}:</b> {product.get('version', 'Latest')}
📅 <b>{get_text('updated', lang)}:</b> {product.get('updated_at', 'N/A')}
━━━━━━━━━━━━━━━━━━━━
💳 {get_text('your_credits', lang)}: <b>{credits} Credits</b>
"""
    
    keyboard = []
    
    if product['price'] == 0:
        keyboard.append([InlineKeyboardButton(
            "🆓 " + get_text("download_free", lang),
            callback_data=f"download_{product_id}"
        )])
    elif can_afford:
        keyboard.append([InlineKeyboardButton(
            f"✅ {get_text('buy_with_credits', lang)} ({product['price']} Credits)",
            callback_data=f"buy_{product_id}"
        )])
    else:
        needed = product['price'] - credits
        keyboard.append([InlineKeyboardButton(
            f"⚠️ {get_text('need_more_credits', lang)} ({needed} more)",
            callback_data="buy_credits"
        )])
        keyboard.append([InlineKeyboardButton(
            "💳 " + get_text("buy_credits", lang),
            callback_data="buy_credits"
        )])
    
    keyboard.append([InlineKeyboardButton("🔙 " + get_text("back", lang), callback_data="categories")])
    
    await query.edit_message_text(
        msg,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )


# ─────────────────────────────────────────────
# CATEGORIES
# ─────────────────────────────────────────────
async def show_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = db.get_user_language(query.from_user.id) or "en"
    
    categories = db.get_categories()
    
    keyboard = []
    icons = {"Firmware": "🔧", "Solution": "💡", "Source Code": "💻", "Tools": "🛠️", "Other": "📦"}
    
    for cat in categories:
        count = db.count_products_in_category(cat['name'])
        icon = icons.get(cat['name'], "📦")
        keyboard.append([InlineKeyboardButton(
            f"{icon} {cat['name']} ({count} items)",
            callback_data=f"category_{cat['id']}"
        )])
    
    keyboard.append([InlineKeyboardButton("🔙 " + get_text("back", lang), callback_data="main_menu")])
    
    await query.edit_message_text(
        f"<b>📂 {get_text('select_category', lang)}</b>",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )


async def show_category_products(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    cat_id = int(query.data.split("_")[1])
    lang = db.get_user_language(query.from_user.id) or "en"
    
    products = db.get_products_by_category(cat_id)
    category = db.get_category(cat_id)
    
    if not products:
        await query.edit_message_text(
            get_text("no_products_in_category", lang),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🔙 " + get_text("back", lang), callback_data="categories")
            ]])
        )
        return
    
    keyboard = []
    for p in products:
        price_label = get_text("free", lang) if p['price'] == 0 else f"{p['price']} CR"
        badge = "🆓" if p['price'] == 0 else "💎"
        keyboard.append([InlineKeyboardButton(
            f"{badge} {p['name']} - {price_label}",
            callback_data=f"product_{p['id']}"
        )])
    
    keyboard.append([InlineKeyboardButton("🔙 " + get_text("back", lang), callback_data="categories")])
    
    await query.edit_message_text(
        f"<b>📂 {category['name']}</b> - {len(products)} {get_text('items', lang)}",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )


# ─────────────────────────────────────────────
# PURCHASE FLOW
# ─────────────────────────────────────────────
async def buy_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    product_id = int(query.data.split("_")[1])
    user = query.from_user
    lang = db.get_user_language(user.id) or "en"
    product = db.get_product(product_id)
    credits = db.get_credits(user.id)
    
    if credits < product['price']:
        await query.edit_message_text(get_text("insufficient_credits", lang))
        return
    
    # Deduct credits and give download
    db.deduct_credits(user.id, product['price'])
    db.record_purchase(user.id, product_id)
    
    await deliver_product(query, product, lang)


async def download_free(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    product_id = int(query.data.split("_")[1])
    lang = db.get_user_language(query.from_user.id) or "en"
    product = db.get_product(product_id)
    
    db.record_purchase(query.from_user.id, product_id)
    await deliver_product(query, product, lang)


async def deliver_product(query, product, lang):
    """Deliver the product to user"""
    msg = f"""
✅ <b>{get_text('purchase_success', lang)}</b>
━━━━━━━━━━━━━━━━━━━━
📦 <b>{product['name']}</b>

🔗 <b>{get_text('download_link', lang)}:</b>
<code>{product.get('download_link', 'Link will be sent shortly')}</code>

🔑 <b>{get_text('license_key', lang)}:</b>
<code>{product.get('license_key', 'N/A')}</code>

📝 <b>{get_text('instructions', lang)}:</b>
{product.get('instructions', 'Check documentation')}
━━━━━━━━━━━━━━━━━━━━
⚠️ {get_text('do_not_share', lang)}
"""
    keyboard = [[InlineKeyboardButton("🏠 " + get_text("home", lang), callback_data="main_menu")]]
    
    await query.edit_message_text(
        msg,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )


# ─────────────────────────────────────────────
# BUY CREDITS
# ─────────────────────────────────────────────
async def buy_credits_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = db.get_user_language(query.from_user.id) or "en"
    
    packages = [
        {"credits": 100, "price_usd": 1, "price_kes": 130, "bonus": 0},
        {"credits": 500, "price_usd": 4, "price_kes": 520, "bonus": 50},
        {"credits": 1000, "price_usd": 7, "price_kes": 910, "bonus": 150},
        {"credits": 5000, "price_usd": 30, "price_kes": 3900, "bonus": 1000},
    ]
    
    msg = f"<b>💳 {get_text('buy_credits', lang)}</b>\n\n"
    msg += f"1 Credit = $0.01 USD\n\n"
    
    keyboard = []
    for pkg in packages:
        bonus_text = f" +{pkg['bonus']} BONUS" if pkg['bonus'] > 0 else ""
        keyboard.append([InlineKeyboardButton(
            f"💎 {pkg['credits']}{bonus_text} Credits - ${pkg['price_usd']} / KES {pkg['price_kes']}",
            callback_data=f"pkg_{pkg['credits']}_{pkg['price_usd']}_{pkg['price_kes']}_{pkg['bonus']}"
        )])
    
    keyboard.append([InlineKeyboardButton("🔙 " + get_text("back", lang), callback_data="main_menu")])
    
    await query.edit_message_text(
        msg,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )


async def select_package(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    parts = query.data.split("_")
    credits = int(parts[1])
    price_usd = float(parts[2])
    price_kes = int(parts[3])
    bonus = int(parts[4])
    
    context.user_data["pending_credits"] = credits + bonus
    context.user_data["pending_amount_usd"] = price_usd
    context.user_data["pending_amount_kes"] = price_kes
    
    lang = db.get_user_language(query.from_user.id) or "en"
    
    total = credits + bonus
    msg = f"""
<b>💳 {get_text('select_payment_method', lang)}</b>
━━━━━━━━━━━━━━━━━━━━
📦 Package: <b>{total} Credits</b>
💵 Amount: <b>${price_usd} USD / KES {price_kes}</b>
━━━━━━━━━━━━━━━━━━━━
"""
    
    keyboard = [
        [InlineKeyboardButton("📱 M-Pesa (Kenya)", callback_data="pay_mpesa")],
        [InlineKeyboardButton("₿ Binance Pay / USDT", callback_data="pay_binance")],
        [InlineKeyboardButton("💳 Credit/Debit Card", callback_data="pay_card")],
        [InlineKeyboardButton("🏦 Bank Transfer", callback_data="pay_bank")],
        [InlineKeyboardButton("🔙 " + get_text("back", lang), callback_data="buy_credits")]
    ]
    
    await query.edit_message_text(
        msg,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )


# ─────────────────────────────────────────────
# M-PESA PAYMENT
# ─────────────────────────────────────────────
async def pay_mpesa(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = db.get_user_language(query.from_user.id) or "en"
    
    amount_kes = context.user_data.get("pending_amount_kes", 0)
    credits = context.user_data.get("pending_credits", 0)
    
    # Generate unique reference
    ref = f"FW{query.from_user.id}{int(datetime.now().timestamp())}"[-10:]
    context.user_data["payment_ref"] = ref
    
    msg = f"""
<b>📱 M-Pesa Payment</b>
━━━━━━━━━━━━━━━━━━━━
<b>💰 Amount: KES {amount_kes}</b>

<b>Method 1 - STK Push (Automatic):</b>
Send your M-Pesa registered phone number and we'll push the payment:

<b>Method 2 - Manual Pay To:</b>
📲 Paybill: <code>247247</code>
🏦 Account: <code>0797XXXXXX</code>

OR

📲 Send Money to: <code>+254 7XX XXX XXX</code>

<b>🔑 Reference: <code>{ref}</code></b>

After payment, send the M-Pesa confirmation code (e.g. <code>QHK12345XY</code>)
━━━━━━━━━━━━━━━━━━━━
💎 You will receive: <b>{credits} Credits</b>
"""
    
    keyboard = [
        [InlineKeyboardButton("📲 Send STK Push to my phone", callback_data="mpesa_stk")],
        [InlineKeyboardButton("✅ I've paid - Enter M-Pesa Code", callback_data="mpesa_confirm")],
        [InlineKeyboardButton("🔙 Back", callback_data="buy_credits")]
    ]
    
    context.user_data["state"] = "awaiting_mpesa_code"
    
    await query.edit_message_text(
        msg,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )


async def verify_mpesa(update: Update, context: ContextTypes.DEFAULT_TYPE, code: str, lang: str):
    """Verify M-Pesa transaction code"""
    user = update.effective_user
    credits = context.user_data.get("pending_credits", 0)
    amount = context.user_data.get("pending_amount_kes", 0)
    
    # Validate M-Pesa code format (10 chars alphanumeric)
    code = code.strip().upper()
    if len(code) < 8 or len(code) > 12:
        await update.message.reply_text(
            "❌ Invalid M-Pesa code format. Please enter the code from SMS (e.g. QHK12345XY)"
        )
        return
    
    # Check if already used
    if db.is_payment_code_used(code):
        await update.message.reply_text("❌ This M-Pesa code has already been used!")
        return
    
    # In production: verify with Safaricom API
    # For now: record pending verification
    verified = payment.verify_mpesa_code(code, amount)
    
    if verified:
        db.add_credits(user.id, credits)
        db.record_payment(user.id, "mpesa", code, amount, credits)
        context.user_data["state"] = ""
        
        await update.message.reply_text(
            f"✅ Payment verified!\n💎 {credits} Credits added to your account!\n\nCurrent balance: {db.get_credits(user.id)} Credits",
            parse_mode="HTML"
        )
    else:
        # Queue for manual verification
        db.queue_payment_verification(user.id, "mpesa", code, amount, credits)
        await update.message.reply_text(
            f"⏳ Payment submitted for verification!\nCode: <code>{code}</code>\n\nYou'll be notified within 5 minutes when credits are added.",
            parse_mode="HTML"
        )
        context.user_data["state"] = ""


# ─────────────────────────────────────────────
# BINANCE PAYMENT
# ─────────────────────────────────────────────
async def pay_binance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = db.get_user_language(query.from_user.id) or "en"
    
    amount_usd = context.user_data.get("pending_amount_usd", 0)
    credits = context.user_data.get("pending_credits", 0)
    
    msg = f"""
<b>₿ Binance Pay / Crypto Payment</b>
━━━━━━━━━━━━━━━━━━━━
<b>💰 Amount: ${amount_usd} USDT/BUSD</b>

<b>Option 1 - Binance Pay ID:</b>
Pay ID: <code>123456789</code>

<b>Option 2 - USDT (TRC20):</b>
Address: <code>TXxxxxxxxxxxxxxxxxxxxxxxxxxxxx</code>

<b>Option 3 - USDT (BEP20):</b>  
Address: <code>0xxxxxxxxxxxxxxxxxxxxxxxxxxx</code>

<b>Option 4 - BTC:</b>
Address: <code>1Axxxxxxxxxxxxxxxxxxxxxxxxxx</code>
Amount: <code>{amount_usd / 43000:.6f} BTC</code>

━━━━━━━━━━━━━━━━━━━━
After sending, share the Transaction ID (TXID)
💎 You will receive: <b>{credits} Credits</b>
"""
    
    keyboard = [
        [InlineKeyboardButton("✅ I've sent - Enter TXID", callback_data="binance_confirm")],
        [InlineKeyboardButton("🔙 Back", callback_data="buy_credits")]
    ]
    
    context.user_data["state"] = "awaiting_binance_txid"
    
    await query.edit_message_text(
        msg,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )


async def verify_binance(update: Update, context: ContextTypes.DEFAULT_TYPE, txid: str, lang: str):
    user = update.effective_user
    credits = context.user_data.get("pending_credits", 0)
    amount = context.user_data.get("pending_amount_usd", 0)
    
    txid = txid.strip()
    
    if db.is_payment_code_used(txid):
        await update.message.reply_text("❌ This transaction ID has already been used!")
        return
    
    db.queue_payment_verification(user.id, "binance", txid, amount, credits)
    context.user_data["state"] = ""
    
    await update.message.reply_text(
        f"⏳ Transaction submitted for verification!\nTXID: <code>{txid[:20]}...</code>\n\nCredits will be added within 10 minutes after blockchain confirmation.",
        parse_mode="HTML"
    )


# ─────────────────────────────────────────────
# MY ACCOUNT
# ─────────────────────────────────────────────
async def my_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    lang = db.get_user_language(user.id) or "en"
    
    user_data = db.get_user(user.id)
    credits = db.get_credits(user.id)
    purchases = db.get_user_purchases(user.id)
    total_spent = db.get_total_spent(user.id)
    
    msg = f"""
<b>👤 {get_text('my_account', lang)}</b>
━━━━━━━━━━━━━━━━━━━━
📛 Name: <b>{user.full_name}</b>
🆔 ID: <code>{user.id}</code>
👤 Username: @{user.username or 'N/A'}
━━━━━━━━━━━━━━━━━━━━
💎 Credits: <b>{credits}</b>
🛒 Total Purchases: <b>{len(purchases)}</b>
💰 Total Spent: <b>{total_spent} Credits</b>
📅 Member Since: <b>{user_data.get('created_at', 'N/A')}</b>
━━━━━━━━━━━━━━━━━━━━
"""
    
    keyboard = [
        [InlineKeyboardButton("📋 " + get_text("purchase_history", lang), callback_data="purchase_history")],
        [InlineKeyboardButton("💳 " + get_text("buy_credits", lang), callback_data="buy_credits")],
        [InlineKeyboardButton("🔙 " + get_text("back", lang), callback_data="main_menu")]
    ]
    
    await query.edit_message_text(
        msg,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )


async def purchase_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user = query.from_user
    lang = db.get_user_language(user.id) or "en"
    purchases = db.get_user_purchases(user.id)
    
    if not purchases:
        msg = f"<b>📋 {get_text('purchase_history', lang)}</b>\n\n{get_text('no_purchases', lang)}"
    else:
        msg = f"<b>📋 {get_text('purchase_history', lang)}</b>\n━━━━━━━━━━━━━━━━━━━━\n"
        for p in purchases[-10:]:
            msg += f"📦 {p['product_name']} - {p['price']} CR - {p['date']}\n"
    
    keyboard = [[InlineKeyboardButton("🔙 " + get_text("back", lang), callback_data="my_account")]]
    
    await query.edit_message_text(
        msg,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )


# ─────────────────────────────────────────────
# LANGUAGE SELECTION
# ─────────────────────────────────────────────
async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    languages = [
        ("🇬🇧 English", "en"),
        ("🇹🇿 Kiswahili", "sw"),
        ("🇫🇷 Français", "fr"),
        ("🇪🇸 Español", "es"),
        ("🇵🇹 Português", "pt"),
        ("🇦🇷 العربية", "ar"),
        ("🇮🇳 Hindi", "hi"),
        ("🇨🇳 中文", "zh"),
    ]
    
    keyboard = []
    for name, code in languages:
        keyboard.append([InlineKeyboardButton(name, callback_data=f"setlang_{code}")])
    
    await query.edit_message_text(
        "<b>🌍 Select Your Language / Chagua Lugha Yako</b>",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )


async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    lang = query.data.split("_")[1]
    db.update_user_language(query.from_user.id, lang)
    
    await start(update, context)


# ─────────────────────────────────────────────
# ADMIN COMMANDS
# ─────────────────────────────────────────────
async def admin_add_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in ADMIN_IDS:
        return
    
    # /addproduct name|category|price|description|download_link|version
    args = " ".join(context.args)
    parts = args.split("|")
    
    if len(parts) < 5:
        await update.message.reply_text(
            "Usage: /addproduct name|category|price|description|download_link|version\n"
            "Categories: Firmware, Solution, Source Code, Tools\n"
            "Price: 0 for free"
        )
        return
    
    product_id = db.add_product(
        name=parts[0].strip(),
        category=parts[1].strip(),
        price=int(parts[2].strip()),
        description=parts[3].strip(),
        download_link=parts[4].strip(),
        version=parts[5].strip() if len(parts) > 5 else "1.0"
    )
    
    await update.message.reply_text(f"✅ Product added! ID: {product_id}\n📦 {parts[0]}")


async def admin_approve_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in ADMIN_IDS:
        return
    
    # /approve user_id credits
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /approve user_id credits")
        return
    
    target_id = int(context.args[0])
    credits = int(context.args[1])
    
    db.add_credits(target_id, credits)
    
    await update.message.reply_text(f"✅ Added {credits} credits to user {target_id}")
    
    # Notify user
    try:
        await context.bot.send_message(
            target_id,
            f"✅ Payment approved!\n💎 {credits} Credits added to your account!"
        )
    except Exception:
        pass


async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id not in ADMIN_IDS:
        return
    
    stats = db.get_admin_stats()
    msg = f"""
<b>📊 Bot Statistics</b>
━━━━━━━━━━━━━━━━━━━━
👥 Total Users: {stats['total_users']}
🛒 Total Sales: {stats['total_sales']}
💰 Total Revenue: {stats['total_revenue']} Credits
📦 Total Products: {stats['total_products']}
⏳ Pending Payments: {stats['pending_payments']}
━━━━━━━━━━━━━━━━━━━━
📅 Today's Sales: {stats['today_sales']}
👤 New Users Today: {stats['new_users_today']}
"""
    await update.message.reply_text(msg, parse_mode="HTML")


# ─────────────────────────────────────────────
# SUPPORT
# ─────────────────────────────────────────────
async def show_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = db.get_user_language(query.from_user.id) or "en"
    
    msg = f"""
<b>📞 {get_text('support', lang)}</b>
━━━━━━━━━━━━━━━━━━━━
📱 Telegram: @YourSupportUsername
📧 Email: support@yourstore.com
⏰ Hours: 24/7

{get_text('support_note', lang)}
━━━━━━━━━━━━━━━━━━━━
"""
    keyboard = [[InlineKeyboardButton("🔙 " + get_text("back", lang), callback_data="main_menu")]]
    
    await query.edit_message_text(
        msg,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML"
    )


# ─────────────────────────────────────────────
# CALLBACK ROUTER
# ─────────────────────────────────────────────
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    
    routes = {
        "main_menu": start,
        "search": handle_search,
        "categories": show_categories,
        "buy_credits": buy_credits_menu,
        "my_account": my_account,
        "change_language": change_language,
        "support": show_support,
        "purchase_history": purchase_history,
        "pay_mpesa": pay_mpesa,
        "pay_binance": pay_binance,
        "mpesa_confirm": lambda u, c: mpesa_confirm_prompt(u, c),
        "binance_confirm": lambda u, c: binance_confirm_prompt(u, c),
    }
    
    if data in routes:
        await routes[data](update, context)
    elif data.startswith("product_"):
        await show_product(update, context)
    elif data.startswith("category_"):
        await show_category_products(update, context)
    elif data.startswith("buy_"):
        await buy_product(update, context)
    elif data.startswith("download_"):
        await download_free(update, context)
    elif data.startswith("pkg_"):
        await select_package(update, context)
    elif data.startswith("setlang_"):
        await set_language(update, context)


async def mpesa_confirm_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    lang = db.get_user_language(query.from_user.id) or "en"
    context.user_data["state"] = "awaiting_mpesa_code"
    await query.edit_message_text(
        "📲 Please type your M-Pesa confirmation code (e.g. <code>QHK12345XY</code>):",
        parse_mode="HTML"
    )


async def binance_confirm_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    context.user_data["state"] = "awaiting_binance_txid"
    await query.edit_message_text(
        "🔗 Please type your Transaction ID (TXID):"
    )


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("addproduct", admin_add_product))
    app.add_handler(CommandHandler("approve", admin_approve_payment))
    app.add_handler(CommandHandler("stats", admin_stats))
    
    # Callbacks
    app.add_handler(CallbackQueryHandler(callback_handler))
    
    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, process_message))
    
    logger.info("🤖 FirmwareShop Bot Starting...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
