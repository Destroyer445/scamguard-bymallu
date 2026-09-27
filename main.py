import os, re, threading, requests, whois, asyncio, base64
from flask import Flask
from datetime import datetime
from urllib.parse import urlparse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

app = Flask(__name__)
@app.route('/')
def home():
    return "Scam Guard India 5.0 FINAL - ALL TOOLS LATEST"
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
VT_KEY = os.environ.get("VT_API_KEY")
USER_LANG = {}
USER_MODE = {}

TEXTS = {
    'en': {'welcome': "🛡️ *Welcome to Scam Guard India* 🛡️\n\nYour personal anti-scam shield. Select your language:", 'ask_tool': "✅ Language set!\n\n👇 *What do you want to check today?*", 'tools': ["🔗 Link Check", "📱 Number Check", "💳 UPI Check", "💼 Job Scam Check", "📸 FB Ad Check"], 'prompts': {'link': "🔗 *Link Check Mode*\n\nSend any link. Eg: `amazon-offer-2024.com`", 'number': "📱 *Number Check Mode*\n\nSend 10 digit mobile number. Must start with 6-9", 'upi': "💳 *UPI Check Mode*\n\nSend UPI ID. Eg: `shop@ybl`", 'job': "💼 *Job Scam Mode*\n\nForward the job message", 'ad': "📸 *FB Ad Check Mode*\n\nSend FB Job Ad screenshot"}},
    'ml': {'welcome': "🛡️ *Scam Guard India* യിലേക്ക് സ്വാഗതം 🛡️\n\nനിങ്ങളുടെ സ്വകാര്യ സ്കാം ഷീൽഡ്. ഭാഷ തിരഞ്ഞെടുക്കൂ:", 'ask_tool': "✅ ഭാഷ സെറ്റ് ചെയ്തു!\n\n👇 *എന്താണ് പരിശോധിക്കേണ്ടത്?*", 'tools': ["🔗 ലിങ്ക് പരിശോധന", "📱 നമ്പർ പരിശോധന", "💳 UPI പരിശോധന", "💼 ജോലി തട്ടിപ്പ്", "📸 FB പരസ്യം"], 'prompts': {'link': "🔗 *ലിങ്ക് മോഡ്*\n\nലിങ്ക് അയക്കൂ.", 'number': "📱 *നമ്പർ മോഡ്*\n\n10 അക്ക നമ്പർ അയക്കൂ. 6-9 il thudanganam", 'upi': "💳 *UPI മോഡ്*\n\nUPI ID അയക്കൂ.", 'job': "💼 *ജോലി മോഡ്*\n\nജോലി മെസ്സേജ് അയക്കൂ", 'ad': "📸 *FB മോഡ്*\n\nScreenshot അയക്കൂ"}},
    'ta': {'welcome': "🛡️ *Scam Guard India* ku Varaverppu 🛡️\n\nLanguage select pannunga:", 'ask_tool': "✅ Language set!\n\n👇 *Enna check pannanum?*", 'tools': ["🔗 Link Check", "📱 Number Check", "💳 UPI Check", "💼 Job Check", "📸 FB Ad Check"], 'prompts': {'link': "🔗 *Link Mode*\n\nLink anupunga", 'number': "📱 *Number Mode*\n\n10 digit anupunga", 'upi': "💳 *UPI Mode*\n\nUPI anupunga", 'job': "💼 *Job Mode*\n\nJob anupunga", 'ad': "📸 *FB Mode*\n\nScreenshot anupunga"}},
    'hi': {'welcome': "🛡️ *Scam Guard India* me Swagat Hai 🛡️\n\nBhasha chune:", 'ask_tool': "✅ Bhasha set ho gayi!\n\n👇 *Kya check karna hai?*", 'tools': ["🔗 Link Check", "📱 Number Check", "💳 UPI Check", "💼 Job Check", "📸 FB Ad Check"], 'prompts': {'link': "🔗 *Link Mode*\n\nLink bhejo", 'number': "📱 *Number Mode*\n\n10 digit bhejo", 'upi': "💳 *UPI Mode*\n\nUPI bhejo", 'job': "💼 *Job Mode*\n\nJob bhejo", 'ad': "📸 *FB Mode*\n\nScreenshot bhejo"}}
}

# NINTE STYLE VECHU FIXED LANGUAGE FUNCTION
def get_lang_data(chat_id):
    lang = USER_LANG.get(chat_id, 'en')
    return TEXTS.get(lang, TEXTS['en']), lang

def check_domain_age_5(domain):
    try:
        w = whois.whois(domain)
        c = w.creation_date[0] if isinstance(w.creation_date, list) else w.creation_date
        if c: return (datetime.now()-c).days, c.date(), str(w.registrar or "Unknown")
    except: pass
    return None, None, "Hidden"

