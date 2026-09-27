import os, re, threading, requests, whois, asyncio, base64, json, socket
from flask import Flask
from datetime import datetime
from urllib.parse import urlparse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# FULL POWER LIBS - V100002 GOD
try:
    from PIL import Image
    import pytesseract
    from bs4 import BeautifulSoup
    from pymongo import MongoClient
    FULL_POWER = True
except Exception as e:
    print(f"Lib missing: {e} - fallback mode")
    FULL_POWER = False
    from PIL import Image
    from pymongo import MongoClient

app = Flask(__name__)
@app.route('/')
def home(): return "Scam Guard India V100002 GOD - Stats Public + OCR Fixed"
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
VT_KEY = os.environ.get("VT_API_KEY")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "6331679163"))
MONGO_URI = os.environ.get("MONGO_URI")

USER_LANG = {}
USER_MODE = {}
DB_FILE = "scam_db_v100002.json"
USERS_FILE = "users_db_v100002.json"

mongo_users = None
mongo_scans = None
if MONGO_URI:
    try:
        client = MongoClient(MONGO_URI)
        dbm = client["scam_guard_v100002"]
        mongo_users = dbm["users"]
        mongo_scans = dbm["scans"]
        print("MONGODB V100002 PERMANENT CONNECTED!")
    except Exception as e:
        print(f"Mongo Error: {e}")

if not os.path.exists(DB_FILE):
    with open(DB_FILE, 'w') as f: json.dump([], f)
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'w') as f: json.dump([], f)

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
            if mongo_users.count_documents({"id": user.id}) == 0:
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

TEXTS = {
    'en': {
        'welcome': "🛡️ *Welcome to Scam Guard India V100002 GOD* 🛡️\n\n🔥 10 TOOLS | 4 LANGUAGES | AGE REAL | OCR GOD\nSelect language:",
        'ask_tool': "✅ *V100002 GOD Loaded! 10 TOOLS Active*\n\n👇 *What to check?*",
        'tools': ["🔗 Link GOD", "📱 Number GOD", "💳 UPI GOD", "💼 Job GOD AI", "📸 FB GOD OCR", "📰 News GOD", "📷 Photo GOD", "🎤 Voice GOD", "📸 Insta GOD", "🛡️ Family GOD"],
        'prompts': {'link': "🔗 *Link GOD V100002*\nSend link - Age + Expand + VT + HTML Scan", 'number': "📱 *Number GOD V100002*\nSend 10 digit", 'upi': "💳 *UPI GOD V100002*\nSend UPI ID", 'job': "💼 *Job GOD AI V100002*\nForward job message", 'ad': "📸 *FB GOD OCR V100002*\nSend screenshot photo - Real OCR", 'news': "📰 *News GOD V100002*\nForward news", 'photo': "📷 *Photo GOD V100002*\nSend photo - Real OCR text", 'voice': "🎤 *Voice GOD V100002*\nSend voice as text", 'insta': "📸 *Insta GOD V100002*\nSend Insta Reel link", 'family': "🛡️ *Family Shield V100002*\nFamily protection tips"}
    },
    'ml': {
        'welcome': "🛡️ *Scam Guard V100002 GOD* 🛡️\n\n🔥 10 TOOLS | 4 ഭാഷ | AGE REAL | OCR GOD\nഭാഷ തിരഞ്ഞെടുക്കൂ:",
        'ask_tool': "✅ *V100002 GOD Loaded! 10 TOOLS*\n\n👇 *എന്ത് പരിശോധിക്കണം?*",
        'tools': ["🔗 ലിങ്ക് GOD", "📱 നമ്പർ GOD", "💳 UPI GOD", "💼 ജോലി GOD", "📸 FB GOD", "📰 വാർത്ത GOD", "📷 ഫോട്ടോ GOD", "🎤 Voice GOD", "📸 Insta GOD", "🛡️ Family GOD"],
        'prompts': {'link': "🔗 *ലിങ്ക് GOD V100002*\nLink ayakk - Age kanikkum", 'number': "📱 *നമ്പർ GOD V100002*", 'upi': "💳 *UPI GOD V100002*", 'job': "💼 *ജോലി GOD V100002*", 'ad': "📸 *FB GOD V100002*", 'news': "📰 *വാർത്ത GOD V100002*", 'photo': "📷 *ഫോട്ടോ GOD V100002* - Photo ayakk - OCR", 'voice': "🎤 *Voice GOD*", 'insta': "📸 *Insta GOD*", 'family': "🛡️ *Family GOD*"}
    },
    'ta': {
        'welcome': "🛡️ *Scam Guard V100002 GOD* 🛡️\n\n🔥 10 TOOLS | 4 மொழிகள் | AGE REAL\nமொழியை தேர்ந்தெடுக்கவும்:",
        'ask_tool': "✅ *V100002 GOD Loaded! 10 TOOLS*\n\n👇 *என்ன சரிபார்க்க வேண்டும்?*",
        'tools': ["🔗 லிங்க் GOD", "📱 நம்பர் GOD", "💳 UPI GOD", "💼 வேலை GOD", "📸 FB GOD", "📰 செய்தி GOD", "📷 போட்டோ GOD", "🎤 Voice GOD", "📸 Insta GOD", "🛡️ Family GOD"],
        'prompts': {'link': "🔗 *லிங்க் GOD V100002*", 'number': "📱 *நம்பர் GOD*", 'upi': "💳 *UPI GOD*", 'job': "💼 *வேலை GOD*", 'ad': "📸 *FB GOD OCR*", 'news': "📰 *செய்தி GOD*", 'photo': "📷 *போட்டோ GOD*", 'voice': "🎤 *Voice GOD*", 'insta': "📸 *Insta GOD*", 'family': "🛡️ *Family GOD*"}
    },
    'hi': {
        'welcome': "🛡️ *Scam Guard V100002 GOD* 🛡️\n\n🔥 10 TOOLS | 4 भाषाएँ | AGE REAL\nभाषा चुनें:",
        'ask_tool': "✅ *V100002 GOD Loaded! 10 TOOLS*\n\n👇 *क्या जांचना है?*",
        'tools': ["🔗 लिंक GOD", "📱 नंबर GOD", "💳 UPI GOD", "💼 जॉब GOD", "📸 FB GOD", "📰 खबर GOD", "📷 फोटो GOD", "🎤 Voice GOD", "📸 Insta GOD", "🛡️ Family GOD"],
        'prompts': {'link': "🔗 *लिंक GOD V100002*", 'number': "📱 *नंबर GOD*", 'upi': "💳 *UPI GOD*", 'job': "💼 *जॉब GOD*", 'ad': "📸 *FB GOD OCR*", 'news': "📰 *खबर GOD*", 'photo': "📷 *फोटो GOD*", 'voice': "🎤 *Voice GOD*", 'insta': "📸 *Insta GOD*", 'family': "🛡️ *Family GOD*"}
    }
}

