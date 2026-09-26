import os, re, threading, requests, whois
from flask import Flask
from datetime import datetime
from urllib.parse import urlparse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# --- 1. FLASK ALWAYS ALIVE FOR RENDER ---
app = Flask(__name__)
@app.route('/')
def home():
    return "Scam Guard India ULTIMATE LIVE - 100% FIXED - Bot is Alive!"
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- 2. CONFIG ---
BOT_TOKEN = os.environ.get("BOT_TOKEN")
VT_KEY = os.environ.get("VT_API_KEY")
USER_LANG = {}
USER_MODE = {}

TEXTS = {
    'en': {
        'welcome': "🛡️ *Welcome to Scam Guard India* 🛡️\n\nYour personal anti-scam shield. Select your language:",
        'ask_tool': "✅ Language set!\n\n👇 *What do you want to check today?*",
        'tools': ["🔗 Link Check", "📱 Number Check", "💳 UPI Check", "💼 Job Scam Check", "📸 FB Ad Check"],
        'prompts': {
            'link': "🔗 *Link Check Mode*\n\nSend any link. Eg: `amazon-offer-2024.com`",
            'number': "📱 *Number Check Mode*\n\nSend 10 digit mobile number. Must start with 6-9",
            'upi': "💳 *UPI Check Mode*\n\nSend UPI ID. Eg: `shop@ybl` or `amazon-refund@okhdfcbank`",
            'job': "💼 *Job Scam Mode*\n\nForward the job message / screenshot text",
            'ad': "📸 *FB Ad Check Mode*\n\nSend FB Job Ad screenshot"
        }
    },
    'ml': {
        'welcome': "🛡️ *Scam Guard India* യിലേക്ക് സ്വാഗതം 🛡️\n\nനിങ്ങളുടെ സ്വകാര്യ സ്കാം ഷീൽഡ്. ഭാഷ തിരഞ്ഞെടുക്കൂ:",
        'ask_tool': "✅ ഭാഷ സെറ്റ് ചെയ്തു!\n\n👇 *എന്താണ് പരിശോധിക്കേണ്ടത്?*",
        'tools': ["🔗 ലിങ്ക് പരിശോധന", "📱 നമ്പർ പരിശോധന", "💳 UPI പരിശോധന", "💼 ജോലി തട്ടിപ്പ്", "📸 FB പരസ്യം"],
        'prompts': {
            'link': "🔗 *ലിങ്ക് മോഡ്*\n\nലിങ്ക് അയക്കൂ. Eg: `amazon-offer.com`",
            'number': "📱 *നമ്പർ മോഡ്*\n\n10 അക്ക മൊബൈൽ നമ്പർ അയക്കൂ. 6-9 ൽ തുടങ്ങണം",
            'upi': "💳 *UPI മോഡ്*\n\nUPI ID അയക്കൂ. Eg: `shop@ybl`",
            'job': "💼 *ജോലി മോഡ്*\n\nജോലി മെസ്സേജ് അയക്കൂ",
            'ad': "📸 *FB മോഡ്*\n\nFB ജോബ് പരസ്യത്തിന്റെ Screenshot അയക്കൂ"
        }
    },
    'ta': {
        'welcome': "🛡️ *Scam Guard India* ku Varaverppu 🛡️\n\nLanguage select pannunga:",
        'ask_tool': "✅ Language set!\n\n👇 *Enna check pannanum?*",
        'tools': ["🔗 Link Check", "📱 Number Check", "💳 UPI Check", "💼 Job Check", "📸 FB Ad Check"],
        'prompts': {
            'link': "🔗 *Link Mode*\n\nLink anupunga",
            'number': "📱 *Number Mode*\n\n10 digit number anupunga (6-9 start)",
            'upi': "💳 *UPI Mode*\n\nUPI ID anupunga",
            'job': "💼 *Job Mode*\n\nJob message anupunga",
            'ad': "📸 *FB Mode*\n\nScreenshot anupunga"
        }
    },
    'hi': {
        'welcome': "🛡️ *Scam Guard India* me Swagat Hai 🛡️\n\nBhasha chune:",
        'ask_tool': "✅ Bhasha set ho gayi!\n\n👇 *Kya check karna hai?*",
        'tools': ["🔗 Link Check", "📱 Number Check", "💳 UPI Check", "💼 Job Check", "📸 FB Ad Check"],
        'prompts': {
            'link': "🔗 *Link Mode*\n\nLink bhejo",
            'number': "📱 *Number Mode*\n\n10 digit mobile bhejo (6-9 se start)",
            'upi': "💳 *UPI Mode*\n\nUPI ID bhejo. Eg: `shop@ybl`",
            'job': "💼 *Job Mode*\n\nJob message bhejo",
            'ad': "📸 *FB Mode*\n\nFB Ad ka screenshot bhejo"
        }
    }
}

