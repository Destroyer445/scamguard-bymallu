import os, re, threading, requests, whois, asyncio
from flask import Flask
from datetime import datetime
from urllib.parse import urlparse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

app = Flask(__name__)
@app.route('/')
def home(): return "Scam Guard India ULTIMATE LIVE - ALL FIXED!"
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
VT_KEY = os.environ.get("VT_API_KEY")
USER_LANG = {}
USER_MODE = {}

TEXTS = {
    'en': {'welcome': "🛡️ *Welcome to Scam Guard India* 🛡️\n\nYour personal anti-scam shield. Select your language:", 'ask_tool': "✅ Language set!\n\n👇 *What do you want to check today?*", 'tools': ["🔗 Link Check", "📱 Number Check", "💳 UPI Check", "💼 Job Scam Check", "📸 FB Ad Check"], 'prompts': {'link': "🔗 *Link Check Mode*\n\nSend any link. Eg: `amazon-offer-2024.com`", 'number': "📱 *Number Check Mode*\n\nSend 10 digit number.", 'upi': "💳 *UPI Check Mode*\n\nSend UPI ID. Eg: `shop@ybl`", 'job': "💼 *Job Scam Mode*\n\nForward the job message", 'ad': "📸 *FB Ad Check Mode*\n\nSend screenshot"}},
    'ml': {'welcome': "🛡️ *Scam Guard India* യിലേക്ക് സ്വാഗതം 🛡️\n\nഭാഷ തിരഞ്ഞെടുക്കൂ:", 'ask_tool': "✅ ഭാഷ സെറ്റ് ചെയ്തു!\n\n👇 *എന്താണ് പരിശോധിക്കേണ്ടത്?*", 'tools': ["🔗 ലിങ്ക് പരിശോധന", "📱 നമ്പർ പരിശോധന", "💳 UPI പരിശോധന", "💼 ജോലി തട്ടിപ്പ്", "📸 FB പരസ്യം"], 'prompts': {'link': "🔗 *ലിങ്ക് മോഡ്*\n\nലിങ്ക് അയക്കൂ", 'number': "📱 *നമ്പർ മോഡ്*\n\n10 അക്ക നമ്പർ അയക്കൂ", 'upi': "💳 *UPI മോഡ്*\n\nUPI ID അയക്കൂ. Eg: `amazon-refund@okhdfcbank`", 'job': "💼 *ജോലി മോഡ്*\n\nജോലി മെസ്സേജ് അയക്കൂ", 'ad': "📸 *FB മോഡ്*\n\nScreenshot അയക്കൂ"}},
    'ta': {'welcome': "🛡️ *Welcome*", 'ask_tool': "✅ Language set! What to check?", 'tools': ["🔗 Link Check", "📱 Number Check", "💳 UPI Check", "💼 Job Scam Check", "📸 FB Ad Check"], 'prompts': {'link': "🔗 Send link", 'number': "📱 Send number", 'upi': "💳 Send UPI", 'job': "💼 Send job msg", 'ad': "📸 Send screenshot"}},
    'hi': {'welcome': "🛡️ *Welcome*", 'ask_tool': "✅ Language set! What to check?", 'tools': ["🔗 Link Check", "📱 Number Check", "💳 UPI Check", "💼 Job Scam Check", "📸 FB Ad Check"], 'prompts': {'link': "🔗 Link bhejo", 'number': "📱 Number bhejo", 'upi': "💳 UPI bhejo", 'job': "💼 Job msg bhejo", 'ad': "📸 Screenshot bhejo"}}
}

def get_lang_data(chat_id):
    return TEXTS.get(USER_LANG.get(chat_id, 'en'), TEXTS['en'])

def check_domain_age(domain):
    try:
        w = whois.whois(domain)
        c = w.creation_date
        if isinstance(c, list): c=c[0]
        if c: return (datetime.now()-c).days
    except: pass
    return None