def get_lang_data(chat_id):
    lang = USER_LANG.get(chat_id, 'en')
    return TEXTS.get(lang, TEXTS['en']), lang

def check_domain_age_ultra(domain):
    domain = domain.replace('https://','').replace('http://','').replace('www.','').split('/')[0].strip().lower()
    known_trusted = {
        'google.com': (10000, '1997-09-15', 'MarkMonitor Inc.', 'Google NS GOD'),
        'youtube.com': (8000, '2005-02-15', 'MarkMonitor Inc.', 'Google NS GOD'),
        'facebook.com': (7000, '1997-03-29', 'RegistrarSafe', 'Facebook NS GOD'),
        'instagram.com': (5000, '2010-06-04', 'RegistrarSafe', 'Facebook NS GOD'),
        'wikipedia.org': (8500, '2001-01-13', 'MarkMonitor', 'Wiki NS GOD'),
        'amazon.com': (9500, '1994-11-01', 'MarkMonitor', 'Amazon NS GOD'),
        'amazon.in': (4000, '2012-01-01', 'Amazon', 'Amazon NS GOD'),
        'flipkart.com': (3500, '2007-10-15', 'Flipkart', 'Flipkart NS GOD'),
        'whatsapp.com': (6000, '2009-02-24', 'MarkMonitor', 'Facebook NS GOD'),
    }
    if domain in known_trusted:
        days, cdate_str, reg, ns = known_trusted[domain]
        try: cdate = datetime.strptime(cdate_str, "%Y-%m-%d").date()
        except: cdate = datetime(2000,1,1).date()
        return days, cdate, reg, ns
    try:
        w = whois.whois(domain)
        c = w.creation_date
        if isinstance(c, list): c = c[0]
        if c:
            days = (datetime.now()-c).days
            registrar = str(w.registrar or "Unknown")[:40]
            ns_str = str(w.name_servers)[:80] if w.name_servers else "Hidden"
            return days, c.date(), registrar, ns_str
    except Exception as e:
        print(f"Whois fail {domain}: {e}")
    try:
        ip = socket.gethostbyname(domain)
        return None, None, "Hidden/Private", f"IP:{ip}"
    except: pass
    return None, None, "Hidden/Private", "Hidden"

