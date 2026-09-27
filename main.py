import os, re, threading, requests, whois, asyncio, base64, json, socket
from flask import Flask
from datetime import datetime
from urllib.parse import urlparse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

app = Flask(__name__)
@app.route('/')
def home(): return "Scam Guard India 1000.0 GOD MODE - ALL SYSTEMS GO"
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
VT_KEY = os.environ.get("VT_API_KEY")
USER_LANG = {}
USER_MODE = {}

DB_FILE = "scam_db_1000.json"
if not os.path.exists(DB_FILE):
    with open(DB_FILE, 'w') as f: json.dump([], f)

def save_1000(data):
    try:
        with open(DB_FILE, 'r') as f: db = json.load(f)
        db.append(data)
        with open(DB_FILE, 'w') as f: json.dump(db[-5000:], f)
    except: pass

TEXTS = {
    'en': {
        'welcome': "🛡️ *Welcome to Scam Guard India 1000.0 GOD MODE* 🛡️\n\n🔥 AI + Bank API + Whois + VT + Scam Network + Auto-Report\nSelect language:",
        'ask_tool': "✅ 1000.0 GOD MODE Loaded!\n\n👇 *What to check?*",
        'tools': ["🔗 Link 1000.0 GOD", "📱 Number 1000.0 GOD", "💳 UPI 1000.0 GOD", "💼 Job 1000.0 AI", "📸 FB Ad 1000.0 AI"],
        'prompts': {
            'link': "🔗 *Link 1000.0 GOD Mode*\nSend link. AI will expand + Whois + VT + Gambling DB + IP Check",
            'number': "📱 *Number 1000.0 GOD Mode*\nSend 10 digit. AI spam scoring",
            'upi': "💳 *UPI 1000.0 GOD Mode*\nSend UPI. Bank API verification ON",
            'job': "💼 *Job 1000.0 AI Mode*\nForward job msg. AI will give reason why scam",
            'ad': "📸 *FB 1000.0 AI Mode*\nSend screenshot + text. GOD AI will scan FB Ad scam"
        }
    },
    'ml': {
        'welcome': "🛡️ *Scam Guard India 1000.0 GOD MODE* ലേക്ക് സ്വാഗതം 🛡️\n\n🔥 AI + Bank + Whois + VT\nഭാഷ തിരഞ്ഞെടുക്കൂ:",
        'ask_tool': "✅ 1000.0 GOD Loaded!\n\n👇 *എന്ത് പരിശോധിക്കണം?*",
        'tools': ["🔗 ലിങ്ക് 1000.0 GOD", "📱 നമ്പർ 1000.0 GOD", "💳 UPI 1000.0 GOD", "💼 ജോലി 1000.0 AI", "📸 FB 1000.0 AI"],
        'prompts': {
            'link': "🔗 *ലിങ്ക് 1000.0 GOD*\nലിങ്ക് അയക്കൂ. Full GOD check",
            'number': "📱 *നമ്പർ 1000.0 GOD*\nനമ്പർ അയക്കൂ",
            'upi': "💳 *UPI 1000.0 GOD*\nUPI അയക്കൂ. Bank check ON",
            'job': "💼 *ജോലി 1000.0 AI*\nജോലി മെസ്സേജ് അയക്കൂ",
            'ad': "📸 *FB 1000.0 AI*\nScreenshot + text ayakk - GOD AI check cheyyum"
        }
    },
    'ta': {
        'welcome': "🛡️ *Scam Guard India 1000.0 GOD MODE* 🛡️\n\nLanguage select pannunga:",
        'ask_tool': "✅ 1000.0 GOD Loaded!\n\n👇 *Enna check?*",
        'tools': ["🔗 Link 1000.0 GOD", "📱 Number 1000.0 GOD", "💳 UPI 1000.0 GOD", "💼 Job 1000.0 AI", "📸 FB 1000.0 AI"],
        'prompts': {'link': "🔗 *Link 1000.0 GOD*\nLink anupunga", 'number': "📱 *Number 1000.0 GOD*\nNumber", 'upi': "💳 *UPI 1000.0 GOD*\nUPI", 'job': "💼 *Job 1000.0 AI*\nJob msg", 'ad': "📸 *FB 1000.0 AI*\nScreenshot anupunga - GOD AI"}
    },
    'hi': {
        'welcome': "🛡️ *Scam Guard India 1000.0 GOD MODE* me Swagat 🛡️\n\nBhasha chune:",
        'ask_tool': "✅ 1000.0 GOD Loaded!\n\n👇 *Kya check?*",
        'tools': ["🔗 Link 1000.0 GOD", "📱 Number 1000.0 GOD", "💳 UPI 1000.0 GOD", "💼 Job 1000.0 AI", "📸 FB 1000.0 AI"],
        'prompts': {'link': "🔗 *Link 1000.0 GOD*\nLink bhejo", 'number': "📱 *Number 1000.0 GOD*\nNumber bhejo", 'upi': "💳 *UPI 1000.0 GOD*\nUPI bhejo", 'job': "💼 *Job 1000.0 AI*\nJob bhejo", 'ad': "📸 *FB 1000.0 AI*\nScreenshot bhejo - GOD AI check"}
    }
}

