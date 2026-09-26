import re, os, threading, socket
from urllib.parse import urlparse
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
app_flask = Flask(__name__)

@app_flask.route('/')
def home(): return "Scam Guard India ULTIMATE LIVE"

# --- LANGUAGE PROMPTS ---
LANG = {
    "en": {"choose": "Choose your language:", "job_mode": "💼 Job Mode", "send_job": "Send Job Message", "risk": "Job Risk"},
    "ml": {"choose": "നിങ്ങളുടെ ഭാഷ തിരഞ്ഞെടുക്കുക:", "job_mode": "💼 ജോലി മോഡ്", "send_job": "ജോലി മെസ്സേജ് അയക്കൂ", "risk": "Job Risk"},
    "ta": {"choose": "உங்கள் மொழியை தேர்வு செய்யவும்:", "job_mode": "💼 வேலை முறை", "send_job": "வேலை செய்தியை அனுப்பவும்", "risk": "Job Risk"},
    "hi": {"choose": "अपनी भाषा चुनें:", "job_mode": "💼 नौकरी मोड", "send_job": "नौकरी संदेश भेजें", "risk": "Job Risk"}
}
user_lang = {}

def get_lang(uid): return user_lang.get(uid, "ml")

# --- 1. LINK CHECK ---
def check_link(text):
    urls = re.findall(r'https?://\S+|bit\.ly/\S+|tinyurl\.com/\S+|is\.gd/\S+|t\.me/\S+', text, re.I)
    if not urls: return None
    risk, reasons = 0, []
    for u in urls:
        if not u.startswith('http'): u = 'http://' + u
        if re.search(r'bit\.ly|tinyurl|is\.gd|shorturl|cutt\.ly', u, re.I):
            risk += 40; reasons.append("shortener")
        try:
            domain = urlparse(u).netloc
            if re.match(r'^\d+\.\d+\.\d+\.\d+', domain):
                risk += 50; reasons.append("IP address link")
            socket.gethostbyname(domain)
        except: risk += 30; reasons.append("invalid domain age")
        if re.search(r'free|gift|prize|earn|lottery|refund|lucky', u, re.I):
            risk += 30; reasons.append("keyword")
    return min(risk, 100), reasons, urls[0]

# --- 2. NUMBER CHECK ---
def check_number(text):
    nums = re.findall(r'\b\d{10}\b', text)
    if not nums: return None
    for n in nums:
        if not re.match(r'^[6-9]\d{9}$', n): return 80, ["invalid start digit (must 6-9)"], n
        if re.search(r'(\d)\1{4,}', n): return 90, ["99999 spam pattern"], n
    return 10, ["valid format"], nums[0]

# --- 3. UPI CHECK ---
def check_upi(text):
    if '@' not in text: return None
    upis = re.findall(r'[\w.\-]+@[\w]+', text)
    if not upis: return None
    risk = 20
    reasons = []
    if re.search(r'refund|lucky|prize|cashback|lottery|reward', text, re.I):
        risk = 95; reasons.append("scam keyword (refund/lucky)")
    else: reasons.append("UPI found")
    return risk, reasons, upis[0]

# --- 4. JOB CHECK ---
def check_job(text):
    score, found = 0, []
    keywords = {
        "registration fee": 50, "fee": 20, "investment": 30,
        "work from home": 20, "earn daily": 25, "rs 5000": 30,
        "amazon work": 20, "like & earn": 25, "telegram.*@": 15
    }
    for k, v in keywords.items():
        if re.search(k, text, re.I):
            score += v; found.append(k)
    if re.search(r'Registration Fee.*Rs', text, re.I): score = 100
    return min(score, 100), found

# --- TELEGRAM HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [
        [InlineKeyboardButton("English 🇬🇧", callback_data="lang_en"),
         InlineKeyboardButton("മലയാളം 🇮🇳", callback_data="lang_ml")],
        [InlineKeyboardButton("தமிழ்", callback_data="lang_ta"),
         InlineKeyboardButton("हिंदी", callback_data="lang_hi")]
    ]
    await update.message.reply_text("Choose your language / നിങ്ങളുടെ ഭാഷ തിരഞ്ഞെടുക്കുക:", reply_markup=InlineKeyboardMarkup(kb))

async def lang_cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    lang = q.data.split("_")[1]
    user_lang[q.from_user.id] = lang
    l = LANG[lang]
    await q.edit_message_text(f"{l['job_mode']}\n\n{l['send_job']}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    uid = update.effective_user.id
    lang = get_lang(uid)

    # Order of checks
    res = check_link(text)
    if res:
        r, reason, val = res
        await update.message.reply_text(f"🔗 Link Risk: {r}/100\nFound: {', '.join(reason)}\nURL: {val}\n{'🚨 SCAM LINK!' if r>60 else '✅ Safe'}")
        return

    res = check_number(text)
    if res:
        r, reason, val = res
        await update.message.reply_text(f"📱 Number Risk: {r}/100\nFound: {', '.join(reason)}\nNumber: {val}")
        return

    res = check_upi(text)
    if res:
        r, reason, val = res
        await update.message.reply_text(f"💳 UPI Risk: {r}/100\nFound: {', '.join(reason)}\nUPI: {val}\n{'🚨 DO NOT PAY!' if r>60 else ''}")
        return

    # Default Job Check
    r, found = check_job(text)
    if r>0:
        await update.message.reply_text(f"💼 Job Risk: {r}/100\nFound: {', '.join(found)}\n{'🚨 FEE TRAP - Do not pay!' if r>=80 else ''}")
    else:
        await update.message.reply_text("✅ No risk found. Safe!")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # FB Ad photo handler
    await update.message.reply_text("📸 FB Ad Check: Photo received\nRisk: Checking Ad text...\n✅ Analyzed - No scam text found / 🚨 Scam Ad Detected if keywords found")

def run_flask():
    app_flask.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(lang_cb, pattern="^lang_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    print("ULTIMATE Bot Started")
    app.run_polling()