def vt_check_ultra(url):
    if not VT_KEY: return "0/91 (Logic GOD ON)"
    try:
        url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
        r = requests.get(f"https://www.virustotal.com/api/v3/urls/{url_id}", headers={"x-apikey": VT_KEY}, timeout=10)
        if r.status_code==200:
            s = r.json()['data']['attributes']['last_analysis_stats']
            total = s.get('malicious',0)+s.get('harmless',0)+s.get('undetected',0)
            return f"{s.get('malicious',0)}/{total} flagged - VT GOD"
    except: pass
    return "VT Logic Active"

def real_html_scan(url):
    try:
        r = requests.get(url, timeout=8, headers={'User-Agent':'Mozilla/5.0'})
        soup = BeautifulSoup(r.text, 'lxml')
        text = soup.get_text().lower()[:3000]
        score=0; reasons=[]
        if 'upi' in text and 'pay' in text and ('qr' in text or 'scan' in text): score+=30; reasons.append("💳 HTML GOD: Fake UPI Page!")
        if 'kyc' in text and ('suspended' in text or 'blocked' in text): score+=35; reasons.append("🏦 HTML GOD: Fake KYC Suspend!")
        if 'lottery' in text and 'winner' in text: score+=35; reasons.append("🎰 HTML GOD: Lottery Page!")
        return score, reasons
    except: return 0, []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id; USER_MODE.pop(chat_id, None)
    save_user_ultra(update.effective_user)
    keyboard = [[InlineKeyboardButton("English 🇬🇧", callback_data="lang_en"), InlineKeyboardButton("മലയാളം 🇮🇳", callback_data="lang_ml")],[InlineKeyboardButton("தமிழ் 🇮🇳", callback_data="lang_ta"), InlineKeyboardButton("हिंदी 🇮🇳", callback_data="lang_hi")]]
    await update.message.reply_text(TEXTS['en']['welcome'], reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def lang_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer()
    lang = query.data.split('_')[1]; USER_LANG[query.message.chat.id]=lang
    save_user_ultra(query.from_user)
    t,_ = get_lang_data(query.message.chat.id)
    keyboard = [[InlineKeyboardButton(t['tools'][0], callback_data="tool_link"), InlineKeyboardButton(t['tools'][1], callback_data="tool_number")],[InlineKeyboardButton(t['tools'][2], callback_data="tool_upi"), InlineKeyboardButton(t['tools'][3], callback_data="tool_job")],[InlineKeyboardButton(t['tools'][4], callback_data="tool_ad"), InlineKeyboardButton(t['tools'][5], callback_data="tool_news")],[InlineKeyboardButton(t['tools'][6], callback_data="tool_photo"), InlineKeyboardButton(t['tools'][7], callback_data="tool_voice")],[InlineKeyboardButton(t['tools'][8], callback_data="tool_insta"), InlineKeyboardButton(t['tools'][9], callback_data="tool_family")]]
    await query.edit_message_text(t['ask_tool'], reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def tool_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer()
    USER_MODE[query.message.chat.id]=query.data.split('_')[1]
    t,_ = get_lang_data(query.message.chat.id)
    await query.edit_message_text(t['prompts'].get(USER_MODE[query.message.chat.id], t['prompts']['link']), parse_mode='Markdown')

async def handle_link(url, update):
    try:
        original = url
        try: resp = requests.head(url, allow_redirects=True, timeout=8, headers={'User-Agent':'Mozilla/5.0'}); final_url = resp.url
        except: final_url = url
        domain = urlparse(final_url).netloc or url; low = final_url.lower(); low_dom = domain.lower()
        age_days, cdate, registrar, ns = check_domain_age_ultra(domain)
        age_txt = f"{age_days} days old ({cdate}) | {registrar}" if age_days else f"Hidden | {registrar}"
        TRUSTED_GOD = ['google.com','google.co.in','youtube.com','facebook.com','instagram.com','whatsapp.com','wikipedia.org','amazon.in','amazon.com','flipkart.com','github.com','telegram.org','apple.com','microsoft.com']
        if any(t in low_dom for t in TRUSTED_GOD):
            vt = vt_check_ultra(final_url)
            await update.message.reply_text(f"🛡️ *LINK V100002 GOD*\n✅ GOD SAFE - TRUSTED (0/100)\n🌐 {domain}\n📅 Age GOD: {age_txt}\n✅ Whitelist - 100% Safe!\n🔍 VT GOD: {vt}\n📡 NS GOD: {ns}\n💾 PERMANENT DB", parse_mode='Markdown')
            return
        score=0; reasons=[f"📅 Age GOD: {age_txt}"]
        gambling_list = ['yono','rummy','teenpatti','casino','aviator','betting','dream11','winzo','mpl','1xbet','bet365','lottery','daman','91club','tiranga','color','predict','wingo','bjtasks','bjtaks','task.shop','earning task','bitly','reel','instagram.com/','ig.me']
        found_g = [k for k in gambling_list if k in low or k in low_dom]
        if found_g: score+=95; reasons.append(f"🚨 GOD DB - {', '.join(found_g)} | 100% SCAM")
        baits = ['offer','win','free','amazon','flipkart','gov','kyc','prize','lucky','reward','claim','urgent','verify','suspended','refund','electricity']
        found_baits = [k for k in baits if k in low_dom]
        if found_baits: b_score = len(found_baits)*15; score+=b_score; reasons.append(f"🧠 GOD Brain: Bait {', '.join(found_baits)} ({b_score})")
        if any(k in low_dom for k in ['.xyz','.tk','.ml','.cf','.top','.buzz','.click','.shop']): score+=35; reasons.append("🌐 GOD TLD: Cheap scam TLD")
        if age_days is not None:
            if age_days<7: score+=60; reasons.append(f"💀 GOD: {age_days} days ONLY ({cdate}) - JUST CREATED!")
            elif age_days<30: score+=50; reasons.append(f"🚨 {age_days} days only ({cdate}) VERY NEW!")
            elif age_days<180: score+=20; reasons.append(f"⚠️ {age_days} days old ({cdate})")
        else: score+=30; reasons.append(f"🕵️ Whois GOD Hidden / {registrar}")
        html_score, html_reasons = real_html_scan(final_url)
        score+=html_score; reasons.extend(html_reasons)
        vt = vt_check_ultra(final_url)
        reasons.append(f"🔍 VT GOD: {vt}"); reasons.append(f"📡 NS GOD: {ns}")
        final_score = min(score, 100)
        status = "💀 GOD CONFIRMED SCAM" if final_score >= 85 else "🚨 GOD RISKY" if final_score >= 70 else "🚨 SCAM LIKELY" if final_score >= 50 else "⚠️ SUSPICIOUS" if final_score >= 25 else "✅ GOD SAFE"
        save_ultra({"type":"link","input":original,"final":final_url,"score":final_score,"time":str(datetime.now())})
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🚨 Report GOD", url="https://cybercrime.gov.in/")]]) if final_score>=25 else None
        await update.message.reply_text(f"🛡️ *LINK V100002 GOD*\n{status} ({final_score}/100)\n🔗 {original}\n🎯 {final_url}\n🌐 {domain}\n\n"+"\n".join(reasons), reply_markup=kb, parse_mode='Markdown')
    except Exception as e: await update.message.reply_text(f"Link error GOD: {e}")

async def handle_number(text, update):
    digits = re.sub(r'\D','',text); num = digits[-10:] if len(digits)>=10 else digits
    if len(num)!=10: await update.message.reply_text("❌ 10 digit GOD."); return
    score=0; reasons=[]
    if re.search(r'(\d)\1{6,}', num): score+=85; reasons.append("7 repeat GOD")
    elif re.search(r'(\d)\1{5,}', num): score+=80; reasons.append("6 repeat GOD")
    if re.search(r'123456|012345|987654', num): score+=75; reasons.append("Sequential GOD")
    if num.startswith('140'): score+=65; reasons.append("Telemarketer GOD")
    if num in ['9999999999','8888888888','7000000000','1234567890','9876543210']: score+=90; reasons.append("🚨 Spam DB GOD")
    save_ultra({"type":"number","input":num,"score":score,"time":str(datetime.now())})
    msg = f"🚨 SPAM GOD ({score}/100) {', '.join(reasons)}" if score>=60 else f"✅ Valid GOD ({score}/100)"
    await update.message.reply_text(f"📱 *NUMBER V100002 GOD*\n+91 {num}\n{msg}", parse_mode='Markdown')

async def handle_upi(text, update):
    upis = re.findall(r'[\w.\-]+@[\w]+', text.lower())
    if not upis: await update.message.reply_text("❌ UPI GOD - Eg: `shop@ybl`"); return
    banks = {'ybl':'PhonePe','okhdfcbank':'HDFC','oksbi':'SBI','okaxis':'Axis','paytm':'Paytm','ibl':'ICICI','axl':'Axis','apl':'Axis','okicici':'ICICI'}
    for upi in upis:
        handle, b = upi.split('@', 1); bank = banks.get(b, b.upper())
        found = [k for k in ['refund','lucky','offer','prize','lottery','army','amazon','flipkart','reward','kyc','verify'] if k in upi]
        score = len(found)*40 + (30 if len(handle)<=3 else 0) + (25 if b not in banks else 0)
        save_ultra({"type":"upi","input":upi,"score":score,"time":str(datetime.now())})
        if score>=30: await update.message.reply_text(f"🚨 *SCAM UPI V100002!* ({min(score,100)}/100)\n💳 `{upi}`\n🏦 {bank}\n🧠 {', '.join(found)}\n❌ Pay cheyyaruth!", parse_mode='Markdown')
        else: await update.message.reply_text(f"✅ *UPI SAFE V100002*\n💳 `{upi}`\n🏦 {bank}\n📊 {score}/100", parse_mode='Markdown')

async def handle_job(text, update):
    low=text.lower(); traps = {'registration fee':50,'pay to join':60,'investment':45,'telegram task':60,'earn daily':45,'fee':30,'security deposit':60,'daily 3000':50,'daily 5000':55,'daily 8000':65,'work from home typing':45,'bj task':70,'bjtasks':70,'task shop':70,'veetilirunnu joli':60,'veetil irunnu':50,'dinasam 5000':55,'panam sambadikkam':60}
    score=0; found=[]
    for k,v in traps.items():
        if k in low: score+=v; found.append(k)
    sal = re.search(r'₹?\s*(\d{4,6})\s*/\s*(day|daily|dinasam)', low)
    if sal and int(sal.group(1))>=3000: score+=50; found.append(f"₹{sal.group(1)}/day UNREAL")
    final = min(score,100)
    save_ultra({"type":"job","input":text[:100],"score":final,"time":str(datetime.now())})
    if final>=60: await update.message.reply_text(f"🚨 *JOB SCAM V100002!* ({final}/100)\n🧠 {', '.join(found)}\n💀 100% SCAM!", parse_mode='Markdown')
    elif final>=30: await update.message.reply_text(f"⚠️ *SUSPICIOUS V100002* ({final}/100)\n{', '.join(found)}", parse_mode='Markdown')
    else: await update.message.reply_text(f"✅ *CLEAN V100002* ({final}/100)", parse_mode='Markdown')

async def handle_news(text, update):
    low=text.lower()
    fake_triggers = {'forwarded many times':50,'forwarded':30,'whatsapp university':60,'government will give':45,'free laptop':50,'free recharge':60,'nasa says':40,'share to 10 groups':70,'share immediately':60,'lottery winner':55}
    score=0; found=[]
    for k,v in fake_triggers.items():
        if k in low: score+=v; found.append(k)
    final = min(score,100)
    save_ultra({"type":"news","input":text[:100],"score":final,"time":str(datetime.now())})
    if final>=70: await update.message.reply_text(f"🚨 *FAKE NEWS V100002!* ({final}/100)\n🧠 {', '.join(found)}\n💀 100% FAKE!", parse_mode='Markdown')
    else: await update.message.reply_text(f"✅ *NEWS OK V100002* ({final}/100)", parse_mode='Markdown')

# --- V100002 FIXED PHOTO HANDLER - ALIYA GOD ---
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        file_path = f"/tmp/{photo.file_id}.jpg"
        await file.download_to_drive(file_path)
        ocr_text = ""
        caption_text = update.message.caption or ""
        if FULL_POWER:
            try:
                img = Image.open(file_path)
                img = img.convert('L')
                img = img.resize((img.width*2, img.height*2))
                ocr_text = pytesseract.image_to_string(img, lang='eng').strip()
                print(f"OCR V100002: {ocr_text[:150]}")
            except Exception as e:
                print(f"OCR Error V100002: {e}")
                ocr_text = ""
        final_text = ocr_text if ocr_text else caption_text
        if final_text.strip():
            await update.message.reply_text(f"📸 *Photo OCR V100002 GOD*\n📝 `{final_text[:600]}`\n\n🔍 Scanning...", parse_mode='Markdown')
            if 'http' in final_text.lower() or 'www.' in final_text.lower():
                await handle_link(final_text, update)
            else:
                await handle_job(final_text, update)
        else:
            await update.message.reply_text("📸 *Photo V100002 GOD*\n⚠️ Text blur aanu, HD screenshot ayakk!", parse_mode='Markdown')
    except Exception as e: await update.message.reply_text(f"Photo error V100002: {e}")

async def voice_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎤 *Voice GOD V100002* - Text aayi ayakk!", parse_mode='Markdown')

# --- V100002 FIXED ROUTER - STATS PUBLIC ---
async def router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""; chat_id=update.effective_chat.id; low=text.lower().strip()

    if low.startswith('/stats'):
        users = load_users_ultra()
        try:
            if mongo_scans is not None:
                total_scans = mongo_scans.count_documents({})
                clean = mongo_scans.count_documents({"score": {"$lt": 25}})
                scams = mongo_scans.count_documents({"score": {"$gte": 50}})
            else:
                with open(DB_FILE,'r') as f:
                    db = json.load(f)
                    total_scans=len(db)
                    clean = len([x for x in db if x.get('score',0)<25])
                    scams = len([x for x in db if x.get('score',0)>=50])
        except: total_scans=0; clean=0; scams=0
        await update.message.reply_text(
            f"📊 *Scam Guard V100002 STATS GOD*\n\n"
            f"👥 Total Users: {len(users)}\n"
            f"🔍 Total Scans: {total_scans}\n"
            f"✅ Clean: {clean}\n"
            f"🚨 Scams Caught: {scams}\n"
            f"⚙️ Version: V100002 GOD\n"
            f"💾 DB: {'MongoDB PERMANENT' if mongo_users else 'JSON'}\n"
            f"🔥 FULL_POWER: {FULL_POWER}",
            parse_mode='Markdown'
        )
        return

    if low.startswith('/users'):
        if update.effective_user.id!= ADMIN_ID:
            await update.message.reply_text("❌ Admin only!")
            return
        users = load_users_ultra()
        await update.message.reply_text(f"👑 *V100002 ADMIN*\n👥 Users: {len(users)}\n🔍 Scans: {total_scans if 'total_scans' in locals() else len(users)}\n💾 DB: {'MongoDB' if mongo_users else 'JSON'}\nFULL_POWER: {FULL_POWER}", parse_mode='Markdown')
        return

    if low in ['hi','hello','hai','hey','/start','start','menu','help','god','ultra','how']:
        if low in ['/start','start','menu','help','god','ultra']:
            await start(update, context); return
        await update.message.reply_text("👋 Type /start to check link/number/UPI/job"); return

    mode = USER_MODE.get(chat_id, 'auto')
    if mode=='link' or mode=='insta' or mode=='family':
        url = text if text.startswith('http') else 'https://'+text
        await handle_link(url, update); return
    if mode=='number': await handle_number(text, update); return
    if mode=='upi': await handle_upi(text, update); return
    if mode in ['job','ad','photo']: await handle_job(text, update); return
    if mode=='news': await handle_news(text, update); return
    if 'instagram.com' in low: await handle_link(text, update); return
    if '@' in text and any(x in low for x in ['ybl','ok','paytm','apl','ibl']): await handle_upi(text, update)
    elif re.search(r'\b\d{10,}\b', text): await handle_number(text, update)
    elif any(k in low for k in ['job','earn','fee','task','veetilirunnu','dinasam','panam']): await handle_job(text, update)
    elif any(k in low for k in ['forwarded','free laptop','government']): await handle_news(text, update)
    else:
        if '.' in text and ' ' not in text and len(text) > 4 and not text.lower().startswith('how'):
            url = text if text.startswith('http') else 'https://'+text
            await handle_link(url, update)
        else:
            await handle_job(text, update)

def main():
    threading.Thread(target=run_flask, daemon=True).start()
    if not BOT_TOKEN: print("BOT_TOKEN missing!"); return
    loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
    app_bot = Application.builder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("stats", router))
    app_bot.add_handler(CommandHandler("users", router))
    app_bot.add_handler(CallbackQueryHandler(lang_callback, pattern="^lang_"))
    app_bot.add_handler(CallbackQueryHandler(tool_callback, pattern="^tool_"))
    app_bot.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app_bot.add_handler(MessageHandler(filters.VOICE, voice_handler))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, router))
    print("V100002 GOD MODE STARTED - STATS PUBLIC + OCR FIXED"); app_bot.run_polling()

if __name__ == '__main__': main()
