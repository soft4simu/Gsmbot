"""
Language Detection & Multi-language Text Handler
Supports: English, Swahili, French, Spanish, Portuguese, Arabic, Hindi, Chinese
"""

# Simple keyword-based language detection
LANGUAGE_KEYWORDS = {
    "sw": ["habari", "karibu", "asante", "nini", "nina", "nataka", "firmware", "ninunue", "pesa", "bei"],
    "fr": ["bonjour", "merci", "oui", "non", "voulez", "acheter", "prix", "logiciel"],
    "es": ["hola", "gracias", "comprar", "precio", "quiero", "necesito"],
    "pt": ["olá", "obrigado", "comprar", "preço", "quero"],
    "ar": ["مرحبا", "شكرا", "اشتري", "سعر", "أريد"],
    "hi": ["नमस्ते", "धन्यवाद", "खरीदना", "कीमत"],
    "zh": ["你好", "谢谢", "购买", "价格"],
}


def detect_language(text: str) -> str:
    """Detect language from message text"""
    text_lower = text.lower()
    
    for lang, keywords in LANGUAGE_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                return lang
    
    return None  # Default: don't change


# ─────────────────────────────────────────────
# TRANSLATIONS
# ─────────────────────────────────────────────
TEXTS = {
    "welcome": {
        "en": """🤖 <b>Welcome to FirmwareShop!</b> {new_badge}

Hello <b>{name}</b>! 👋
Your digital store for Firmwares, Solutions & Source Codes.

💎 Your Credits: <b>{credits}</b>

Use the menu below to get started:""",

        "sw": """🤖 <b>Karibu FirmwareShop!</b> {new_badge}

Habari <b>{name}</b>! 👋
Duka lako la Firmware, Solutions & Source Codes.

💎 Credits Zako: <b>{credits}</b>

Tumia menyu hapa chini kuanza:""",

        "fr": """🤖 <b>Bienvenue sur FirmwareShop!</b> {new_badge}

Bonjour <b>{name}</b>! 👋
Votre boutique de Firmware, Solutions & Codes Source.

💎 Vos Crédits: <b>{credits}</b>

Utilisez le menu ci-dessous pour commencer:""",

        "es": """🤖 <b>¡Bienvenido a FirmwareShop!</b> {new_badge}

Hola <b>{name}</b>! 👋
Tu tienda de Firmware, Soluciones y Código Fuente.

💎 Tus Créditos: <b>{credits}</b>

Usa el menú de abajo para empezar:""",

        "pt": """🤖 <b>Bem-vindo ao FirmwareShop!</b> {new_badge}

Olá <b>{name}</b>! 👋
Sua loja de Firmware, Soluções e Código Fonte.

💎 Seus Créditos: <b>{credits}</b>

Use o menu abaixo para começar:""",

        "ar": """🤖 <b>مرحباً بك في FirmwareShop!</b> {new_badge}

مرحبا <b>{name}</b>! 👋
متجرك للبرامج الثابتة والحلول وأكواد المصدر.

💎 رصيدك: <b>{credits}</b>

استخدم القائمة أدناه للبدء:""",

        "hi": """🤖 <b>FirmwareShop में आपका स्वागत है!</b> {new_badge}

नमस्ते <b>{name}</b>! 👋
फ़र्मवेयर, समाधान और सोर्स कोड के लिए आपकी दुकान।

💎 आपके क्रेडिट: <b>{credits}</b>

शुरू करने के लिए नीचे मेनू का उपयोग करें:""",

        "zh": """🤖 <b>欢迎来到 FirmwareShop!</b> {new_badge}

你好 <b>{name}</b>! 👋
您的固件、解决方案和源代码商店。

💎 您的积分: <b>{credits}</b>

使用下面的菜单开始:""",
    },

    "new_user_bonus": {
        "en": "🎁 You received 50 FREE welcome credits!",
        "sw": "🎁 Umepewa credits 50 za bure za kukaribisha!",
        "fr": "🎁 Vous avez reçu 50 crédits de bienvenue GRATUITS!",
        "es": "🎁 ¡Recibiste 50 créditos de bienvenida GRATIS!",
        "pt": "🎁 Você recebeu 50 créditos de boas-vindas GRÁTIS!",
        "ar": "🎁 حصلت على 50 رصيد ترحيب مجانًا!",
        "hi": "🎁 आपको 50 मुफ़्त वेलकम क्रेडिट मिले!",
        "zh": "🎁 您获得了50个免费欢迎积分！",
    },

    "search": {
        "en": "Search", "sw": "Tafuta", "fr": "Rechercher",
        "es": "Buscar", "pt": "Pesquisar", "ar": "بحث",
        "hi": "खोज", "zh": "搜索",
    },

    "categories": {
        "en": "Categories", "sw": "Makundi", "fr": "Catégories",
        "es": "Categorías", "pt": "Categorias", "ar": "الفئات",
        "hi": "श्रेणियाँ", "zh": "分类",
    },

    "buy_credits": {
        "en": "Buy Credits", "sw": "Nunua Credits", "fr": "Acheter des Crédits",
        "es": "Comprar Créditos", "pt": "Comprar Créditos", "ar": "شراء رصيد",
        "hi": "क्रेडिट खरीदें", "zh": "购买积分",
    },

    "my_account": {
        "en": "My Account", "sw": "Akaunti Yangu", "fr": "Mon Compte",
        "es": "Mi Cuenta", "pt": "Minha Conta", "ar": "حسابي",
        "hi": "मेरा खाता", "zh": "我的账户",
    },

    "change_language": {
        "en": "Language", "sw": "Lugha", "fr": "Langue",
        "es": "Idioma", "pt": "Idioma", "ar": "اللغة",
        "hi": "भाषा", "zh": "语言",
    },

    "support": {
        "en": "Support", "sw": "Msaada", "fr": "Support",
        "es": "Soporte", "pt": "Suporte", "ar": "الدعم",
        "hi": "सहायता", "zh": "支持",
    },

    "back": {
        "en": "Back", "sw": "Rudi", "fr": "Retour",
        "es": "Volver", "pt": "Voltar", "ar": "رجوع",
        "hi": "वापस", "zh": "返回",
    },

    "home": {
        "en": "Home", "sw": "Nyumbani", "fr": "Accueil",
        "es": "Inicio", "pt": "Início", "ar": "الرئيسية",
        "hi": "होम", "zh": "首页",
    },

    "search_prompt": {
        "en": "🔍 <b>Search Products</b>\n\nType the name of firmware, solution, or source code you're looking for:",
        "sw": "🔍 <b>Tafuta Bidhaa</b>\n\nAndika jina la firmware, solution, au source code unayotafuta:",
        "fr": "🔍 <b>Rechercher des Produits</b>\n\nTapez le nom du firmware, solution ou code source que vous cherchez:",
        "es": "🔍 <b>Buscar Productos</b>\n\nEscribe el nombre del firmware, solución o código fuente que buscas:",
        "pt": "🔍 <b>Pesquisar Produtos</b>\n\nDigite o nome do firmware, solução ou código fonte que você procura:",
        "ar": "🔍 <b>البحث عن المنتجات</b>\n\nاكتب اسم البرنامج الثابت أو الحل أو كود المصدر الذي تبحث عنه:",
        "hi": "🔍 <b>उत्पाद खोजें</b>\n\nआप जो फ़र्मवेयर, सॉल्यूशन या सोर्स कोड खोज रहे हैं उसका नाम टाइप करें:",
        "zh": "🔍 <b>搜索产品</b>\n\n输入您要查找的固件、解决方案或源代码名称:",
    },

    "not_found": {
        "en": "❌ <b>No results found for:</b> <i>{query}</i>\n\nTry different keywords or browse categories.",
        "sw": "❌ <b>Hakuna matokeo kwa:</b> <i>{query}</i>\n\nJaribu maneno tofauti au angalia makundi.",
        "fr": "❌ <b>Aucun résultat pour:</b> <i>{query}</i>\n\nEssayez d'autres mots-clés ou parcourez les catégories.",
        "es": "❌ <b>Sin resultados para:</b> <i>{query}</i>\n\nIntenta con otras palabras clave o navega por categorías.",
        "pt": "❌ <b>Nenhum resultado para:</b> <i>{query}</i>\n\nTente outras palavras-chave ou navegue pelas categorias.",
        "ar": "❌ <b>لا توجد نتائج لـ:</b> <i>{query}</i>\n\nجرب كلمات مختلفة أو تصفح الفئات.",
        "hi": "❌ <b>कोई परिणाम नहीं मिला:</b> <i>{query}</i>\n\nअलग कीवर्ड आज़माएं या श्रेणियाँ देखें।",
        "zh": "❌ <b>未找到结果:</b> <i>{query}</i>\n\n尝试其他关键词或浏览分类。",
    },

    "not_found_suggestions": {
        "en": "❓ <b>'{query}' not found exactly.</b>\n\nDid you mean one of these?",
        "sw": "❓ <b>'{query}' haipatikani haswa.</b>\n\nUnakusudia moja ya hizi?",
        "fr": "❓ <b>'{query}' introuvable exactement.</b>\n\nVouliez-vous dire?",
        "es": "❓ <b>'{query}' no encontrado exactamente.</b>\n\n¿Quisiste decir uno de estos?",
        "pt": "❓ <b>'{query}' não encontrado exatamente.</b>\n\nQuis dizer um destes?",
        "ar": "❓ <b>'{query}' غير موجود بالضبط.</b>\n\nهل تقصد أحد هؤلاء؟",
        "hi": "❓ <b>'{query}' बिल्कुल नहीं मिला।</b>\n\nक्या आपका मतलब इनमें से कोई था?",
        "zh": "❓ <b>未精确找到'{query}'。</b>\n\n您是否是指这些之一？",
    },

    "search_results": {
        "en": "🔍 <b>Found {count} results for:</b> <i>{query}</i>",
        "sw": "🔍 <b>Matokeo {count} kwa:</b> <i>{query}</i>",
        "fr": "🔍 <b>{count} résultats pour:</b> <i>{query}</i>",
        "es": "🔍 <b>{count} resultados para:</b> <i>{query}</i>",
        "pt": "🔍 <b>{count} resultados para:</b> <i>{query}</i>",
        "ar": "🔍 <b>وجدنا {count} نتيجة لـ:</b> <i>{query}</i>",
        "hi": "🔍 <b>{count} परिणाम मिले:</b> <i>{query}</i>",
        "zh": "🔍 <b>找到 {count} 个结果:</b> <i>{query}</i>",
    },

    "free": {
        "en": "FREE", "sw": "BURE", "fr": "GRATUIT",
        "es": "GRATIS", "pt": "GRÁTIS", "ar": "مجاني",
        "hi": "मुफ़्त", "zh": "免费",
    },

    "price": {
        "en": "Price", "sw": "Bei", "fr": "Prix",
        "es": "Precio", "pt": "Preço", "ar": "السعر",
        "hi": "कीमत", "zh": "价格",
    },

    "category": {
        "en": "Category", "sw": "Kundi", "fr": "Catégorie",
        "es": "Categoría", "pt": "Categoria", "ar": "الفئة",
        "hi": "श्रेणी", "zh": "分类",
    },

    "description": {
        "en": "Description", "sw": "Maelezo", "fr": "Description",
        "es": "Descripción", "pt": "Descrição", "ar": "الوصف",
        "hi": "विवरण", "zh": "描述",
    },

    "version": {
        "en": "Version", "sw": "Toleo", "fr": "Version",
        "es": "Versión", "pt": "Versão", "ar": "الإصدار",
        "hi": "संस्करण", "zh": "版本",
    },

    "updated": {
        "en": "Updated", "sw": "Imesasishwa", "fr": "Mis à jour",
        "es": "Actualizado", "pt": "Atualizado", "ar": "تحديث",
        "hi": "अपडेट", "zh": "更新",
    },

    "your_credits": {
        "en": "Your Credits", "sw": "Credits Zako", "fr": "Vos Crédits",
        "es": "Tus Créditos", "pt": "Seus Créditos", "ar": "رصيدك",
        "hi": "आपके क्रेडिट", "zh": "您的积分",
    },

    "download_free": {
        "en": "Download Free", "sw": "Pakua Bure", "fr": "Télécharger Gratuitement",
        "es": "Descargar Gratis", "pt": "Baixar Grátis", "ar": "تحميل مجاني",
        "hi": "मुफ़्त डाउनलोड", "zh": "免费下载",
    },

    "buy_with_credits": {
        "en": "Buy with Credits", "sw": "Nunua kwa Credits", "fr": "Acheter avec Crédits",
        "es": "Comprar con Créditos", "pt": "Comprar com Créditos", "ar": "شراء بالرصيد",
        "hi": "क्रेडिट से खरीदें", "zh": "用积分购买",
    },

    "need_more_credits": {
        "en": "Not enough credits", "sw": "Credits hazitoshi", "fr": "Crédits insuffisants",
        "es": "Créditos insuficientes", "pt": "Créditos insuficientes", "ar": "رصيد غير كافٍ",
        "hi": "पर्याप्त क्रेडिट नहीं", "zh": "积分不足",
    },

    "purchase_success": {
        "en": "Purchase Successful!", "sw": "Ununuzi Umefanikiwa!",
        "fr": "Achat Réussi!", "es": "¡Compra Exitosa!",
        "pt": "Compra Bem-Sucedida!", "ar": "تم الشراء بنجاح!",
        "hi": "खरीदारी सफल!", "zh": "购买成功！",
    },

    "download_link": {
        "en": "Download Link", "sw": "Kiungo cha Kupakua", "fr": "Lien de Téléchargement",
        "es": "Enlace de Descarga", "pt": "Link de Download", "ar": "رابط التحميل",
        "hi": "डाउनलोड लिंक", "zh": "下载链接",
    },

    "license_key": {
        "en": "License Key", "sw": "Ufunguo wa Leseni", "fr": "Clé de Licence",
        "es": "Clave de Licencia", "pt": "Chave de Licença", "ar": "مفتاح الترخيص",
        "hi": "लाइसेंस की", "zh": "许可证密钥",
    },

    "instructions": {
        "en": "Instructions", "sw": "Maelekezo", "fr": "Instructions",
        "es": "Instrucciones", "pt": "Instruções", "ar": "التعليمات",
        "hi": "निर्देश", "zh": "说明",
    },

    "do_not_share": {
        "en": "Do NOT share this link/key with others.", 
        "sw": "USISHIRIKI kiungo/ufunguo huu na wengine.",
        "fr": "Ne partagez PAS ce lien/clé avec d'autres.",
        "es": "NO compartas este enlace/clave con otros.",
        "pt": "NÃO compartilhe este link/chave com outros.",
        "ar": "لا تشارك هذا الرابط/المفتاح مع الآخرين.",
        "hi": "इस लिंक/की को दूसरों के साथ साझा न करें।",
        "zh": "请勿与他人分享此链接/密钥。",
    },

    "select_category": {
        "en": "Select a Category", "sw": "Chagua Kundi", "fr": "Sélectionner une Catégorie",
        "es": "Seleccionar Categoría", "pt": "Selecionar Categoria", "ar": "اختر فئة",
        "hi": "श्रेणी चुनें", "zh": "选择分类",
    },

    "items": {
        "en": "items", "sw": "bidhaa", "fr": "articles",
        "es": "artículos", "pt": "itens", "ar": "عناصر",
        "hi": "आइटम", "zh": "项目",
    },

    "no_products_in_category": {
        "en": "No products in this category yet.", "sw": "Hakuna bidhaa katika kundi hili bado.",
        "fr": "Aucun produit dans cette catégorie pour l'instant.", "es": "Sin productos en esta categoría todavía.",
        "pt": "Nenhum produto nesta categoria ainda.", "ar": "لا توجد منتجات في هذه الفئة بعد.",
        "hi": "इस श्रेणी में अभी कोई उत्पाद नहीं।", "zh": "此分类暂无产品。",
    },

    "select_payment_method": {
        "en": "Select Payment Method", "sw": "Chagua Njia ya Malipo",
        "fr": "Sélectionner la Méthode de Paiement", "es": "Seleccionar Método de Pago",
        "pt": "Selecionar Método de Pagamento", "ar": "اختر طريقة الدفع",
        "hi": "भुगतान विधि चुनें", "zh": "选择支付方式",
    },

    "insufficient_credits": {
        "en": "❌ Insufficient credits. Please buy more credits first.",
        "sw": "❌ Credits hazitoshi. Tafadhali nunua credits zaidi kwanza.",
        "fr": "❌ Crédits insuffisants. Veuillez d'abord acheter plus de crédits.",
        "es": "❌ Créditos insuficientes. Por favor compra más créditos primero.",
        "pt": "❌ Créditos insuficientes. Por favor, compre mais créditos primeiro.",
        "ar": "❌ الرصيد غير كافٍ. يرجى شراء المزيد من الرصيد أولاً.",
        "hi": "❌ पर्याप्त क्रेडिट नहीं। पहले अधिक क्रेडिट खरीदें।",
        "zh": "❌ 积分不足。请先购买更多积分。",
    },

    "product_not_found": {
        "en": "❌ Product not found.", "sw": "❌ Bidhaa haipatikani.",
        "fr": "❌ Produit non trouvé.", "es": "❌ Producto no encontrado.",
        "pt": "❌ Produto não encontrado.", "ar": "❌ المنتج غير موجود.",
        "hi": "❌ उत्पाद नहीं मिला।", "zh": "❌ 未找到产品。",
    },

    "purchase_history": {
        "en": "Purchase History", "sw": "Historia ya Manunuzi",
        "fr": "Historique d'Achats", "es": "Historial de Compras",
        "pt": "Histórico de Compras", "ar": "سجل المشتريات",
        "hi": "खरीदारी इतिहास", "zh": "购买历史",
    },

    "no_purchases": {
        "en": "You haven't made any purchases yet.", "sw": "Bado hujafanya ununuzi wowote.",
        "fr": "Vous n'avez pas encore effectué d'achats.", "es": "No has realizado ninguna compra todavía.",
        "pt": "Você ainda não fez nenhuma compra.", "ar": "لم تقم بأي عمليات شراء بعد.",
        "hi": "आपने अभी तक कोई खरीदारी नहीं की है।", "zh": "您尚未进行任何购买。",
    },

    "support_note": {
        "en": "Our team responds within 30 minutes during business hours.",
        "sw": "Timu yetu inajibu ndani ya dakika 30 wakati wa kazi.",
        "fr": "Notre équipe répond dans les 30 minutes pendant les heures de bureau.",
        "es": "Nuestro equipo responde en 30 minutos durante el horario comercial.",
        "pt": "Nossa equipe responde em 30 minutos durante o horário comercial.",
        "ar": "يستجيب فريقنا في غضون 30 دقيقة خلال ساعات العمل.",
        "hi": "हमारी टीम व्यापार समय के दौरान 30 मिनट में जवाब देती है।",
        "zh": "我们的团队在工作时间内30分钟内回复。",
    },
}


def get_text(key: str, lang: str = "en") -> str:
    """Get translated text for a key and language"""
    if key not in TEXTS:
        return key
    
    texts = TEXTS[key]
    
    # Try exact language
    if lang in texts:
        return texts[lang]
    
    # Fallback to English
    return texts.get("en", key)
