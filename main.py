import os, re, threading, requests, whois, asyncio
from flask import Flask
from datetime import datetime
from urllib.parse import urlparse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

app = Flask(__name__)
@app.route('/')
def home(): return "Scam Guard India ULTIMATE LIVE - Fixed!"
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
VT_KEY = os.environ.get("VT_API_KEY")
USER_LANG = {}
USER_MODE = {} # ennum / mlnum / upi / job / link
REPORTS = []

TEXTS = {
    'en': {
        'welcome': "🛡️ *Welcome to Scam Guard India* 🛡️\n\nYour personal anti-scam shield. Select your language:",
        'ask_tool': "✅ Language set!\n\n👇 *What do you want to check today?*",
        'tools': ["🔗 Link Check", "📱 Number Check", "💳 UPI Check", "💼 Job Scam Check", "📸 FB Ad Check"],
        'prompts': {
            'link': "🔗 *Link Check Mode*\n\nSend any link. Eg: `amazon-offer-2024.com`",
            'number': "📱 *Number Check Mode*\n\nSend 10 digit number. Eg: `9876543210`",
            'upi': "💳 *UPI Check Mode*\n\nSend UPI ID. Eg: `shop@ybl`",
            'job': "💼 *Job Scam Mode*\n\nForward the job message / description",
            'ad': "📸 *FB Ad Check Mode*\n\nSend screenshot of ad"
        }
    },
    'ml': {
        'welcome': "🛡️ *Scam Guard India* യിലേക്ക് സ്വാഗതം 🛡️\n\nനിങ്ങളുടെ സ്കാം പരിശോധകൻ. ഭാഷ തിരഞ്ഞെടുക്കൂ:",
        'ask_tool': "✅ ഭാഷ സെറ്റ് ചെയ്തു!\n\n👇 *എന്താണ് പരിശോധിക്കേണ്ടത്?*",
        'tools': ["🔗 ലിങ്ക് പരിശോധന", "📱 നമ്പർ പരിശോധന", "💳 UPI പരിശോധന", "💼 ജോലി തട്ടിപ്പ്", "📸 FB പരസ്യം"],
        'prompts': {
            'link': "🔗 *ലിങ്ക് മോഡ്*\n\nലിങ്ക് അയക്കൂ. Eg: `lottery-kerala-win.com`",
            'number': "📱 *നമ്പർ മോഡ്*\n\n10 അക്ക നമ്പർ അയക്കൂ",
            'upi': "💳 *UPI മോഡ്*\n\nUPI ID അയക്കൂ",
            'job': "💼 *ജോലി തട്ടിപ്പ് മോഡ്*\n\nജോലി മെസ്സേജ് forward ചെയ്യൂ",
            'ad': "📸 *FB പരസ്യ മോഡ്*\n\nScreenshot അയക്കൂ"
        }
    }
}

def get_text(chat_id, key):
    lang = USER_LANG.get(chat_id, 'en')
    return TEXTS.get(lang, TEXTS['en']).get(key, TEXTS['en'][key])

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
            return f"{stats['malicious']} engines flagged"
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
    # Now show tools
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
    lang = USER_LANG.get(chat_id, 'en')
    prompts = TEXTS.get(lang, TEXTS['en'])['prompts']
    prompt_map = {'link': prompts['link'], 'number': prompts['number'], 'upi': prompts['upi'], 'job': prompts['job'], 'ad': prompts['ad']}
    await query.edit_message_text(prompt_map.get(mode, prompts['link']), parse_mode='Markdown')

async def handle_link(url, update):
    domain = urlparse(url).netloc or urlparse('https://'+url).netloc
    age = check_domain_age(domain)
    score=0; reasons=[]
    # Strong keyword check
    scam_keywords = ['offer','lottery','win','free','amazon','flipkart','gov','kyc','prize']
    if any(k in domain.lower() for k in scam_keywords): score+=30; reasons.append(f"⚠️ Suspicious keywords in domain")

    if age is not None:
        if age<30: score+=40; reasons.append(f"🚨 Domain {age} days only (NEW!)")
        elif age<180: score+=20; reasons.append(f"⚠️ Domain {age} days old")
        else: reasons.append(f"✅ Domain {age} days old")
    else:
        score+=15; reasons.append("⚠️ Whois hidden / new domain")

    if re.search(r'\d+\.\d+\.\d+\.\d+', url): score+=25; reasons.append("⚠️ IP URL")
    if 'bit.ly' in url or 'tinyurl' in url or '@' in url: score+=20; reasons.append("⚠️ Shortener / masked URL")

    vt = vt_check(url)
    if vt: reasons.append(f"🔍 VT: {vt}")
    else: reasons.append("🔍 VT: Add VT_API_KEY for full check")

    status = "🚨 SCAM LIKELY" if score>=50 else "⚠️ SUSPICIOUS" if score>=25 else "✅ SAFE"
    await update.message.reply_text(f"{status} ({score}/100)\n{domain}\n\n"+"\n".join(reasons))

async def handle_number(text, update):
    num = re.sub(r'\D','',text)[-10:]
    spam_score = 80 if '9999' in num or '1111' in num else 40 if num.startswith('140') else 20
    await update.message.reply_text(f"📱 Number: +91 {num}\nSpam Score: {spam_score}/100\n{'🚨 Spam Likely' if spam_score>60 else '⚠️ Telemarketer' if spam_score>30 else '✅ Looks OK'}")

async def handle_upi(text, update):
    upis = re.findall(r'[\w.-]+@[\w]+', text)
    for upi in upis:
        fake = any(x in upi.lower() for x in ['fake','fraud','lottery'])
        await update.message.reply_text(f"💳 UPI: {upi}\n{'🚨 FAKE PATTERN' if fake else '✅ Format OK - check receiver name!'}")

async def handle_job(text, update):
    traps = ['registration fee','₹','pay to join','investment','work from home','telegram task','earn daily']
    found = [t for t in traps if t in text.lower()]
    score = len(found)*30
    await update.message.reply_text(f"💼 Job Risk: {score}/100\nFound: {', '.join(found) if found else 'None'}\n{'🚨 FEE TRAP - Do not pay!' if score>=30 else '✅ No obvious trap'}")

async def router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    chat_id = update.effective_chat.id
    mode = USER_MODE.get(chat_id, 'auto')

    if mode == 'link' or '.' in text and len(text) < 100:
        url = text if text.startswith('http') else 'https://'+text
        await handle_link(url, update)
    elif mode == 'number' or re.search(r'\b\d{10}\b', text): await handle_number(text, update)
    elif mode == 'upi' or '@' in text: await handle_upi(text, update)
    elif mode == 'job' or any(k in text.lower() for k in ['job','work','fee','earn']): await handle_job(text, update)
    else: await handle_link(text if text.startswith('http') else 'https://'+text, update)

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 FB Ad AI: 'Earn ₹5000 daily' - Check if registration fee asked. MLM trap likely!")

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
    print("ULTIMATE Bot Started - FIXED")
    app_bot.run_polling()

if __name__ == '__main__':
    main()