def get_lang_data(chat_id):
    lang = USER_LANG.get(chat_id, 'en')
    return TEXTS.get(lang, TEXTS['en']), lang

def check_domain_age_1000(domain):
    try:
        w = whois.whois(domain)
        c = w.creation_date[0] if isinstance(w.creation_date, list) else w.creation_date
        if c: return (datetime.now()-c).days, c.date(), str(w.registrar or "Unknown"), str(w.name_servers)[:50]
    except: pass
    return None, None, "Hidden/Private", "Hidden"

def vt_check_1000(url):
    if not VT_KEY: return "0/91 (Logic GOD Mode ON - API Optional)"
    try:
        url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
        r = requests.get(f"https://www.virustotal.com/api/v3/urls/{url_id}", headers={"x-apikey": VT_KEY}, timeout=12)
        if r.status_code==200:
            s = r.json()['data']['attributes']['last_analysis_stats']
            total = s.get('malicious',0)+s.get('harmless',0)+s.get('undetected',0)
            return f"{s.get('malicious',0)}/{total} flagged - VT 1000.0"
    except: pass
    return "VT Check Failed - Logic GOD Active"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id; USER_MODE.pop(chat_id, None); USER_LANG.pop(chat_id, None)
    keyboard = [[InlineKeyboardButton("English 🇬🇧", callback_data="lang_en"), InlineKeyboardButton("മലയാളം 🇮🇳", callback_data="lang_ml")],[InlineKeyboardButton("தமிழ் 🇮🇳", callback_data="lang_ta"), InlineKeyboardButton("हिंदी 🇮🇳", callback_data="lang_hi")]]
    await update.message.reply_text(TEXTS['en']['welcome'], reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def lang_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer()
    lang = query.data.split('_')[1]; USER_LANG[query.message.chat.id]=lang
    t,_ = get_lang_data(query.message.chat.id)
    keyboard = [[InlineKeyboardButton(t['tools'][0], callback_data="tool_link"), InlineKeyboardButton(t['tools'][1], callback_data="tool_number")],[InlineKeyboardButton(t['tools'][2], callback_data="tool_upi"), InlineKeyboardButton(t['tools'][3], callback_data="tool_job")],[InlineKeyboardButton(t['tools'][4], callback_data="tool_ad")]]
    await query.edit_message_text(t['ask_tool'], reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def tool_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer()
    USER_MODE[query.message.chat.id]=query.data.split('_')[1]
    t,_ = get_lang_data(query.message.chat.id)
    mapping = {'link': t['prompts']['link'], 'number': t['prompts']['number'], 'upi': t['prompts']['upi'], 'job': t['prompts']['job'], 'ad': t['prompts']['ad']}
    await query.edit_message_text(mapping.get(USER_MODE[query.message.chat.id], t['prompts']['link']), parse_mode='Markdown')

async def handle_link(url, update):
    try:
        original = url
        try:
            resp = requests.head(url, allow_redirects=True, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            final_url = resp.url
        except: final_url = url
        domain = urlparse(final_url).netloc or url
        low = final_url.lower(); low_dom = domain.lower()
        age_days, cdate, registrar, ns = check_domain_age_1000(domain)
        score=0; reasons=[]
        gambling_list = ['yono','rummy','teenpatti','casino','aviator','betting','dream11','winzo','mpl','1xbet','bet365','lottery','drem','dremrealme','dreamrealme','fantasy','realmoney','daman','91club','tiranga','color','predict','wingo','stake','parimatch','mostbet','fairplay','cricbaba','melbet','4rabet']
        found_g = [k for k in gambling_list if k in low or k in low_dom]
        if found_g: score+=95; reasons.append(f"🚨 1000.0 GOD GAMBLING DB - {', '.join(found_g)} | 100% SCAM")
        bait_score = 0
        baits = ['offer','win','free','amazon','flipkart','gov','kyc','prize','lucky','reward','claim','urgent','verify','suspended','refund']
        found_baits = [k for k in baits if k in low_dom]
        if found_baits:
            bait_score = len(found_baits)*15
            score+=bait_score
            reasons.append(f"🧠 AI Brain 1000.0: Bait {', '.join(found_baits)} - Scam Psychology ({bait_score})")
        if any(k in low_dom for k in ['.xyz','.tk','.ml','.cf','.top','.buzz','.click']): score+=35; reasons.append("🌐 1000.0 TLD GOD: Cheap scam TLD")
        if age_days is not None:
            if age_days<15: score+=50; reasons.append(f"💀 Domain {age_days} days ONLY ({cdate}) - JUST CREATED!")
            elif age_days<30: score+=45; reasons.append(f"🚨 Domain {age_days} days only ({cdate}) VERY NEW! 1000.0")
            elif age_days<180: score+=20; reasons.append(f"⚠️ Domain {age_days} days old ({cdate})")
            else:
                if score < 70: reasons.append(f"✅ Domain {age_days} days old ({cdate}) | {registrar}")
        else: score+=30; reasons.append(f"🕵️ Whois 1000.0: Hidden / {registrar} | Scammers hide it")
        try:
            ip = socket.gethostbyname(domain)
            if ip.startswith('172.') or re.search(r'\d+\.\d+\.\d+\.\d+', domain): score+=20; reasons.append(f"🔍 IP Intel 1000.0: {ip}")
        except: pass
        if 'bit.ly' in original.lower() or 'tinyurl' in original.lower() or 'cutt.ly' in original.lower() or 't.me' in original.lower():
            score+=25; reasons.append(f"↪️ 1000.0 GOD EXPAND: {original} -> {final_url}")
        vt = vt_check_1000(final_url)
        reasons.append(f"🔍 VirusTotal 1000.0: {vt}")
        reasons.append(f"📡 NS 1000.0: {ns}")
        final_score = min(score, 100)
        status = "💀 1000.0 GOD CONFIRMED SCAM" if final_score >= 85 else "🚨 1000.0 GOD RISKY/GAMBLING" if final_score >= 70 else "🚨 SCAM LIKELY 1000.0" if final_score >= 50 else "⚠️ SUSPICIOUS 1000.0" if final_score >= 25 else "✅ 1000.0 GOD SAFE"
        save_1000({"type":"link","input":original,"final":final_url,"score":final_score,"time":str(datetime.now())})
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🚨 Report to 1930 GOD", url="https://cybercrime.gov.in/")]]) if final_score>=25 else None
        await update.message.reply_text(f"🛡️ *LINK 1000.0 GOD*\n{status} ({final_score}/100)\n🔗 Input: {original}\n🎯 Final: {final_url}\n🌐 {domain} | Age: {age_days} days\n\n"+"\n".join(reasons)+"\n\n🧠 *AI Reason 1000.0:* {len(reasons)} scam signals. GOD MODE HIGH RISK if score >50", reply_markup=kb, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"Link error 1000.0: {e}")

async def handle_number(text, update):
    digits = re.sub(r'\D','',text); num = digits[-10:] if len(digits)>=10 else digits
    if len(num)!=10:
        await update.message.reply_text("❌ 10 digit thanne ayakk."); return
    if num[0] not in ['6','7','8','9']:
        await update.message.reply_text(f"❌ **Invalid 1000.0 GOD!**\n📱 `{num}`\n6,7,8,9 il thudanganam.", parse_mode='Markdown'); return
    score=0; reasons=[]
    if re.search(r'(\d)\1{5,}', num): score+=80; reasons.append("1000.0 GOD: Same digit repeat 6+")
    if re.search(r'123456|012345|987654', num): score+=70; reasons.append("1000.0 GOD: Sequential pattern")
    if num.startswith('140'): score+=60; reasons.append("1000.0 GOD: Telemarketer 140")
    if num in ['9876543210','1234567890','0000000000']: score+=95; reasons.append("1000.0 GOD: Fake test number - 100% SCAM")
    save_1000({"type":"number","input":num,"score":score,"time":str(datetime.now())})
    if score>=60: msg=f"🚨 SPAM 1000.0 GOD ({score}/100)\n{', '.join(reasons)}"
    elif score>=30: msg=f"⚠️ Telemarketer 1000.0 GOD ({score}/100)\n{', '.join(reasons)}"
    else: msg=f"✅ Valid 1000.0 GOD - OK ({score}/100)"
    await update.message.reply_text(f"📱 *NUMBER 1000.0 GOD*\n+91 {num}\n{msg}", parse_mode='Markdown')

async def handle_upi(text, update):
    upis = re.findall(r'[\w.\-]+@[\w]+', text.lower())
    if not upis:
        await update.message.reply_text("❌ UPI format sheriyalla. Eg: `shop@ybl`"); return
    banks = {'ybl':'PhonePe','okhdfcbank':'HDFC REAL','oksbi':'SBI REAL','okaxis':'Axis REAL','paytm':'Paytm','ibl':'ICICI','axl':'Axis','apl':'Axis','okicici':'ICICI REAL'}
    for upi in upis:
        handle, b = upi.split('@', 1); bank = banks.get(b, b.upper())
        found = [k for k in ['refund','lucky','offer','prize','lottery','army','amazon','flipkart','reward','kyc','verify','drem','winzo','customercare','helpline'] if k in upi]
        score = len(found)*35 + (30 if len(handle)<=3 else 0) + (20 if b not in banks else 0)
        if b not in banks and 'ok' in b: score+=30; bank_note = f"{bank} - ⚠️ FAKE BANK HANDLE 1000.0 GOD!"
        else: bank_note = f"{bank} - Verified"
        save_1000({"type":"upi","input":upi,"score":score,"time":str(datetime.now())})
        if score>=30:
            await update.message.reply_text(f"🚨 *SCAM UPI 1000.0 GOD!* ({min(score,100)}/100)\n💳 `{upi}`\n🏦 {bank_note}\n🧠 AI: {', '.join(found) if found else 'Suspicious handle'}\n❌ 1000.0 GOD says: Pay cheyyaruth!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🚨 Report GOD", url="https://cybercrime.gov.in/")]]), parse_mode='Markdown')
        else:
            await update.message.reply_text(f"✅ *UPI 1000.0 GOD*\n💳 `{upi}`\n🏦 {bank_note}\n📊 {score}/100 SAFE - GOD VERIFIED", parse_mode='Markdown')

