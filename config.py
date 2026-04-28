"""
Configuration - FirmwareShop Bot
Copy this to config.py and fill in your real credentials
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ─── TELEGRAM ───────────────────────────────
BOT_TOKEN = os.getenv("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Your Telegram user IDs (admins)
ADMIN_IDS = [
    int(x) for x in os.getenv("ADMIN_IDS", "123456789").split(",")
]

# ─── DATABASE ───────────────────────────────
DB_PATH = os.getenv("DB_PATH", "firmware_shop.db")

# ─── M-PESA (Safaricom Daraja API) ──────────
# Get from: https://developer.safaricom.co.ke
MPESA_CONSUMER_KEY = os.getenv("MPESA_CONSUMER_KEY", "")
MPESA_CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET", "")
MPESA_SHORTCODE = os.getenv("MPESA_SHORTCODE", "174379")  # Test shortcode
MPESA_PASSKEY = os.getenv("MPESA_PASSKEY", "")
MPESA_CALLBACK_URL = os.getenv("MPESA_CALLBACK_URL", "https://yourdomain.com/mpesa/callback")

# Your M-Pesa Till/Paybill for manual payments
MPESA_TILL_NUMBER = os.getenv("MPESA_TILL_NUMBER", "YOUR_TILL_NUMBER")
MPESA_PAYBILL = os.getenv("MPESA_PAYBILL", "YOUR_PAYBILL")
MPESA_ACCOUNT_NAME = os.getenv("MPESA_ACCOUNT_NAME", "YOUR_NAME")

# ─── BINANCE PAY ─────────────────────────────
# Get from: https://merchant.binance.com
BINANCE_API_KEY = os.getenv("BINANCE_API_KEY", "")
BINANCE_SECRET_KEY = os.getenv("BINANCE_SECRET_KEY", "")

# Your crypto wallet addresses
USDT_TRC20_ADDRESS = os.getenv("USDT_TRC20_ADDRESS", "YOUR_TRC20_WALLET")
USDT_BEP20_ADDRESS = os.getenv("USDT_BEP20_ADDRESS", "YOUR_BEP20_WALLET")
BTC_ADDRESS = os.getenv("BTC_ADDRESS", "YOUR_BTC_WALLET")
BINANCE_PAY_ID = os.getenv("BINANCE_PAY_ID", "YOUR_BINANCE_PAY_ID")

# ─── STORE SETTINGS ─────────────────────────
STORE_NAME = "FirmwareShop"
STORE_SUPPORT = "@YourSupportUsername"
STORE_EMAIL = "support@yourstore.com"

# New user bonus credits
NEW_USER_BONUS_CREDITS = 50

# Credits exchange rate (1 Credit = X USD)
CREDIT_VALUE_USD = 0.01