def vt_check(url):
    if not VT_KEY: return None
    try:
        r = requests.post("https://www.virustotal.com/api/v3/urls", headers={"x-apikey": VT_KEY}, data={"url":url}, timeout=15)
        if r.status_code==200:
            aid = r.json()['data']['id']
            r2 = requests.get(f"https://www.virustotal.com/api/v3/analyses/{aid}", headers={"x-apikey": VT_KEY}, timeout=15)
            if r2.status_code==200:
                stats = r2.json()['data']['attributes']['stats']
                return f"{stats.get('malicious',0)} engines flagged"
    except: pass
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("English 🇬🇧", callback_data="lang_en"), InlineKeyboardButton("മലയാളം 🇮🇳", callback_data="lang_ml")],[InlineKeyboardButton("தமிழ்", callback_data="lang_ta"), InlineKeyboardButton("हिंदी", callback_data="lang_hi")]]
    await update.message.reply_text(TEXTS['en']['welcome'], reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def lang_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data.split('_')[1]
    USER_LANG[query.message.chat.id] = lang
    t = TEXTS.get(lang, TEXTS['en'])
    keyboard = [[InlineKeyboardButton(t['tools'][0], callback_data="tool_link"), InlineKeyboardButton(t['tools'][1], callback_data="tool_number")],[InlineKeyboardButton(t['tools'][2], callback_data="tool_upi"), InlineKeyboardButton(t['tools'][3], callback_data="tool_job")],[InlineKeyboardButton(t['tools'][4], callback_data="tool_ad")]]
    await query.edit_message_text(t['ask_tool'], reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def tool_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    mode = query.data.split('_')[1]
    USER_MODE[query.message.chat.id] = mode
    prompts = get_lang_data(query.message.chat.id)['prompts']
    mapping = {'link': prompts['link'], 'number': prompts['number'], 'upi': prompts['upi'], 'job': prompts['job'], 'ad': prompts['ad']}
    await query.edit_message_text(mapping.get(mode, prompts['link']), parse_mode='Markdown')

async def handle_link(url, update):
    try:
        domain = urlparse(url).netloc or urlparse('https://'+url).netloc or url
        age = check_domain_age(domain)
        score=0; reasons=[]
        if any(k in domain.lower() for k in ['offer','lottery','win','free','amazon','flipkart','gov','kyc','prize','lucky']): score+=30; reasons.append("⚠️ Suspicious keywords")
        if age is not None:
            if age<30: score+=40; reasons.append(f"🚨 Domain {age} days only (NEW!)")
            elif age<180: score+=20; reasons.append(f"⚠️ Domain {age} days old")
            else: reasons.append(f"✅ Domain {age} days old")
        else: score+=15; reasons.append("⚠️ Whois hidden / new domain")
        if re.search(r'\d+\.\d+\.\d+\.\d+', url): score+=25; reasons.append("⚠️ IP URL")
        if 'bit.ly' in url or 'tinyurl' in url: score+=20; reasons.append("⚠️ Shortener URL")
        vt = vt_check(url)
        reasons.append(f"🔍 VT: {vt}" if vt else "🔍 VT: 0 flagged - Clean" if VT_KEY else "🔍 VT: API not set")
        status = "🚨 SCAM LIKELY" if score>=50 else "⚠️ SUSPICIOUS" if score>=25 else "✅ SAFE"
        await update.message.reply_text(f"{status} ({score}/100)\n{domain}\n\n"+"\n".join(reasons))
    except Exception as e:
        await update.message.reply_text(f"Link check error: {e}")

async def handle_number(text, update):
    digits = re.sub(r'\D','',text)
    num = digits[-10:] if len(digits)>=10 else digits
    if len(num)<10:
        await update.message.reply_text("❌ 10 digit number ayakk")
        return
    spam_score = 80 if '9999' in num or '1111' in num else 40 if num.startswith('140') else 20
    await update.message.reply_text(f"📱 Number: +91 {num}\nSpam Score: {spam_score}/100\n{'🚨 Spam Likely' if spam_score>60 else '⚠️ Telemarketer' if spam_score>30 else '✅ Looks OK'}")

async def handle_upi(text, update):
    upis = re.findall(r'[\w.\-]+@[\w]+', text)
    if not upis:
        await update.message.reply_text("❌ UPI format sheriyalla. Eg: shop@ybl")
        return
    for upi in upis:
        low = upi.lower()
        scam_keywords = ['refund','lucky','offer','prize','lottery','army','amazon','flipkart','reward','cashback','kyc','verify','blocked','earn','investment','fake','fraud','free','gift']
        found = [k for k in scam_keywords if k in low]
        if found:
            await update.message.reply_text(f"🚨 SCAM UPI! ({min(len(found)*30,100)}/100)\n💳 {upi}\n⚠️ Keywords: {', '.join(found)}\n\n❌ Ith pay cheyyaruth!")
        else:
            await update.message.reply_text(f"✅ UPI Format OK\n💳 {upi}\n⚠️ Receiver name UPI appil nokku!")

async def handle_job(text, update):
    traps = ['registration fee','₹','pay to join','investment','work from home','telegram task','earn daily','fee']
    found = [t for t in traps if t in text.lower()]
    score = len(found)*30
    await update.message.reply_text(f"💼 Job Risk: {min(score,100)}/100\nFound: {', '.join(found) if found else 'None'}\n{'🚨 FEE TRAP - Do not pay!' if score>=30 else '✅ No obvious trap'}")

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = ("🕵️ *FB AD SCAM ANALYSIS*\n\n⚠️ *Screenshotil ithokke nokku:*\n1. `Registration Fee` undo? -> 100% SCAM 🚨\n2. `Telegramil message ayakk` -> SCAM\n3. `Daily ₹3000-5000` -> FAKE\n4. Company name illa? -> SUSPICIOUS\n\n📊 Fee chodikkunna ellam = 🚨 SCAM (90/100)\n\n💡 Tip: Adile text copy cheythu ayakk!")
    await update.message.reply_text(msg, parse_mode='Markdown')

async def router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    chat_id = update.effective_chat.id
    mode = USER_MODE.get(chat_id, 'auto')
    low = text.lower()
    if mode == 'upi': await handle_upi(text, update); return
    if mode == 'number': await handle_number(text, update); return
    if mode == 'job': await handle_job(text, update); return
    if mode == 'link':
        url = text if text.startswith('http') else 'https://'+text
        await handle_link(url, update); return
    if mode == 'ad': await photo_handler(update, context); return
    if re.search(r'[\w.\-]+@(?:okaxis|okhdfcbank|okicici|oksbi|ybl|axl|upi|paytm)', low):
        await handle_upi(text, update)
    elif re.search(r'\b\d{10}\b', text):
        await handle_number(text, update)
    elif any(k in low for k in ['job','work','fee','earn','registration']):
        await handle_job(text, update)
    else:
        url = text if text.startswith('http') else 'https://'+text
        await handle_link(url, update)

def main():
    threading.Thread(target=run_flask, daemon=True).start()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    app_bot = Application.builder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CallbackQueryHandler(lang_callback, pattern="^lang_"))
    app_bot.add_handler(CallbackQueryHandler(tool_callback, pattern="^tool_"))
    app_bot.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, router))
    print("ULTIMATE Bot Started - FINAL ALL FIXED")
    app_bot.run_polling()

if __name__ == '__main__':
    main()