def vt_check_5(url):
    if not VT_KEY: return None
    try:
        url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")
        r = requests.get(f"https://www.virustotal.com/api/v3/urls/{url_id}", headers={"x-apikey": VT_KEY}, timeout=10)
        if r.status_code==200:
            s = r.json()['data']['attributes']['last_analysis_stats']
            return f"{s.get('malicious',0)}/{s.get('malicious',0)+s.get('harmless',0)} flagged"
    except: pass
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id; USER_MODE.pop(chat_id, None); USER_LANG.pop(chat_id, None)
    keyboard = [[InlineKeyboardButton("English 🇬🇧", callback_data="lang_en"), InlineKeyboardButton("മലയാളം 🇮🇳", callback_data="lang_ml")],[InlineKeyboardButton("தமிழ்", callback_data="lang_ta"), InlineKeyboardButton("हिंदी 🇮🇳", callback_data="lang_hi")]]
    await update.message.reply_text(TEXTS['en']['welcome'], reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def lang_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer()
    lang = query.data.split('_')[1]; USER_LANG[query.message.chat.id]=lang; USER_MODE.pop(query.message.chat.id, None)
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
            resp = requests.head(url, allow_redirects=True, timeout=10)
            final_url = resp.url; redirects = len(resp.history)
        except:
            final_url = url; redirects = 0
        domain = urlparse(final_url).netloc or url
        low = final_url.lower(); low_dom = domain.lower()
        age_days, cdate, registrar = check_domain_age_5(domain)
        score=0; reasons=[]
        gambling_list = ['yono', 'rummy', 'teenpatti', 'casino', 'aviator', 'betting', 'dream11', 'winzo', 'mpl', '1xbet', 'bet365', 'lottery']
        found_g = [k for k in gambling_list if k in low or k in low_dom]
        if found_g: score+=90; reasons.append(f"🚨 GAMBLING/BETTING - {', '.join(found_g)}")
        if any(k in low_dom for k in ['offer','win','free','amazon','flipkart','gov','kyc','prize','lucky']): score+=30; reasons.append("⚠️ Suspicious keywords")
        if age_days is not None:
            if age_days<30: score+=40; reasons.append(f"🚨 Domain {age_days} days only ({cdate}) VERY NEW!")
            elif age_days<180: score+=20; reasons.append(f"⚠️ Domain {age_days} days old ({cdate})")
            else:
                if score < 70: reasons.append(f"✅ Domain {age_days} days old ({cdate}) {registrar}")
        else: score+=15; reasons.append(f"⚠️ Whois hidden / {registrar}")
        if re.search(r'\d+\.\d+\.\d+\.\d+', final_url): score+=25; reasons.append("⚠️ IP based URL")
        if 'bit.ly' in original.lower() or 'tinyurl' in original.lower(): score+=15; reasons.append(f"↪️ Shortener: {original} -> {final_url}")
        vt = vt_check_5(final_url)
        if vt: reasons.append(f"🔍 VirusTotal: {vt}")
        final_score = min(score, 100)
        status = "🚨 RISKY / GAMBLING TRAP" if final_score >= 70 else "🚨 SCAM LIKELY" if final_score >= 50 else "⚠️ SUSPICIOUS" if final_score >= 25 else "✅ SAFE"
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🚨 Report", url="https://cybercrime.gov.in/")]]) if final_score>=25 else None
        await update.message.reply_text(f"🛡️ *LINK 5.0*\n{status} ({final_score}/100)\n🔗 {original}\n🎯 {final_url}\n🌐 {domain} | Age: {age_days} days\n\n"+"\n".join(reasons), reply_markup=kb, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"Link error: {e}")

async def handle_number(text, update):
    digits = re.sub(r'\D','',text); num = digits[-10:] if len(digits)>=10 else digits
    if len(num)!=10:
        await update.message.reply_text("❌ 10 digit number thanne ayakk."); return
    if num[0] not in ['6','7','8','9']:
        await update.message.reply_text(f"❌ **Invalid Mobile 5.0!**\n📱 `{num}`\n6,7,8,9 il thudanganam.", parse_mode='Markdown'); return
    score=0; reasons=[]
    if re.search(r'(\d)\1{5,}', num): score+=80; reasons.append("Same digit repeat 6+")
    if re.search(r'123456|012345|987654', num): score+=70; reasons.append("Sequential pattern")
    if num.startswith('140'): score+=60; reasons.append("Telemarketer 140")
    if num in ['9876543210','1234567890','0000000000']: score+=90; reasons.append("Fake test number")
    if score>=60: msg=f"🚨 SPAM / FAKE 5.0 ({score}/100)\n{', '.join(reasons)}"
    elif score>=30: msg=f"⚠️ Telemarketer? 5.0 ({score}/100)\n{', '.join(reasons)}"
    else: msg=f"✅ Valid Mobile 5.0 - Looks OK ({score}/100)"
    await update.message.reply_text(f"📱 *NUMBER 5.0*\n+91 {num}\n{msg}", parse_mode='Markdown')

async def handle_upi(text, update):
    upis = re.findall(r'[\w.\-]+@[\w]+', text.lower())
    if not upis:
        await update.message.reply_text("❌ UPI format sheriyalla. Eg: `shop@ybl`"); return
    banks = {'ybl':'PhonePe','okhdfcbank':'HDFC','oksbi':'SBI','okaxis':'Axis','paytm':'Paytm','ibl':'ICICI','axl':'Axis'}
    for upi in upis:
        handle, b = upi.split('@', 1)
        bank = banks.get(b, b.upper())
        found = [k for k in ['refund','lucky','offer','prize','lottery','army','amazon','flipkart','reward','kyc','verify'] if k in upi]
        score = len(found)*30
        if len(handle)<=3: score+=25
        if score>=30:
            await update.message.reply_text(f"🚨 *SCAM UPI 5.0!* ({min(score,100)}/100)\n💳 `{upi}`\nBank: {bank}\n⚠️ {', '.join(found)}\n❌ Pay cheyyaruth!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🚨 Report UPI", url="https://cybercrime.gov.in/")]]), parse_mode='Markdown')
        else:
            await update.message.reply_text(f"✅ *UPI 5.0*\n💳 `{upi}`\nBank: {bank}\n📊 {score}/100 SAFE", parse_mode='Markdown')

