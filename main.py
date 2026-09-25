import os, re, threading, requests, whois, asyncio
from flask import Flask
from datetime import datetime
from urllib.parse import urlparse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

app = Flask(__name__)
@app.route('/')
def home(): return "Scam Guard India - FULL ML TA HI FIXED"
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
VT_KEY = os.environ.get("VT_API_KEY")
USER_LANG = {}
USER_MODE = {}

TEXTS = {
    'en': {
        'welcome': "🛡️ *Scam Guard India* 🛡️\n\nYour anti-scam shield. Select language:",
        'ask_tool': "✅ Language: English\n\n👇 *What to check?*",
        'tools': ["🔗 Link", "📱 Number", "💳 UPI", "💼 Job", "📸 FB Ad"],
        'prompts': {
            'link': "🔗 *Link Mode*\nSend link. Eg: `lottery-kerala-win.com`",
            'number': "📱 *Number Mode*\nSend 10-digit number. Eg: `9999999999`",
            'upi': "💳 *UPI Mode*\nSend UPI. Eg: `lottery@ybl`",
            'job': "💼 *Job Mode*\nForward job message",
            'ad': "📸 *FB Ad Mode*\nSend screenshot + caption text also"
        }
    },
    'ml': {
        'welcome': "🛡️ *സ്കാം ഗാർഡ് ഇന്ത്യ* 🛡️\n\nനിങ്ങളുടെ തട്ടിപ്പ് പരിശോധകൻ. ഭാഷ തിരഞ്ഞെടുക്കൂ:",
        'ask_tool': "✅ ഭാഷ: മലയാളം\n\n👇 *എന്ത് പരിശോധിക്കണം?*",
        'tools': ["🔗 ലിങ്ക്", "📱 നമ്പർ", "💳 UPI", "💼 ജോലി", "📸 FB പരസ്യം"],
        'prompts': {
            'link': "🔗 *ലിങ്ക് മോഡ്*\nലിങ്ക് അയക്കൂ. Eg: `lottery-kerala-win.com`",
            'number': "📱 *നമ്പർ മോഡ്*\n10 അക്ക നമ്പർ അയക്കൂ. Eg: `9999999999`",
            'upi': "💳 *UPI മോഡ്*\nUPI അയക്കൂ. Eg: `lottery@ybl`",
            'job': "💼 *ജോലി മോഡ്*\nജോലി മെസ്സേജ് forward ചെയ്യൂ",
            'ad': "📸 *FB പരസ്യ മോഡ്*\nScreenshot + അതിലെ എഴുത്തും അയക്കൂ"
        },
        'result_link': "🔍 ലിങ്ക് ഫലം", 'result_num': "🔍 നമ്പർ ഫലം", 'result_upi': "🔍 UPI ഫലം", 'result_job': "🔍 ജോലി ഫലം", 'result_ad': "🔍 പരസ്യ ഫലം"
    },
    'ta': {
        'welcome': "🛡️ *Scam Guard India* 🛡️\n\nஉங்கள் மோசடி பாதுகாப்பு. மொழியைத் தேர்ந்தெடுக்கவும்:",
        'ask_tool': "✅ மொழி: தமிழ்\n\n👇 *என்ன சரிபார்க்க வேண்டும்?*",
        'tools': ["🔗 இணைப்பு", "📱 எண்", "💳 UPI", "💼 வேலை", "📸 FB விளம்பரம்"],
        'prompts': {
            'link': "🔗 *இணைப்பு முறை*\nஇணைப்பை அனுப்பவும்",
            'number': "📱 *எண் முறை*\n10 இலக்க எண்ணை அனுப்பவும்",
            'upi': "💳 *UPI முறை*\nUPI அனுப்பவும்",
            'job': "💼 *வேலை முறை*\nவேலை செய்தியை அனுப்பவும்",
            'ad': "📸 *FB விளம்பர முறை*\nஸ்கிரீன்ஷாட் அனுப்பவும்"
        },
        'result_link': "🔍 இணைப்பு முடிவு", 'result_num': "🔍 எண் முடிவு", 'result_upi': "🔍 UPI முடிவு", 'result_job': "🔍 வேலை முடிவு", 'result_ad': "🔍 விளம்பர முடிவு"
    },
    'hi': {
        'welcome': "🛡️ *Scam Guard India* 🛡️\n\nआपका स्कैम सुरक्षा कवच। भाषा चुनें:",
        'ask_tool': "✅ भाषा: हिंदी\n\n👇 *क्या जांचना है?*",
        'tools': ["🔗 लिंक", "📱 नंबर", "💳 UPI", "💼 नौकरी", "📸 FB विज्ञापन"],
        'prompts': {
            'link': "🔗 *लिंक मोड*\nलिंक भेजें",
            'number': "📱 *नंबर मोड*\n10 अंकों का नंबर भेजें",
            'upi': "💳 *UPI मोड*\nUPI भेजें",
            'job': "💼 *नौकरी मोड*\nनौकरी मैसेज भेजें",
            'ad': "📸 *FB विज्ञापन मोड*\nस्क्रीनशॉट भेजें"
        },
        'result_link': "🔍 लिंक परिणाम", 'result_num': "🔍 नंबर परिणाम", 'result_upi': "🔍 UPI परिणाम", 'result_job': "🔍 नौकरी परिणाम", 'result_ad': "🔍 विज्ञापन परिणाम"
    }
}

