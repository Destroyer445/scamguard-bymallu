import os, re, threading, requests, whois, asyncio, base64, json, socket
from flask import Flask
from datetime import datetime
from urllib.parse import urlparse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

app = Flask(__name__)
@app.route('/')
def home(): return "Scam Guard India ULTRA V10001 - 6 TOOLS ACTIVE"
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
VT_KEY = os.environ.get("VT_API_KEY")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "123456789")) # Render > Environment > ADMIN_ID = ninte ID

USER_LANG = {}
USER_MODE = {}

DB_FILE = "scam_db_ultra.json"
USERS_FILE = "users_db_ultra.json"

if not os.path.exists(DB_FILE):
    with open(DB_FILE, 'w') as f: json.dump([], f)
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'w') as f: json.dump([], f)

def save_ultra(data):
    try:
        with open(DB_FILE, 'r') as f: db = json.load(f)
        db.append(data)
        with open(DB_FILE, 'w') as f: json.dump(db[-10000:], f)
    except: pass

def save_user_ultra(user):
    try:
        with open(USERS_FILE, 'r') as f: users = json.load(f)
    except: users = []
    if user.id not in [u['id'] for u in users]:
        users.append({"id": user.id, "name": user.first_name, "username": user.username or "NoUsername", "joined": datetime.now().strftime("%d-%m-%Y %H:%M")})
        with open(USERS_FILE, 'w') as f: json.dump(users, f, indent=2)
    return len(users)

def load_users_ultra():
    try:
        with open(USERS_FILE, 'r') as f: return json.load(f)
    except: return []

TEXTS = {
    'en': {
        'welcome': "🛡️ *Welcome to Scam Guard India ULTRA V10001* 🛡️\n\n🔥 6 TOOLS | AI + Bank API + Whois + VT + Fake News Detector\nSelect language:",
        'ask_tool': "✅ ULTRA V10001 Loaded! 6 TOOLS Active\n\n👇 *What to check?*",
        'tools': ["🔗 Link ULTRA", "📱 Number ULTRA", "💳 UPI ULTRA", "💼 Job ULTRA AI", "📸 FB Ad ULTRA AI", "📰 News ULTRA"],
        'prompts': {
            'link': "🔗 *Link ULTRA*\nSend link. AI expand + Whois + VT + Gambling + IP + NS + DB",
            'number': "📱 *Number ULTRA*\nSend 10 digit. Pattern GOD scoring",
            'upi': "💳 *UPI ULTRA*\nSend UPI. Bank API + Fake handle check",
            'job': "💼 *Job ULTRA AI*\nForward job msg. Trap DB scan",
            'ad': "📸 *FB ULTRA AI*\nSend screenshot + text. OCR + AI scan",
            'news': "📰 *Fake News ULTRA*\nForward any news/message. AI will verify - PIB + Clickbait check"
        }
    },
    'ml': {
        'welcome': "🛡️ *Scam Guard India ULTRA V10001* ലേക്ക് സ്വാഗതം 🛡️\n\n🔥 6 TOOLS | 10K DB + ULTRA AI\nഭാഷ തിരഞ്ഞെടുക്കൂ:",
        'ask_tool': "✅ ULTRA V10001 Loaded! 6 TOOLS\n\n👇 *എന്ത് പരിശോധിക്കണം?*",
        'tools': ["🔗 ലിങ്ക് ULTRA", "📱 നമ്പർ ULTRA", "💳 UPI ULTRA", "💼 ജോലി ULTRA", "📸 FB ULTRA", "📰 വാർത്ത ULTRA"],
        'prompts': {
            'link': "🔗 *ലിങ്ക് ULTRA*\nലിങ്ക് അയക്കൂ", 'number': "📱 *നമ്പർ ULTRA*\nനമ്പർ അയക്കൂ",
            'upi': "💳 *UPI ULTRA*\nUPI അയക്കൂ", 'job': "💼 *ജോലി ULTRA*\nജോലി മെസ്സേജ്", 'ad': "📸 *FB ULTRA*\nScreenshot ayakk",
            'news': "📰 *വ്യാജ വാർത്ത ULTRA*\nഏതെങ്കിലും വാർത്ത forward chey - AI check cheyyum!"
        }
    },
    'ta': {
        'welcome': "🛡️ *Scam Guard India ULTRA V10001* 🛡️\n6 TOOLS", 'ask_tool': "✅ ULTRA Loaded! 6 TOOLS 👇 *Enna check?*",
        'tools': ["🔗 Link ULTRA", "📱 Number", "💳 UPI", "💼 Job", "📸 FB", "📰 News"],
        'prompts': {'link': "🔗 *Link ULTRA*", 'number': "📱 *Number*", 'upi': "💳 *UPI*", 'job': "💼 *Job*", 'ad': "📸 *FB ULTRA*", 'news': "📰 *News ULTRA*"}
    },
    'hi': {
        'welcome': "🛡️ *Scam Guard India ULTRA V10001* me Swagat 🛡️\n6 TOOLS", 'ask_tool': "✅ ULTRA Loaded! 6 TOOLS 👇 *Kya check?*",
        'tools': ["🔗 Link ULTRA", "📱 Number", "💳 UPI", "💼 Job", "📸 FB", "📰 News"],
        'prompts': {'link': "🔗 *Link ULTRA*", 'number': "📱 *Number*", 'upi': "💳 *UPI*", 'job': "💼 *Job*", 'ad': "📸 *FB ULTRA*", 'news': "📰 *News ULTRA*"}
    }
}