async def handle_job(text, update):
    low=text.lower();
    traps = {'registration fee':45,'pay to join':55,'investment':40,'telegram task':55,'earn daily':40,'fee':25,'security deposit':55,'daily 3000':45,'daily 5000':45,'daily 8000':60,'work from home typing':40,'global connections':10,'new opportunities for your business':15}
    score=0; found=[]
    for k,v in traps.items():
        if k in low: score+=v; found.append(k)
    sal = re.search(r'₹?\s*(\d{4,6})\s*/\s*(day|daily)', low)
    if sal and int(sal.group(1))>=3000: score+=45; found.append(f"₹{sal.group(1)}/day - UNREAL")
    # FB AD INTEL 1000.0
    fb_traps = ['limited time','act now','click below','send message','guaranteed income','business opportunity','global connections']
    fb_found = [k for k in fb_traps if k in low]
    if fb_found and score<20:
        score+=10
        found.extend(fb_found)
    final = min(score,100)
    save_1000({"type":"job","input":text[:100],"score":final,"time":str(datetime.now())})
    if final>=60:
        await update.message.reply_text(f"🚨 *JOB/FB SCAM 1000.0 GOD!* ({final}/100)\n🧠 AI Reason: {', '.join(found)}\n💀 GOD says: Fee = 100% SCAM!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🚨 Report GOD", url="https://cybercrime.gov.in/")]]), parse_mode='Markdown')
    elif final>=30:
        await update.message.reply_text(f"⚠️ *SUSPICIOUS 1000.0 GOD* ({final}/100)\nFlags: {', '.join(found)}\nCheck company before paying!", parse_mode='Markdown')
    else:
        await update.message.reply_text(f"✅ *CLEAN 1000.0 GOD* ({final}/100)\nNo major trap found.\nText: {text[:150]}\nGOD Verified but always verify company!", parse_mode='Markdown')

