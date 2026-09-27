import os, re, threading, requests, whois, asyncio, base64, json, socket
from flask import Flask
from datetime import datetime
from urllib.parse import urlparse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

try:
    from PIL import Image, ImageOps, ImageEnhance, ImageFilter
    import pytesseract
    from bs4 import BeautifulSoup
    from pymongo import MongoClient
    FULL_POWER = True
except Exception as e:
    print(f"Lib missing: {e}")
    FULL_POWER = False
    from PIL import Image, ImageOps, ImageEnhance, ImageFilter
    from pymongo import MongoClient

app = Flask(__name__)
@app.route('/')
def home(): return "Scam Guard V100010 ALL SCAM ULTRA 1LAKH10 LIVE"
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
VT_KEY = os.environ.get("VT_API_KEY")

try:
    ADMIN_ID = int(str(os.environ.get("ADMIN_ID", "6331679163")).strip())
except:
    ADMIN_ID = 6331679163

MONGO_URI = os.environ.get("MONGO_URI") or os.environ.get("MONGODB_URI") or os.environ.get("MONGO_URL")

USER_LANG = {}
USER_MODE = {}
DB_FILE = "scam_db_v100010.json"
USERS_FILE = "users_db_v100010.json"

mongo_users = None
mongo_scans = None
if MONGO_URI:
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
        dbm = client["scam_guard_v100010"]
        mongo_users = dbm["users"]
        mongo_scans = dbm["scans"]
        mongo_users.find_one()
        print("MONGODB CONNECTED!")
    except Exception as e:
        print(f"Mongo Error use JSON: {e}")
        mongo_users = None
        mongo_scans = None

for f in [DB_FILE, USERS_FILE]:
    if not os.path.exists(f):
        with open(f, 'w') as fp: json.dump([], fp)

def save_ultra(data):
    if mongo_scans is not None:
        try: mongo_scans.insert_one(data); return
        except: pass
    try:
        with open(DB_FILE, 'r') as f: db = json.load(f)
        db.append(data)
        with open(DB_FILE, 'w') as f: json.dump(db[-10000:], f)
    except: pass

def save_user_ultra(user):
    if mongo_users is not None:
        try:
            if mongo_users.count_documents({"id": user.id}, maxTimeMS=2000) == 0:
                mongo_users.insert_one({"id": user.id, "name": user.first_name, "username": user.username or "NoUsername", "joined": datetime.now().strftime("%d-%m-%Y %H:%M")})
            return mongo_users.count_documents({})
        except: pass
    try:
        with open(USERS_FILE, 'r') as f: users = json.load(f)
    except: users = []
    if user.id not in [u['id'] for u in users]:
        users.append({"id": user.id, "name": user.first_name, "username": user.username or "NoUsername", "joined": datetime.now().strftime("%d-%m-%Y %H:%M")})
        with open(USERS_FILE, 'w') as f: json.dump(users, f, indent=2)
    return len(users)

def load_users_ultra():
    if mongo_users is not None:
        try: return list(mongo_users.find({}, {"_id":0}))
        except: pass
    try:
        with open(USERS_FILE, 'r') as f: return json.load(f)
    except: return []

# ===== ALL SCAM DATABASE V100010 =====
ALL_SCAM_KEYWORDS = {
    'gambling': ['amb.game', 'play. enjoy', 'anytime', 'rummy', 'yono', 'daman', '91club', 'wingo', 'aviator', 'casino', 'betting', 'play now win', 'good games'],
    'crypto_telegram': ['t.me/', 'alexyulia', 'alphacrypto', 'aitoken', 'unlock daily benefits', 'unlock benefits', 'click to join', 'level up your day with ai', 'follow to unlock', 'qr code', 'crypto bot', 'usdt earning', 'alpha crypto', 'daily benefits'],
    'job': ['registration fee', 'pay to join', 'telegram task', 'daily 5000', 'bj task', 'veetilirunnu', 'work from home 5000', 'like and earn', 'task.shop', 'bjtasks', 'part time 2000', 'veetilirunnu joli'],
    'loan': ['instant loan', 'pan card loan', 'adhar loan', '0% interest', 'kyc update loan', 'personal loan approved', '5 min loan', 'instant personal loan'],
    'kyc_bank': ['sbi account blocked', 'account suspended', 'electricity bill pending', 'kyc expired', 'update kyc', 'bank account blocked', 'sbi yono blocked'],
    'investment': ['2x profit', 'double money', 'trading investment', 'usdt double', 'crypto investment', 'forex profit', 'invest 500 get 5000'],
    'parcel_gift': ['customs parcel', 'gift parcel', 'uk doctor', 'army gift', 'parcel fee', 'airport parcel', 'military parcel']
}