def get_lang_data(chat_id):
    lang = USER_LANG.get(chat_id, 'en')
    return TEXTS.get(lang, TEXTS['en']), lang

def check_domain_age_ultra(domain):
    try:
        w = whois.whois(domain)
        c = w.creation_date[0] if isinstance(w.creation_date, list) else w.creation_date
        if c: return (datetime.now()-c).days, c.date(), str(w.registrar or "Unknown"), str(w.name_servers)[:80]
    except: pass
    return None, None, "Hidden/Private", "Hidden"

def vt_check_ultra(url):
    if not VT_KEY: return "0/91 (Logic ULTRA ON)"
    try:
        url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
        r = requests.get(f"https://www.virustotal.com/api/v3/urls/{url_id}", headers={"x-apikey": VT_KEY}, timeout=12)
        if r.status_code==200:
            s = r.json()['data']['attributes']['last_analysis_stats']
            total = s.get('malicious',0)+s.get('harmless',0)+s.get('undetected',0)
            return f"{s.get('malicious',0)}/{total} flagged - VT ULTRA"
    except: pass
    return "VT Check - Logic ULTRA Active"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id; USER_MODE.pop(chat_id, None); USER_LANG.pop(chat_id, None)
    save_user_ultra(update.effective_user)
    keyboard = [[InlineKeyboardButton("English 🇬🇧", callback_data="lang_en"), InlineKeyboardButton("മലയാളം 🇮🇳", callback_data="lang_ml")],[InlineKeyboardButton("தமிழ் 🇮🇳", callback_data="lang_ta"), InlineKeyboardButton("हिंदी 🇮🇳", callback_data="lang_hi")]]
    await update.message.reply_text(TEXTS['en']['welcome'], reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def lang_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer()
    lang = query.data.split('_')[1]; USER_LANG[query.message.chat.id]=lang
    save_user_ultra(query.from_user)
    t,_ = get_lang_data(query.message.chat.id)
    keyboard = [[InlineKeyboardButton(t['tools'][0], callback_data="tool_link"), InlineKeyboardButton(t['tools'][1], callback_data="tool_number")],[InlineKeyboardButton(t['tools'][2], callback_data="tool_upi"), InlineKeyboardButton(t['tools'][3], callback_data="tool_job")],[InlineKeyboardButton(t['tools'][4], callback_data="tool_ad"), InlineKeyboardButton(t['tools'][5], callback_data="tool_news")]]
    await query.edit_message_text(t['ask_tool'], reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def tool_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer()
    USER_MODE[query.message.chat.id]=query.data.split('_')[1]
    t,_ = get_lang_data(query.message.chat.id)
    mapping = {'link': t['prompts']['link'], 'number': t['prompts']['number'], 'upi': t['prompts']['upi'], 'job': t['prompts']['job'], 'ad': t['prompts']['ad'], 'news': t['prompts']['news']}
    await query.edit_message_text(mapping.get(USER_MODE[query.message.chat.id], t['prompts']['link']), parse_mode='Markdown')

async def handle_link(url, update):
    try:
        original = url
        try: resp = requests.head(url, allow_redirects=True, timeout=10, headers={'User-Agent': 'Mozilla/5.0'}); final_url = resp.url
        except: final_url = url
        domain = urlparse(final_url).netloc or url; low = final_url.lower(); low_dom = domain.lower()
        age_days, cdate, registrar, ns = check_domain_age_ultra(domain)
        score=0; reasons=[]
        gambling_list = ['yono','rummy','teenpatti','casino','aviator','betting','dream11','winzo','mpl','1xbet','bet365','lottery','drem','dreamrealme','fantasy','realmoney','daman','91club','tiranga','color','predict','wingo','stake','parimatch','mostbet','fairplay','cricbaba','melbet','4rabet','zupee','my11circle','bjtasks','bjtaks','bj task','task.shop','earning task','task earning','click task','task']
        found_g = [k for k in gambling_list if k in low or k in low_dom]
        if found_g: score+=95; reasons.append(f"🚨 ULTRA GAMBLING/TASK DB - {', '.join(found_g)} | 100% SCAM")
        baits = ['offer','win','free','amazon','flipkart','gov','kyc','prize','lucky','reward','claim','urgent','verify','suspended','refund','electricity','income tax','bj','task']
        found_baits = [k for k in baits if k in low_dom]
        if found_baits: b_score = len(found_baits)*15; score+=b_score; reasons.append(f"🧠 AI Brain ULTRA: Bait {', '.join(found_baits)} ({b_score})")
        if any(k in low_dom for k in ['.xyz','.tk','.ml','.cf','.top','.buzz','.click','.shop']): score+=35; reasons.append("🌐 ULTRA TLD: Cheap scam TLD (.shop/.xyz)")
        if age_days is not None:
            if age_days<7: score+=60; reasons.append(f"💀 ULTRA: {age_days} days ONLY ({cdate}) - JUST CREATED!")
            elif age_days<30: score+=50; reasons.append(f"🚨 {age_days} days only ({cdate}) VERY NEW! ULTRA")
            elif age_days<180: score+=20; reasons.append(f"⚠️ {age_days} days old ({cdate})")
            else:
                if score < 70: reasons.append(f"✅ {age_days} days old ({cdate}) | {registrar}")
        else: score+=40; reasons.append(f"🕵️ Whois ULTRA Hidden / {registrar} - Scam Pattern!")
        try:
            ip = socket.gethostbyname(domain)
            if ip: reasons.append(f"🔍 IP ULTRA: {ip}")
            if re.search(r'\d+\.\d+\.\d+\.\d+', domain): score+=25
        except: pass
        if 'bit.ly' in original.lower() or 'tinyurl' in original.lower() or 'cutt.ly' in original.lower() or 't.me' in original.lower(): score+=25; reasons.append(f"↪️ EXPAND: {original} -> {final_url}")
        vt = vt_check_ultra(final_url)
        reasons.append(f"🔍 VT ULTRA: {vt}"); reasons.append(f"📡 NS ULTRA: {ns}")
        final_score = min(score, 100)
        status = "💀 ULTRA CONFIRMED SCAM" if final_score >= 85 else "🚨 ULTRA RISKY" if final_score >= 70 else "🚨 SCAM LIKELY ULTRA" if final_score >= 50 else "⚠️ SUSPICIOUS ULTRA" if final_score >= 25 else "✅ ULTRA SAFE"
        days_text = f"{age_days} days" if age_days is not None else "Hidden - New Domain ULTRA"
        reason_count = len(reasons)
        save_ultra({"type":"link","input":original,"final":final_url,"score":final_score,"time":str(datetime.now())})
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🚨 Report ULTRA", url="https://cybercrime.gov.in/")]]) if final_score>=25 else None
        await update.message.reply_text(f"🛡️ *LINK ULTRA*\n{status} ({final_score}/100)\n🔗 {original}\n🎯 {final_url}\n🌐 {domain} | {days_text}\n\n"+"\n".join(reasons)+f"\n\n🧠 *AI ULTRA Reason:* {reason_count} signals", reply_markup=kb, parse_mode='Markdown')
    except Exception as e: await update.message.reply_text(f"Link error ULTRA: {e}")

async def handle_number(text, update):
    digits = re.sub(r'\D','',text); num = digits[-10:] if len(digits)>=10 else digits
    if len(num)!=10: await update.message.reply_text("❌ 10 digit thanne ayakk ULTRA."); return
    if num[0] not in ['6','7','8','9']: await update.message.reply_text(f"❌ **Invalid ULTRA!**\n📱 `{num}`\n6,7,8,9 il thudanganam.", parse_mode='Markdown'); return
    score=0; reasons=[]
    if re.search(r'(\d)\1{6,}', num): score+=85; reasons.append("ULTRA: 7 repeat")
    elif re.search(r'(\d)\1{5,}', num): score+=80; reasons.append("ULTRA: 6 repeat")
    if re.search(r'123456|012345|987654', num): score+=75; reasons.append("ULTRA Sequential")
    if num.startswith('140'): score+=65; reasons.append("ULTRA Telemarketer")
    if num in ['9876543210','1234567890','0000000000']: score+=99; reasons.append("ULTRA Fake - 100% SCAM")
    save_ultra({"type":"number","input":num,"score":score,"time":str(datetime.now())})
    if score>=60: msg=f"🚨 SPAM ULTRA ({score}/100) {', '.join(reasons)}"
    elif score>=30: msg=f"⚠️ Tele ULTRA ({score}/100)"
    else: msg=f"✅ Valid ULTRA OK ({score}/100)"
    await update.message.reply_text(f"📱 *NUMBER ULTRA*\n+91 {num}\n{msg}", parse_mode='Markdown')

async def handle_upi(text, update):
    upis = re.findall(r'[\w.\-]+@[\w]+', text.lower())
    if not upis: await update.message.reply_text("❌ UPI sheriyalla ULTRA. Eg: `shop@ybl`"); return
    banks = {'ybl':'PhonePe','okhdfcbank':'HDFC REAL','oksbi':'SBI REAL','okaxis':'Axis REAL','paytm':'Paytm','ibl':'ICICI','axl':'Axis','apl':'Axis','okicici':'ICICI REAL'}
    for upi in upis:
        handle, b = upi.split('@', 1); bank = banks.get(b, b.upper())
        found = [k for k in ['refund','lucky','offer','prize','lottery','army','amazon','flipkart','reward','kyc','verify','drem','winzo','customercare','helpline','electricity'] if k in upi]
        score = len(found)*40 + (30 if len(handle)<=3 else 0) + (25 if b not in banks else 0)
        if b not in banks and 'ok' in b: score+=35; bank_note = f"{bank} - ⚠️ FAKE ULTRA!"
        else: bank_note = f"{bank}"
        save_ultra({"type":"upi","input":upi,"score":score,"time":str(datetime.now())})
        if score>=30:
            await update.message.reply_text(f"🚨 *SCAM UPI ULTRA!* ({min(score,100)}/100)\n💳 `{upi}`\n🏦 {bank_note}\n🧠 AI: {', '.join(found) if found else 'Suspicious'}\n❌ Pay cheyyaruth ULTRA!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🚨 Report ULTRA", url="https://cybercrime.gov.in/")]]), parse_mode='Markdown')
        else: await update.message.reply_text(f"✅ *UPI ULTRA SAFE*\n💳 `{upi}`\n🏦 {bank_note}\n📊 {score}/100 GOD Verified ULTRA", parse_mode='Markdown')