async def handle_job(text, update):
    low=text.lower(); traps = {'registration fee':40,'pay to join':50,'investment':35,'telegram task':50,'earn daily':35,'fee':20,'security deposit':50,'daily 3000':40,'daily 5000':40}
    score=0; found=[]
    for k,v in traps.items():
        if k in low: score+=v; found.append(k)
    sal = re.search(r'₹?\s*(\d{4,6})\s*/\s*(day|daily)', low)
    if sal and int(sal.group(1))>=3000: score+=40; found.append(f"₹{sal.group(1)}/day")
    final = min(score,100)
    if final>=60: await update.message.reply_text(f"🚨 *JOB SCAM 5.0!* ({final}/100)\nFlags: {', '.join(found)}\n❌ Fee = SCAM!", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🚨 Report", url="https://cybercrime.gov.in/")]]), parse_mode='Markdown')
    elif final>=30: await update.message.reply_text(f"⚠️ *SUSPICIOUS JOB 5.0* ({final}/100)\nFlags: {', '.join(found)}", parse_mode='Markdown')
    else: await update.message.reply_text(f"✅ *JOB 5.0*\nNo trap ({final}/100)\nVerify company!", parse_mode='Markdown')

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    _, lang = get_lang_data(update.effective_chat.id)
    msg = "📸 *FB AD 5.0*\n\nFee undo? -> 90/100 SCAM 🚨\nDaily 3000? -> FAKE\nTelegram? -> SCAM\n\nText copy cheythu ayakk!" if lang=='ml' else "🕵️ *FB AD 5.0*\n\nFee? -> 90/100 SCAM\nDaily 3000-5000? -> FAKE\nTelegram? -> SCAM\nNo company? -> SUS\n\nPaste text!"
    await update.message.reply_text(msg, parse_mode='Markdown')

async def router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""; chat_id=update.effective_chat.id; low=text.lower().strip()
    if low in ['hi','hello','hai','hey','yo','/start','start','menu','help']:
        USER_MODE.pop(chat_id, None); await start(update, context); return
    mode = USER_MODE.get(chat_id, 'auto')
    if mode == 'upi':
        if '@' not in text: await update.message.reply_text("💳 UPI modeil aanu. UPI ID ayakk."); return
        await handle_upi(text, update); return
    if mode == 'number': await handle_number(text, update); return
    if mode == 'job': await handle_job(text, update); return
    if mode == 'link':
        url = text if text.startswith('http') else 'https://'+text; await handle_link(url, update); return
    if mode == 'ad': await photo_handler(update, context); return
    if re.search(r'[\w.\-]+@(?:okaxis|okhdfcbank|okicici|oksbi|ybl|axl|upi|paytm|apl|ibl)', low): await handle_upi(text, update)
    elif re.search(r'\b\d{10,}\b', text): await handle_number(text, update)
    elif any(k in low for k in ['job','work','earn','registration','fee','investment','telegram task']): await handle_job(text, update)
    else:
        url = text if text.startswith('http') else 'https://'+text; await handle_link(url, update)

def main():
    threading.Thread(target=run_flask, daemon=True).start()
    if not BOT_TOKEN: print("BOT_TOKEN missing!"); return
    loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
    app_bot = Application.builder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CallbackQueryHandler(lang_callback, pattern="^lang_"))
    app_bot.add_handler(CallbackQueryHandler(tool_callback, pattern="^tool_"))
    app_bot.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, router))
    print("ALL TOOLS 5.0 FINAL - Language Fixed Started"); app_bot.run_polling()

if __name__ == '__main__': main()