def get_lang(chat_id):
    return USER_LANG.get(chat_id, 'en')

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
        r = requests.post("https://www.virustotal.com/api/v3/urls", headers={"x-apikey": VT_KEY}, data={"url":url}, timeout=10)
        if r.status_code==200:
            id = r.json()['data']['id']
            r2 = requests.get(f"https://www.virustotal.com/api/v3/analyses/{id}", headers={"x-apikey": VT_KEY}, timeout=10)
            stats = r2.json()['data']['attributes']['stats']
            return stats['malicious']
    except: return None
    return None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("English 🇬🇧", callback_data="lang_en"),
         InlineKeyboardButton("മലയാളം 🇮🇳", callback_data="lang_ml")],
        [InlineKeyboardButton("தமிழ்", callback_data="lang_ta"),
         InlineKeyboardButton("हिंदी", callback_data="lang_hi")]
    ]
    await update.message.reply_text(TEXTS['en']['welcome'], reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def lang_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data.split('_')[1]
    USER_LANG[query.message.chat.id] = lang
    t = TEXTS.get(lang, TEXTS['en'])
    keyboard = [
        [InlineKeyboardButton(t['tools'][0], callback_data="tool_link"), InlineKeyboardButton(t['tools'][1], callback_data="tool_number")],
        [InlineKeyboardButton(t['tools'][2], callback_data="tool_upi"), InlineKeyboardButton(t['tools'][3], callback_data="tool_job")],
        [InlineKeyboardButton(t['tools'][4], callback_data="tool_ad")]
    ]
    await query.edit_message_text(t['ask_tool'], reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def tool_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    mode = query.data.split('_')[1]
    chat_id = query.message.chat.id
    USER_MODE[chat_id] = mode
    lang = get_lang(chat_id)
    prompts = TEXTS.get(lang, TEXTS['en'])['prompts']
    prompt_map = {'link': prompts['link'], 'number': prompts['number'], 'upi': prompts['upi'], 'job': prompts['job'], 'ad': prompts['ad']}
    await query.edit_message_text(prompt_map.get(mode, prompts['link']), parse_mode='Markdown')

async def handle_link(url, update):
    lang = get_lang(update.effective_chat.id)
    domain = urlparse(url).netloc or urlparse('https://'+url).netloc
    if not domain: domain=url
    age = check_domain_age(domain)
    score=0; reasons=[]
    scam_keywords = ['offer','lottery','win','free','amazon','flipkart','gov','kyc','prize','claim','bonus']
    if any(k in domain.lower() for k in scam_keywords): score+=35; reasons.append("⚠️ തട്ടിപ്പ് വാക്കുകൾ ഉണ്ട് / Suspicious keywords")
    if re.search(r'(.)\1{4,}', domain): score+=40; reasons.append("⚠️ Repeated chars - spam pattern")
    if age is not None:
        if age<30: score+=40; reasons.append(f"🚨 {age} ദിവസം മാത്രം പഴക്കം / Only {age} days old!")
        elif age<180: score+=20; reasons.append(f"⚠️ {age} ദിവസം പഴക്കം / {age} days")
        else: reasons.append(f"✅ {age} ദിവസം പഴക്കം / {age} days old")
    else:
        score+=20; reasons.append("⚠️ Whois മറച്ചിരിക്കുന്നു / Hidden")
    if re.search(r'\d+\.\d+\.\d+\.\d+', url): score+=30
    if 'bit.ly' in url or 'tinyurl' in url or '@' in url: score+=20; reasons.append("⚠️ Short link / മറച്ച ലിങ്ക്")
    vt = vt_check(url)
    if vt and vt>0: score+=vt*5; reasons.append(f"🔍 VirusTotal: {vt} engines flagged 🚨")

    status = "🚨 SCAM LIKELY / തട്ടിപ്പ് സാധ്യത!" if score>=50 else "⚠️ SUSPICIOUS / സംശയകരം" if score>=25 else "✅ SAFE / സുരക്ഷിതം"
    head = TEXTS.get(lang, TEXTS['en']).get('result_link','Result')
    await update.message.reply_text(f"{head}\n{status} ({score}/100)\n{domain}\n\n"+"\n".join(reasons))

async def handle_number(text, update):
    lang = get_lang(update.effective_chat.id)
    num = re.sub(r'\D','',text)[-10:]
    if not num: return
    score=0; reasons=[]
    # STRONG SPAM LOGIC
    if re.search(r'(.)\1{5,}', num): score+=80; reasons.append("🚨 6+ same digits - 100% spam pattern!")
    if num in ['9999999999','8888888888','7777777777','1234567890','0000000000']: score+=90; reasons.append("🚨 Famous fake/spam number!")
    if re.search(r'^(.)\1{3,}', num) or num.count(num[0])>=7: score+=70; reasons.append("🚨 Repeated digits")
    if num.startswith('140'): score+=50; reasons.append("⚠️ Telemarketer series (140)")
    if re.search(r'12345|54321|9999|8888|7777', num): score+=40; reasons.append("⚠️ Sequential / spam pattern")

    status = "🚨 SPAM LIKELY / സ്പാം!" if score>=50 else "⚠️ TELEMARKETER / ടെലിമാർക്കറ്റർ" if score>=25 else "✅ Looks OK / കുഴപ്പമില്ല"
    head = TEXTS.get(lang, TEXTS['en']).get('result_num','Number Result')
    await update.message.reply_text(f"{head}\n📱 +91 {num}\n{status} ({score}/100)\n\n"+"\n".join(reasons) if reasons else f"{head}\n📱 +91 {num}\n{status} ({score}/100)")

async def handle_upi(text, update):
    lang = get_lang(update.effective_chat.id)
    upis = re.findall(r'[\w.-]+@[\w]+', text)
    for upi in upis:
        score=0
        if any(x in upi.lower() for x in ['lottery','offer','prize','win','cashback']): score+=60
        if len(upi.split('@')[0])<3: score+=20
        status = "🚨 SCAM UPI!" if score>=40 else "⚠️ Check name" if score>=20 else "✅ Format OK"
        await update.message.reply_text(f"💳 UPI: {upi}\n{status} ({score}/100)")

async def handle_job(text, update):
    lang = get_lang(update.effective_chat.id)
    traps = ['registration fee','₹','pay to join','investment','work from home','telegram task','earn daily','fees','deposit']
    found = [t for t in traps if t in text.lower()]
    score = len(found)*35
    await update.message.reply_text(f"💼 Job Risk: {score}/100\nFound: {', '.join(found) if found else 'None'}\n{'🚨 FEE TRAP - Do not pay! / പണം കൊടുക്കരുത്!' if score>=30 else '✅ OK'}")

async def router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    chat_id = update.effective_chat.id
    mode = USER_MODE.get(chat_id, 'auto')
    if mode == 'number' or (text.replace(' ','').isdigit() and len(re.sub(r'\D','',text))>=10):
        await handle_number(text, update)
    elif mode == 'upi' or '@ybl' in text or '@okaxis' in text or '@paytm' in text:
        await handle_upi(text, update)
    elif mode == 'job' or any(k in text.lower() for k in ['job','work','fee','earn','registration']):
        await handle_job(text, update)
    elif mode == 'ad':
        await update.message.reply_text("📸 FB Ad check: Send screenshot + type the text in ad. I will check for 'earn daily', 'registration fee' traps.")
    else:
        url = text if text.startswith('http') else 'https://'+text
        await handle_link(url, update)

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(update.effective_chat.id)
    # Improved FB check
    msg = "📸 *FB Ad Analysis:*\n\n" if lang=='en' else "📸 *FB പരസ്യ വിശകലനം:*\n\n"
    msg += "1. 'Earn ₹5000 daily' ഉണ്ടോ? -> MLM Trap 🚨\n2. Registration fee ചോദിക്കുന്നുണ്ടോ? -> Scam 🚨\n3. WhatsAppil മാത്രം contact? -> Suspicious ⚠️\n\nദയവായി പരസ്യത്തിലെ എഴുത്ത് കൂടി ടൈപ്പ് ചെയ്ത് അയക്കൂ, ഞാൻ full check ചെയ്യാം!"
    await update.message.reply_text(msg, parse_mode='Markdown')

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
    print("Bot Started - FULL ML TA HI + SPAM FIXED")
    app_bot.run_polling()

if __name__ == '__main__':
    main()