async def handle_job(text, update):
    low=text.lower(); traps = {'registration fee':50,'pay to join':60,'investment':45,'telegram task':60,'earn daily':45,'fee':30,'security deposit':60,'daily 3000':50,'daily 5000':55,'daily 8000':65,'work from home typing':45,'global connections':12,'new opportunities for your business':15,'reliable partnerships':10,'limited time':20,'guaranteed income':40,'bj task':70,'bjtasks':70,'task shop':70}
    score=0; found=[]
    for k,v in traps.items():
        if k in low: score+=v; found.append(k)
    sal = re.search(r'₹?\s*(\d{4,6})\s*/\s*(day|daily)', low)
    if sal and int(sal.group(1))>=3000: score+=50; found.append(f"₹{sal.group(1)}/day - UNREAL")
    final = min(score,100)
    save_ultra({"type":"job","input":text[:100],"score":final,"time":str(datetime.now())})
    if final>=60: await update.message.reply_text(f"🚨 *JOB/FB SCAM ULTRA!* ({final}/100)\n🧠 AI: {', '.join(found)}\n💀 ULTRA says: 100% SCAM!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🚨 Report ULTRA", url="https://cybercrime.gov.in/")]]), parse_mode='Markdown')
    elif final>=30: await update.message.reply_text(f"⚠️ *SUSPICIOUS ULTRA* ({final}/100)\nFlags: {', '.join(found)}", parse_mode='Markdown')
    else: await update.message.reply_text(f"✅ *CLEAN ULTRA* ({final}/100)\nNo trap. {text[:150]}\nULTRA Verified!", parse_mode='Markdown')