TEXTS = {
    'en': {'welcome': "🛡️ Welcome to Scam Guard India V100010 ALL SCAM ULTRA 🛡️\n\n🔥 10 TOOLS | 1LAKH10 | 100+ SCAMS\nSelect language:", 'ask_tool': "✅ V100010 GOD Loaded! 10 TOOLS Active\n\n👇 What to check?", 'tools': ["🔗 Link GOD", "📱 Number GOD", "💳 UPI GOD", "💼 Job GOD", "📸 FB GOD", "📰 News GOD", "📷 Photo GOD", "🎤 Voice GOD", "📸 Insta GOD", "🛡️ Family GOD"], 'prompts': {'link': "🔗 Link GOD - Send link", 'number': "📱 Number GOD", 'upi': "💳 UPI GOD", 'job': "💼 Job GOD", 'ad': "📸 FB GOD OCR", 'news': "📰 News GOD", 'photo': "📷 Photo GOD", 'voice': "🎤 Voice GOD", 'insta': "📸 Insta GOD", 'family': "🛡️ Family GOD"}},
    'ml': {'welcome': "🛡️ Scam Guard V100010 ALL SCAM ULTRA 🛡️\n\n🔥 10 TOOLS | 1LAKH10 | 100+ SCAMS\nഭാഷ തിരഞ്ഞെടുക്കൂ:", 'ask_tool': "✅ V100010 Loaded!\n\n👇 എന്ത് പരിശോധിക്കണം?", 'tools': ["🔗 ലിങ്ക് GOD", "📱 നമ്പർ GOD", "💳 UPI GOD", "💼 ജോലി GOD", "📸 FB GOD", "📰 വാർത്ത GOD", "📷 ഫോട്ടോ GOD", "🎤 Voice GOD", "📸 Insta GOD", "🛡️ Family GOD"], 'prompts': {'link': "🔗 ലിങ്ക് GOD", 'number': "📱 നമ്പർ GOD", 'upi': "💳 UPI GOD", 'job': "💼 ജോലി GOD", 'ad': "📸 FB GOD", 'news': "📰 വാർത്ത GOD", 'photo': "📷 ഫോട്ടോ GOD", 'voice': "🎤 Voice", 'insta': "📸 Insta", 'family': "🛡️ Family"}},
    'ta': {'welcome': "🛡️ Scam Guard V100010 🛡️", 'ask_tool': "✅ V100010 Loaded!", 'tools': ["🔗 லிங்க் GOD", "📱 நம்பர் GOD", "💳 UPI GOD", "💼 வேலை GOD", "📸 FB GOD", "📰 செய்தி GOD", "📷 போட்டோ GOD", "🎤 Voice GOD", "📸 Insta GOD", "🛡️ Family GOD"], 'prompts': {'link': "🔗 Link GOD", 'number': "📱 Number", 'upi': "💳 UPI", 'job': "💼 Job", 'ad': "📸 FB", 'news': "📰 News", 'photo': "📷 Photo", 'voice': "🎤 Voice", 'insta': "📸 Insta", 'family': "🛡️ Family"}},
    'hi': {'welcome': "🛡️ Scam Guard V100010 🛡️", 'ask_tool': "✅ V100010 Loaded!", 'tools': ["🔗 लिंक GOD", "📱 नंबर GOD", "💳 UPI GOD", "💼 जॉब GOD", "📸 FB GOD", "📰 खबर GOD", "📷 फोटो GOD", "🎤 Voice GOD", "📸 Insta GOD", "🛡️ Family GOD"], 'prompts': {'link': "🔗 Link", 'number': "📱 Number", 'upi': "💳 UPI", 'job': "💼 Job", 'ad': "📸 FB", 'news': "📰 News", 'photo': "📷 Photo", 'voice': "🎤 Voice", 'insta': "📸 Insta", 'family': "🛡️ Family"}}
}

def get_lang_data(chat_id):
    lang = USER_LANG.get(chat_id, 'en')
    return TEXTS.get(lang, TEXTS['en']), lang