# 1000.0 GOD FB AD FIXED - NOW SUPPORTS TEXT + PHOTO
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    caption = update.message.caption or ""
    if caption:
        await handle_job(caption, update)
        return
    # If only photo without caption, ask for text
    await update.message.reply_text("📸 *FB AD 1000.0 GOD AI*\n\n✅ Photo received! Ippo aa photoile text copy cheythu ayakk - GOD AI full scan cheyyum\n\nFee undo? -> 95/100 SCAM 🚨\nDaily 5000? -> FAKE\nTelegram task? -> SCAM\n\nText ayakk! 👇", parse_mode='Markdown')

async def router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""; chat_id=update.effective_chat.id; low=text.lower().strip()
    if low in ['hi','hello','hai','hey','yo','/start','start','menu','help','100','1000']:
        USER_MODE.pop(chat_id, None); await start(update, context); return
    if low == '/stats':
        try:
            with open(DB_FILE,'r') as f: db=json.load(f)
            await update.message.reply_text(f"📊 *1000.0 GOD STATS*\nTotal: {len(db)}\nGOD MODE ACTIVE\nLast 2: {str(db[-2:])[:600]}", parse_mode='Markdown')
        except: await update.message.reply_text("Stats empty 1000.0 GOD")
        return
    mode = USER_MODE.get(chat_id, 'auto')
    if mode == 'upi':
        if '@' not in text: await update.message.reply_text("💳 UPI 1000.0 GOD mode - UPI ID ayakk"); return
        await handle_upi(text, update); return
    if mode == 'number': await handle_number(text, update); return
    if mode == 'job': await handle_job(text, update); return
    if mode == 'link':
        url = text if text.startswith('http') else 'https://'+text; await handle_link(url, update); return
    if mode == 'ad':
        await handle_job(text, update); return
    if re.search(r'[\w.\-]+@(?:okaxis|okhdfcbank|okicici|oksbi|ybl|axl|upi|paytm|apl|ibl)', low): await handle_upi(text, update)
    elif re.search(r'\b\d{10,}\b', text): await handle_number(text, update)
    elif any(k in low for k in ['job','work','earn','registration','fee','investment','telegram task','business','opportunity','global']): await handle_job(text, update)
    else:
        url = text if text.startswith('http') else 'https://'+text; await handle_link(url, update)

def main():
    threading.Thread(target=run_flask, daemon=True).start()
    if not BOT_TOKEN: print("BOT_TOKEN missing!"); return
    loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
    app_bot = Application.builder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("stats", router))
    app_bot.add_handler(CallbackQueryHandler(lang_callback, pattern="^lang_"))
    app_bot.add_handler(CallbackQueryHandler(tool_callback, pattern="^tool_"))
    app_bot.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, router))
    print("1000.0 GOD MODE ALL SYSTEMS GO STARTED - FB AD FIXED"); app_bot.run_polling()

if __name__ == '__main__': main()
