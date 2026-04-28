# 🤖 FirmwareShop Telegram Bot - Setup Guide

## 📁 Muundo wa Faili / File Structure

```
firmware_bot/
├── bot.py              ← Main bot (faili kuu)
├── database.py         ← Database (hifadhi ya data)
├── language_detector.py ← Lugha nyingi (multi-language)
├── payment_handler.py  ← Malipo (M-Pesa, Binance, etc)
├── config.py           ← Mipangilio (settings)
├── .env.example        ← Template ya environment variables
├── requirements.txt    ← Python packages zinazohitajika
└── README.md           ← Maelekezo haya
```

---

## 🚀 HATUA ZA KUANZISHA / Setup Steps

### HATUA 1: Pata Bot Token kutoka BotFather

1. Fungua Telegram → tafuta **@BotFather**
2. Tuma `/newbot`
3. Weka jina la bot yako (mfano: `FirmwareShop`)
4. Weka username (lazima iishie na `bot`, mfano: `FirmwareShopBot`)
5. BotFather atakupa **TOKEN** kama hii:
   ```
   7123456789:AAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
6. Hifadhi token hiyo — utaihitaji!

---

### HATUA 2: Pata Telegram User ID yako (Admin)

1. Tuma ujumbe kwa **@userinfobot**
2. Itakuambia ID yako (mfano: `123456789`)
3. Hiyo ndiyo `ADMIN_IDS` yako

---

### HATUA 3: Weka Python na dependencies

```bash
# Hakikisha Python 3.10+ ipo
python3 --version

# Unda virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# au
venv\Scripts\activate     # Windows

# Sakinisha packages
pip install -r requirements.txt
```

---

### HATUA 4: Weka Environment Variables

```bash
# Nakili faili la .env.example
cp .env.example .env

# Hariri .env na maelezo yako
nano .env   # au notepad .env (Windows)
```

**Weka thamani hizi katika .env:**
```env
BOT_TOKEN=7123456789:AAxxxxxxxxxxxxxxxxxx
ADMIN_IDS=123456789
MPESA_TILL_NUMBER=5123456
MPESA_ACCOUNT_NAME=Jina Lako
```

---

### HATUA 5: Anzisha Bot

```bash
python bot.py
```

Utaona:
```
INFO - 🤖 FirmwareShop Bot Starting...
```

Bot inaanza kufanya kazi! 🎉

---

## 💳 MIPANGILIO YA MALIPO / Payment Setup

### M-Pesa (Kenya)

**Option A - Manual (Rahisi kuanza):**
- Weka namba yako ya M-Pesa/Till kwenye `.env`
- Wateja watakulipa, kutuma code, wewe uthibitishe manually
- Tumia: `/approve USER_ID CREDITS` kwenye Telegram

**Option B - Automatic (Safaricom Daraja API):**
1. Nenda: https://developer.safaricom.co.ke
2. Fungua akaunti ya developer
3. Unda app → pata Consumer Key na Consumer Secret
4. Omba Lipa Na M-Pesa paybill kwa production
5. Weka credentials kwenye `.env`

### Binance Pay

1. Nenda: https://merchant.binance.com
2. Fungua Merchant account
3. Pata API Key na Secret
4. Weka Pay ID yako

### Crypto Wallets (USDT, BTC)

- Fungua wallet yako (Trust Wallet, Metamask, Binance, nk)
- Nakili wallet addresses
- Weka kwenye `.env`

---

## 📦 KUONGEZA BIDHAA / Adding Products

Tumia command hii kwenye Telegram (kama Admin):

```
/addproduct Samsung A52|Firmware|300|Samsung A52 SM-A525F Official Firmware|https://yourlink.com/file.zip|v5.0
```

**Format:** `name|category|price|description|download_link|version`

**Categories zinazopatikana:**
- `Firmware`
- `Solution`
- `Source Code`
- `Tools`
- `Other`

**Bei (Price):**
- `0` = Bure/Free
- `300` = 300 Credits

---

## 👑 AMRI ZA ADMIN / Admin Commands

| Command | Maelezo |
|---------|---------|
| `/addproduct name\|category\|price\|desc\|link\|version` | Ongeza bidhaa |
| `/approve USER_ID CREDITS` | Ongeza credits kwa mtumiaji |
| `/stats` | Ona takwimu za bot |

---

## 🛡️ KUTHIBITISHA MALIPO MANUALLY

Wakati mtumiaji anatuma M-Pesa code au Crypto TXID:

1. Angalia database ya `payments` — column `status = 'pending'`
2. Thibitisha kwenye M-Pesa au Blockchain explorer
3. Thibitishiwa → tuma kwenye Telegram:
   ```
   /approve 123456789 500
   ```
4. Mtumiaji atapata notification ya credits

---

## 🌍 LUGHA ZINAZOTUMIKA / Supported Languages

Bot inatambua lugha ya mtumiaji automatically:

| Lugha | Code |
|-------|------|
| English | `en` |
| Kiswahili | `sw` |
| Français | `fr` |
| Español | `es` |
| Português | `pt` |
| العربية | `ar` |
| Hindi | `hi` |
| 中文 | `zh` |

---

## 🖥️ DEPLOYMENT (Kuendesha 24/7)

### Option A: VPS (Hetzner, DigitalOcean, nk)

```bash
# Sakinisha screen
sudo apt install screen

# Anza bot kwenye background
screen -S firmware_bot
python bot.py

# Ondoka bila kusimamisha: Ctrl+A then D
```

### Option B: Systemd Service (Inashauriwa)

```bash
# Unda service file
sudo nano /etc/systemd/system/firmwarebot.service
```

Weka hii:
```ini
[Unit]
Description=FirmwareShop Telegram Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/firmware_bot
ExecStart=/home/ubuntu/firmware_bot/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Activate
sudo systemctl enable firmwarebot
sudo systemctl start firmwarebot
sudo systemctl status firmwarebot
```

### Option C: Railway.app (Bure kuanza)

1. Nenda: https://railway.app
2. Fungua akaunti na GitHub
3. Create New Project → Deploy from GitHub
4. Weka environment variables kwenye dashboard
5. Deploy! 🚀

---

## ⚠️ MUHIMU / Important Notes

1. **Usishiriki** BOT_TOKEN wako na mtu yeyote
2. **Backup** database (`firmware_shop.db`) kila siku
3. Thibitisha malipo yote kabla ya kutoa bidhaa
4. Weka download links zinazofanya kazi kwenye server salama
5. Thibitisha kwamba download links zinafanya kazi kabla ya kuongeza bidhaa

---

## 🆘 Msaada / Help

Kwa matatizo yoyote:
- Angalia logs: `tail -f bot.log`
- Telegram Docs: https://core.telegram.org/bots
- python-telegram-bot docs: https://python-telegram-bot.org