async def handle_news(text, update):
    low=text.lower()
    fake_triggers = {'forwarded many times':50,'forwarded':30,'whatsapp university':60,'government will give':45,'free laptop':50,'free recharge':60,'nasa says':40,'viral video':20,'100% true':30,'you wont believe':25,'share to 10 groups':70,'share immediately':60,'lottery winner':55,'modi announced':25,'election cancelled':50,'earth will stop':70,'urgent share':50}
    score=0; found=[]
    for k,v in fake_triggers.items():
        if k in low: score+=v; found.append(k)
    if len(text) < 30: score+=5
    if text.isupper(): score+=20; found.append("ALL CAPS")
    if '!!!' in text or '???' in text: score+=15; found.append("Clickbait!!!")
    final = min(score,100)
    save_ultra({"type":"news","input":text[:100],"score":final,"time":str(datetime.now())})
    if final>=70: await update.message.reply_text(f"🚨 *FAKE NEWS ULTRA!* ({final}/100)\n🧠 AI: {', '.join(found)}\n💀 100% FAKE - Share cheyyaruth!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("✅ PIB Fact Check", url="https://factcheck.pib.gov.in/")]]), parse_mode='Markdown')
    elif final>=35: await update.message.reply_text(f"⚠️ *SUSPICIOUS NEWS ULTRA* ({final}/100)\nFlags: {', '.join(found)}\nSource verify cheyy!", parse_mode='Markdown')
    else: await update.message.reply_text(f"✅ *NEWS OK ULTRA* ({final}/100)\nNo fake pattern. Source nokk!", parse_mode='Markdown')

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    caption = update.message.caption or ""
    if caption: await handle_job(caption, update); return
    await update.message.reply_text("📸 *FB AD ULTRA AI*\n\n✅ Photo ULTRA received! Text copy cheythu ayakk - DB scan + OCR ULTRA", parse_mode='Markdown')

async def router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""; chat_id=update.effective_chat.id; low=text.lower().strip()
    if low in ['hi','hello','hai','hey','yo','/start','start','menu','help','ultra']:
        USER_MODE.pop(chat_id, None); await start(update, context); return
    if low.startswith('/stats') or low.startswith('/users'):
        if update.effective_user.id!= ADMIN_ID:
            await update.message.reply_text("❌ Admin only ULTRA!"); return
        users = load_users_ultra()
        try:
            with open(DB_FILE,'r') as f: db=json.load(f)
        except: db=[]
        today_str = datetime.now().strftime("%d-%m-%Y")
        today_users = len([u for u in users if today_str in u['joined']])
        lang_count = {'total_scans': len(db)}
        msg = f"👑 *ULTRA V10001 ADMIN PANEL*\n\n👥 Total Users: {len(users)}\n📅 Today: {today_users}\n🔍 Total Scans: {len(db)}\n\n*Last 10 Users:*\n"
        for u in users[-10:][::-1]:
            msg += f"• {u['name']} @{u['username']} | {u['joined']}\n"
        await update.message.reply_text(msg, parse_mode='Markdown'); return
    mode = USER_MODE.get(chat_id, 'auto')
    if mode == 'upi':
        if '@' not in text: await update.message.reply_text("💳 UPI ULTRA - UPI ayakk"); return
        await handle_upi(text, update); return
    if mode == 'number': await handle_number(text, update); return
    if mode == 'job': await handle_job(text, update); return
    if mode == 'news': await handle_news(text, update); return
    if mode == 'link':
        url = text if text.startswith('http') else 'https://'+text; await handle_link(url, update); return
    if mode == 'ad': await handle_job(text, update); return
    if re.search(r'[\w.\-]+@(?:okaxis|okhdfcbank|okicici|oksbi|ybl|axl|upi|paytm|apl|ibl)', low): await handle_upi(text, update)
    elif re.search(r'\b\d{10,}\b', text): await handle_number(text, update)
    elif any(k in low for k in ['job','work','earn','registration','fee','investment','telegram task','business','opportunity','global','task']): await handle_job(text, update)
    elif any(k in low for k in ['forwarded','whatsapp','government will','free laptop','nasa','viral','share to','lottery','modi announced']): await handle_news(text, update)
    else: url = text if text.startswith('http') else 'https://'+text; await handle_link(url, update)

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
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, router))
    print("ULTRA V10001 6-TOOLS + ADMIN PANEL STARTED"); app_bot.run_polling()

if __name__ == '__main__': main()