def check_domain_age_ultra(domain):
    domain = domain.replace('https://','').replace('http://','').replace('www.','').split('/')[0].strip().lower()
    known = {'google.com': (10000, '1997-09-15'), 'youtube.com': (8000, '2005-02-15'), 'facebook.com': (7000, '1997-03-29'), 'instagram.com': (5000, '2010-06-04'), 'amazon.in': (4000, '2012-01-01')}
    if domain in known:
        days, cdate_str = known[domain]
        return days, datetime.strptime(cdate_str, "%Y-%m-%d").date(), "Google/Meta", "Safe NS"
    try:
        w = whois.whois(domain)
        c = w.creation_date
        if isinstance(c, list): c = c[0]
        if c: return (datetime.now()-c).days, c.date(), str(w.registrar or "Unknown")[:30], "Hidden"
    except: pass
    return None, None, "Hidden", "Hidden"

def vt_check_ultra(url):
    if not VT_KEY: return "Logic GOD ON"
    try:
        url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
        r = requests.get(f"https://www.virustotal.com/api/v3/urls/{url_id}", headers={"x-apikey": VT_KEY}, timeout=5)
        if r.status_code==200:
            s = r.json()['data']['attributes']['last_analysis_stats']
            return f"{s.get('malicious',0)}/91 VT"
    except: pass
    return "VT Logic"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    USER_MODE.pop(update.effective_chat.id, None)
    save_user_ultra(update.effective_user)
    keyboard = [[InlineKeyboardButton("English 🇬🇧", callback_data="lang_en"), InlineKeyboardButton("മലയാളം 🇮🇳", callback_data="lang_ml")],[InlineKeyboardButton("தமிழ் 🇮🇳", callback_data="lang_ta"), InlineKeyboardButton("हिंदी 🇮🇳", callback_data="lang_hi")]]
    await update.message.reply_text(TEXTS['en']['welcome'], reply_markup=InlineKeyboardMarkup(keyboard))

async def lang_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer()
    lang = query.data.split('_')[1]; USER_LANG[query.message.chat.id]=lang
    save_user_ultra(query.from_user)
    t,_ = get_lang_data(query.message.chat.id)
    keyboard = [[InlineKeyboardButton(t['tools'][0], callback_data="tool_link"), InlineKeyboardButton(t['tools'][1], callback_data="tool_number")],[InlineKeyboardButton(t['tools'][2], callback_data="tool_upi"), InlineKeyboardButton(t['tools'][3], callback_data="tool_job")],[InlineKeyboardButton(t['tools'][4], callback_data="tool_ad"), InlineKeyboardButton(t['tools'][5], callback_data="tool_news")],[InlineKeyboardButton(t['tools'][6], callback_data="tool_photo"), InlineKeyboardButton(t['tools'][7], callback_data="tool_voice")],[InlineKeyboardButton(t['tools'][8], callback_data="tool_insta"), InlineKeyboardButton(t['tools'][9], callback_data="tool_family")]]
    await query.edit_message_text(t['ask_tool'], reply_markup=InlineKeyboardMarkup(keyboard))

async def tool_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer()
    USER_MODE[query.message.chat.id]=query.data.split('_')[1]
    t,_ = get_lang_data(query.message.chat.id)
    await query.edit_message_text(t['prompts'].get(USER_MODE[query.message.chat.id], t['prompts']['link']))

async def handle_link(url, update):
    try:
        original = url
        try: resp = requests.head(url, allow_redirects=True, timeout=5, headers={'User-Agent':'Mozilla/5.0'}); final_url = resp.url
        except: final_url = url
        domain = urlparse(final_url).netloc or url; low = final_url.lower()
        age_days, cdate, registrar, ns = check_domain_age_ultra(domain)
        age_txt = f"{age_days} days ({cdate})" if age_days else "Hidden"
        if any(t in domain.lower() for t in ['google.com','youtube.com','facebook.com','amazon.in']):
            await update.message.reply_text(f"LINK V100010\nSAFE TRUSTED (0/100)\n{domain}\n{age_txt}"); return
        score=0
        if any(k in low for k in ['yono','rummy','casino','aviator','betting','daman','91club','wingo','bjtasks','task.shop','t.me/alex','alphacrypto','aitoken']): score+=95
        if age_days and age_days<7: score+=60
        if 't.me/' in low: score+=80
        save_ultra({"type":"link","input":original,"score":score,"time":str(datetime.now())})
        await update.message.reply_text(f"LINK V100010\n{'🚨 SCAM' if score>=70 else '⚠️ SUSPICIOUS' if score>=25 else '✅ SAFE'} ({score}/100)\n{domain}\nAge: {age_txt}")
    except Exception as e: await update.message.reply_text(f"Link error: {e}")