def get_lang_data(chat_id):
    lang = USER_LANG.get(chat_id, 'en')
    return TEXTS.get(lang, TEXTS['en'])

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
    chat_id = update.effective_chat.id
    USER_MODE.pop(chat_id, None)
    USER_LANG.pop(chat_id, None)
    keyboard = [
        [InlineKeyboardButton("English 🇬🇧", callback_data="lang_en"), InlineKeyboardButton("മലയാളം 🇮🇳", callback_data="lang_ml")],
        [InlineKeyboardButton("தமிழ்", callback_data="lang_ta"), InlineKeyboardButton("हिंदी 🇮🇳", callback_data="lang_hi")]
    ]
    await update.message.reply_text(TEXTS['en']['welcome'], reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def lang_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data.split('_')[1]
    chat_id = query.message.chat.id
    USER_LANG[chat_id] = lang
    USER_MODE.pop(chat_id, None)
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
    prompts = get_lang_data(chat_id)['prompts']
    mapping = {'link': prompts['link'], 'number': prompts['number'], 'upi': prompts['upi'], 'job': prompts['job'], 'ad': prompts['ad']}
    await query.edit_message_text(mapping.get(mode, prompts['link']), parse_mode='Markdown')

async def handle_link(url, update):
    try:
        domain = urlparse(url).netloc or urlparse('https://'+url).netloc or url
        age = check_domain_age(domain)
        score=0; reasons=[]
        if any(k in domain.lower() for k in ['offer','lottery','win','free','amazon','flipkart','gov','kyc','prize','lucky']): score+=30; reasons.append("⚠️ Suspicious keywords (offer/lottery/gov)")
        if age is not None:
            if age<30: score+=40; reasons.append(f"🚨 Domain {age} days only (VERY NEW!)")
            elif age<180: score+=20; reasons.append(f"⚠️ Domain {age} days old")
            else: reasons.append(f"✅ Domain {age} days old")
        else: score+=15; reasons.append("⚠️ Whois hidden / new domain")
        if re.search(r'\d+\.\d+\.\d+\.\d+', url): score+=25; reasons.append("⚠️ IP based URL (scam sign)")
        if 'bit.ly' in url or 'tinyurl' in url or 'cutt.ly' in url: score+=20; reasons.append("⚠️ Shortener URL (hidden)")
        vt = vt_check(url)
        if vt: reasons.append(f"🔍 VirusTotal: {vt}")
        status = "🚨 SCAM LIKELY" if score>=50 else "⚠️ SUSPICIOUS" if score>=25 else "✅ SAFE"
        await update.message.reply_text(f"{status} ({score}/100)\n🌐 {domain}\n\n"+"\n".join(reasons))
    except Exception as e:
        await update.message.reply_text(f"Link check error: {e}")

async def handle_number(text, update):
    digits = re.sub(r'\D','',text)
    num = digits[-10:] if len(digits)>=10 else digits
    if len(num)!=10:
        await update.message.reply_text("❌ 10 digit number thanne ayakk. Eg: 9876543210")
        return
    if num[0] not in ['6','7','8','9']:
        await update.message.reply_text(f"❌ **Invalid Mobile Number!**\n\n📱 `{num}`\nIndian mobile 6,7,8,9 il thanne thudanganam.\n\n11, 01, 14 okke Landline/Invalid aanu.\nType /start to go back.", parse_mode='Markdown')
        return
    spam_score=0; reasons=[]
    if re.search(r'(\d)\1{5,}', num): spam_score+=80; reasons.append("Same digit repeated (99999)")
    if num.startswith('140'): spam_score+=60; reasons.append("Telemarketer series (140)")
    if num in ['9876543210','1234567890','0000000000','1111111111']: spam_score+=90; reasons.append("Fake test number")
    if spam_score>=60: msg=f"🚨 SPAM / FAKE ({spam_score}/100)\n{', '.join(reasons)}"
    elif spam_score>=30: msg=f"⚠️ Telemarketer? ({spam_score}/100)"
    else: msg=f"✅ Valid Mobile - Looks OK ({spam_score}/100)"
    await update.message.reply_text(f"📱 Number: +91 {num}\n{msg}")

async def handle_upi(text, update):
    upis = re.findall(r'[\w.\-]+@[\w]+', text.lower())
    if not upis:
        await update.message.reply_text("❌ UPI format sheriyalla. Eg: `shop@ybl` or `name@okhdfcbank`\nType /start to change mode.", parse_mode='Markdown')
        return
    for upi in upis:
        scam_keywords = ['refund','lucky','offer','prize','lottery','army','amazon','flipkart','reward','cashback','kyc','verify','blocked','earn','investment','free','gift','paytm-cash']
        found = [k for k in scam_keywords if k in upi]
        if found:
            await update.message.reply_text(f"🚨 **SCAM UPI!** ({min(len(found)*30,100)}/100)\n💳 `{upi}`\n⚠️ Keywords: {', '.join(found)}\n\n❌ **Ith pay cheyyaruth!**\nType /start", parse_mode='Markdown')
        else:
            await update.message.reply_text(f"✅ UPI Format OK\n💳 `{upi}`\n⚠️ UPI appil receiver name nokku, verify cheyyu!\n\nType /start", parse_mode='Markdown')

async def handle_job(text, update):
    traps = ['registration fee','registration fees','₹','rs.','pay to join','investment','work from home','telegram task','earn daily','fee','charges','security deposit']
    found = [t for t in traps if t in text.lower()]
    score = len(found)*30
    if score>=60:
        await update.message.reply_text(f"🚨 **JOB SCAM LIKELY!** ({min(score,100)}/100)\nFound trap words: {', '.join(found)}\n\n❌ **Fee chodikkunna job = 100% SCAM!** Pay cheyyaruth!\n\nType /start")
    elif score>=30:
        await update.message.reply_text(f"⚠️ **SUSPICIOUS JOB** ({score}/100)\nFound: {', '.join(found)}\n\nBe careful! Company verify cheyyu.\nType /start")
    else:
        await update.message.reply_text(f"✅ No obvious trap words found ({score}/100)\nBut still verify company in Google/LinkedIn.\n\nType /start")

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = ("🕵️ *FB AD SCAM ANALYSIS*\n\nScreenshotil ithokke nokku:\n1. `Registration Fee` undo? -> 100% SCAM 🚨\n2. `Telegramil message ayakk` -> SCAM\n3. `Daily ₹3000-5000 work from home` -> FAKE\n4. Company name, website illa? -> SUSPICIOUS\n\n📊 **Rule:** Fee chodikkunna ellam = 🚨 SCAM (90/100)\n\n💡 Adile text copy cheythu ivide ayakk, njaan check cheyyam!\n\nType /start")
    await update.message.reply_text(msg, parse_mode='Markdown')

async def router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    chat_id = update.effective_chat.id
    low = text.lower().strip()
    if low in ['hi','hello','hai','hey','yo','/start','start','menu','help']:
        USER_MODE.pop(chat_id, None)
        await start(update, context)
        return
    mode = USER_MODE.get(chat_id, 'auto')
    if mode == 'upi':
        if '@' not in text:
            await update.message.reply_text("💳 UPI modeil aanu. UPI ID ayakk. Eg: `shop@ybl`\nMaaranaan /start adikk", parse_mode='Markdown')
            return
        await handle_upi(text, update); return
    if mode == 'number':
        await handle_number(text, update); return
    if mode == 'job':
        await handle_job(text, update); return
    if mode == 'link':
        url = text if text.startswith('http') else 'https://'+text
        await handle_link(url, update); return
    if mode == 'ad':
        await photo_handler(update, context); return
    if re.search(r'[\w.\-]+@(?:okaxis|okhdfcbank|okicici|oksbi|ybl|axl|upi|paytm|apl|ibl)', low):
        await handle_upi(text, update)
    elif re.search(r'\b\d{10,}\b', text):
        await handle_number(text, update)
    elif any(k in low for k in ['job','work','earn','registration','fee','investment','telegram task']):
        await handle_job(text, update)
    else:
        url = text if text.startswith('http') else 'https://'+text
        await handle_link(url, update)

def main():
    threading.Thread(target=run_flask, daemon=True).start()
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN missing!")
        return
    print("ULTIMATE Bot Started - 100% PERFECT - NO CRASH")
    app_bot = Application.builder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CallbackQueryHandler(lang_callback, pattern="^lang_"))
    app_bot.add_handler(CallbackQueryHandler(tool_callback, pattern="^tool_"))
    app_bot.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, router))
    app_bot.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