async def handle_number(text, update):
    digits = re.sub(r'\D','',text); num = digits[-10:] if len(digits)>=10 else digits
    if len(num)!=10: await update.message.reply_text("10 digit needed"); return
    score=85 if re.search(r'(\d)\1{6,}', num) else 0
    save_ultra({"type":"number","input":num,"score":score,"time":str(datetime.now())})
    await update.message.reply_text(f"+91 {num} - {'SPAM' if score>=60 else 'OK'} ({score}/100) V100010")

async def handle_upi(text, update):
    upis = re.findall(r'[\w.\-]+@[\w]+', text.lower())
    if not upis: await update.message.reply_text("UPI Eg: shop@ybl"); return
    for upi in upis:
        score = 90 if any(k in upi for k in ['refund','offer','prize','lottery']) else 0
        save_ultra({"type":"upi","input":upi,"score":score,"time":str(datetime.now())})
        await update.message.reply_text(f"{'🚨 SCAM' if score>=30 else '✅ SAFE'} UPI {upi} ({score}/100) V100010")

async def handle_job(text, update):
    low = text.lower()
    score = 0
    found_type = ""
    for scam_type, keywords in ALL_SCAM_KEYWORDS.items():
        for k in keywords:
            if k in low:
                score += 40
                found_type = scam_type
                break
    if any(k in low for k in ['registration fee', 'pay to join', 'instant loan', 'sbi blocked', 'double money', 't.me/']):
        score = 95
    save_ultra({"type":found_type or "job","input":text[:100],"score":score,"time":str(datetime.now())})
    if score >= 80:
        msg = f"🚨 {found_type.upper()} SCAM DETECTED! ({score}/100) V100010\n\n⚠️ 100% SCAM! Money pokum!\n❌ Pay cheyyaruthu!\n\n🛡️ Scam Guard India V100010"
    elif score >= 40:
        msg = f"⚠️ SUSPICIOUS {found_type.upper()} ({score}/100) V100010\n\nCareful! Scam chance!\n\n🛡️ Scam Guard"
    else:
        msg = f"✅ CLEAN ({score}/100) V100010\n\nSafe aanennu thonnunnu!\n\n🛡️ Scam Guard"
    await update.message.reply_text(msg)

# ===== PHOTO GOD V100010 - ALL SCAM SMART - NO TIP =====
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        file = None
        if update.message.photo:
            file = await context.bot.get_file(update.message.photo[-1].file_id)
        elif update.message.document:
            file = await context.bot.get_file(update.message.document.file_id)
        if not file: return
        file_path = f"/tmp/{file.file_id}.jpg"
        await file.download_to_drive(file_path)

        caption = (update.message.caption or "").lower()
        ocr_text = ""
        try:
            if FULL_POWER:
                img = Image.open(file_path)
                img = ImageOps.exif_transpose(img)
                w,h = img.size
                if w < 1200: img = img.resize((int(w*2.2), int(h*2.2)), Image.LANCZOS)
                img_gray = ImageOps.grayscale(img)
                img_gray = img_gray.filter(ImageFilter.SHARPEN)
                img_gray = ImageEnhance.Contrast(img_gray).enhance(1.6)
                t1 = pytesseract.image_to_string(img_gray, lang='eng', config='--psm 6').strip()
                t2 = pytesseract.image_to_string(img_gray, lang='eng', config='--psm 11').strip()
                ocr_text = f"{t1} {t2}".strip()
        except: ocr_text = ""

        final = (ocr_text + " " + caption).lower()

        detected = None
        for scam_type, keywords in ALL_SCAM_KEYWORDS.items():
            for k in keywords:
                if k in final:
                    detected = scam_type
                    break
            if detected: break

        if detected:
            if detected == 'gambling':
                txt = f"🚨 GAMBLING AD SCAM! (95/100) V100010\n\n🎰 AMB.GAME / Rummy / Aviator - Fake Earning App!\n❌ Install cheyyaruthu! Money pokum!\n\n🛡️ Scam Guard V100010"
            elif detected == 'crypto_telegram':
                txt = f"🚨 CRYPTO TELEGRAM BOT SCAM! (92/100) V100010\n\n🤖 Found: {ocr_text[:120] or caption[:120]}\n⚠️ t.me/AlexYulia_bot, AlphaCrypto9002 pola bots SCAM!\n❌ QR Scan / Click cheyyaruthu!\n\n🛡️ Scam Guard V100010"
            elif detected == 'loan':
                txt = f"🚨 LOAN SCAM! (95/100) V100010\n\n💸 Instant Loan - 100% Fraud!\n❌ Fee adakkaruthu!\n\n🛡️ Scam Guard V100010"
            elif detected == 'kyc_bank':
                txt = f"🚨 BANK KYC SCAM! (98/100) V100010\n\n🏦 SBI Blocked / Electricity Bill - Fake!\n❌ Link click cheyyaruthu!\n\n🛡️ Scam Guard V100010"
            elif detected == 'job':
                txt = f"🚨 JOB SCAM! (95/100) V100010\n\n💼 Registration Fee / Telegram Task - SCAM!\n❌ Pay cheyyaruthu!\n\n🛡️ Scam Guard V100010"
            else:
                txt = f"🚨 {detected.upper()} SCAM! (90/100) V100010\n\n⚠️ {final[:150]}\n❌ Scam aanu!\n\n🛡️ Scam Guard V100010"
            await update.message.reply_text(txt)
            save_ultra({"type":f"photo_{detected}","input":final[:100],"score":95,"time":str(datetime.now())})
        else:
            if len(final.strip()) < 5:
                await update.message.reply_text(f"⚠️ SUSPICIOUS AD! (75/100) V100010\n\nPhoto text clear alla, but FB la kanda AI/Crypto/Loan ad aanel 99% SCAM!\n❌ Click/Install cheyyaruthu!\nLink undel Link GODil check cheyyu!\n\n🛡️ Scam Guard India V100010")
            else:
                await update.message.reply_text(f"📸 OCR V100010:\n{ocr_text[:500]}\n\nScanning...")
                await handle_job(final, update)
    except Exception as e:
        print(f"Photo error: {e}")
        await update.message.reply_text(f"⚠️ SUSPICIOUS AD! (70/100) V100010\n\nScam chance undu! Careful!\n\n🛡️ Scam Guard")

async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Voice - text aayi ayakk! V100010")

async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        users = load_users_ultra()
        total_scans = 0
        try:
            with open(DB_FILE,'r') as f: total_scans = len(json.load(f))
        except: total_scans = 0
        await update.message.reply_text(f"STATS V100010 ALL SCAM ULTRA 1LAKH10\n\nUsers: {len(users)}\nScans: {total_scans}\nDB: {'Mongo OK' if mongo_users else 'JSON'}\nFULL_POWER: {FULL_POWER}\nADMIN: {ADMIN_ID}\nYour ID: {update.effective_user.id}\nBot Alive!", parse_mode=None)
    except Exception as e:
        await update.message.reply_text(f"Stats Error: {e}", parse_mode=None)

async def id_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        is_admin = (update.effective_user.id == ADMIN_ID)
        if is_admin:
            await update.message.reply_text(f"ID V100010 ADMIN\nYou: {update.effective_user.id}\nAdmin: {ADMIN_ID} YES\nMongo: {'YES' if mongo_users else 'NO'}\nFULL_POWER: {FULL_POWER}", parse_mode=None)
        else:
            await update.message.reply_text(f"ID V100010\nYour ID: {update.effective_user.id}\nBot: Scam Guard India V100010\nStatus: Alive ✅", parse_mode=None)
    except:
        await update.message.reply_text(f"ID: {update.effective_user.id}", parse_mode=None)

async def users_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!= ADMIN_ID:
        await update.message.reply_text(f"Admin only! You {update.effective_user.id}", parse_mode=None); return
    users = load_users_ultra()
    await update.message.reply_text(f"ADMIN V100010\nUsers: {len(users)}\nDB: {'Mongo' if mongo_users else 'JSON'}", parse_mode=None)

async def router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    if not text or text.startswith('/'): return
    if '.' in text and ' ' not in text and len(text)>4:
        url = text if text.startswith('http') else 'https://'+text
        await handle_link(url, update); return
    if re.search(r'\b\d{10}\b', text): await handle_number(text, update); return
    await handle_job(text, update)

def main():
    threading.Thread(target=run_flask, daemon=True).start()
    if not BOT_TOKEN: print("BOT_TOKEN missing!"); return
    app_bot = Application.builder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("stats", stats_cmd))
    app_bot.add_handler(CommandHandler("id", id_cmd))
    app_bot.add_handler(CommandHandler("users", users_cmd))
    app_bot.add_handler(CallbackQueryHandler(lang_callback, pattern="^lang_"))
    app_bot.add_handler(CallbackQueryHandler(tool_callback, pattern="^tool_"))
    app_bot.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app_bot.add_handler(MessageHandler(filters.Document.ALL, photo_handler))
    app_bot.add_handler(MessageHandler(filters.VOICE, voice_handler))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, router))
    print(f"V100010 ALL SCAM ULTRA STARTED - ADMIN {ADMIN_ID}")
    app_bot.run_polling(drop_pending_updates=True)

if __name__ == '__main__': main()
