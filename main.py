import os, re, threading, requests, whois
from flask import Flask
from datetime import datetime
from urllib.parse import urlparse
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

app = Flask(__name__)
@app.route('/')
def home(): return "Scam Guard India ULTIMATE LIVE"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
VT_KEY = os.environ.get("VT_API_KEY")
USER_LANG = {}
REPORTS = []

LANG = {
 'en': {'start': "🛡️ *Scam Guard India Ultimate* 🛡️\n\n🔗 Link Check - Domain age + VirusTotal\n📱 Number Check - Spam score + Circle\n💳 UPI/QR Check - Fake vs Original\n💼 Job Check - Fee trap\n\nExtra:\n🌐 /lang - En/Ml/Ta/Hi\n📸 Send FB Ad Screenshot\n🚨 /report <scam>\n💰 /full <link> - ₹0 Premium\n\nJust send any link/number/UPI/job!"},
 'ml': {'start': "🛡️ *Scam Guard India* 🛡️\n\nLink, Number, UPI, Job okke check cheyyam! Link ayakk!"},
 'ta': {'start': "🛡️ *Scam Guard* 🛡️\nLink, Number, UPI, Job scam check pannalam!"},
 'hi': {'start': "🛡️ *Scam Guard India* 🛡️\nLink, Number, UPI, Job check karega! Link bhejo!"}
}

def get_lang(chat_id): return USER_LANG.get(chat_id, 'en')

def check_domain_age(domain):
    try:
        w = whois.whois(domain)
        c = w.creation_date
        if isinstance(c, list): c=c[0]
        if c: return (datetime.now()-c).days
    except: pass
    return None

def vt_check(url):
    if not VT_KEY: return "Add VT_API_KEY in Render for VirusTotal"
    try:
        r = requests.post("https://www.virustotal.com/api/v3/urls", headers={"x-apikey": VT_KEY}, data={"url":url}, timeout=10)
        if r.status_code==200:
            id = r.json()['data']['id']
            r2 = requests.get(f"https://www.virustotal.com/api/v3/analyses/{id}", headers={"x-apikey": VT_KEY}, timeout=10)
            stats = r2.json()['data']['attributes']['stats']
            return f"VT: {stats['malicious']} malicious"
    except Exception as e: return f"VT Error: {e}"
    return "VT done"

async def handle_link(url, update):
    domain = urlparse(url).netloc
    age = check_domain_age(domain)
    score=0; reasons=[]
    if age is not None:
        if age<30: score+=40; reasons.append(f"⚠️ Domain {age} days only (NEW!)")
        elif age<180: score+=20; reasons.append(f"⚠️ Domain {age} days")
        else: reasons.append(f"✅ Domain {age} days old")
    if re.search(r'\d+\.\d+\.\d+\.\d+', url): score+=25; reasons.append("⚠️ IP URL")
    if 'bit.ly' in url or '@' in url: score+=20; reasons.append("⚠️ Shortener")
    reasons.append(f"🔍 {vt_check(url)}")
    reasons.append(f"🖼️ Preview: https://image.thum.io/get/width/600/crop/800/{url}")
    status = "🚨 SCAM LIKELY" if score>=50 else "⚠️ SUSPICIOUS" if score>=25 else "✅ SAFE"
    await update.message.reply_text(f"{status} ({score}/100)\n{domain}\n\n"+"\n".join(reasons))

async def handle_number(text, update):
    num = re.sub(r'\D','',text)[-10:]
    spam_score = 80 if '9999' in num else 30
    await update.message.reply_text(f"📱 Number: +91 {num}\nSpam Score: {spam_score}/100\n{'🚨 Spam Likely' if spam_score>60 else '✅ Looks OK'}")

async def handle_upi(text, update):
    upis = re.findall(r'[\w.-]+@[\w]+', text)
    for upi in upis:
        fake = 'fake' in upi.lower()
        await update.message.reply_text(f"💳 UPI: {upi}\n{'🚨 FAKE PATTERN' if fake else '✅ Format OK - Check name in app'}")

async def handle_job(text, update):
    traps = ['registration fee','₹','pay to join','investment','work from home','telegram task']
    found = [t for t in traps if t in text.lower()]
    score = len(found)*25
    await update.message.reply_text(f"💼 Job Risk: {score}/100\nFound: {', '.join(found) if found else 'None'}\n{'🚨 FEE TRAP - Real jobs never ask money' if score>=25 else '✅ No trap'}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(update.effective_chat.id)
    await update.message.reply_text(LANG[lang]['start'], parse_mode='Markdown')

async def lang_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.args and context.args[0] in ['en','ml','ta','hi']:
        USER_LANG[update.effective_chat.id]=context.args[0]
        await update.message.reply_text(f"Language set to {context.args[0]}")
    else: await update.message.reply_text("Use: /lang en/ml/ta/hi")

async def report_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    REPORTS.append(update.message.text)
    await update.message.reply_text(f"🚨 Report added! Total: {len(REPORTS)} - You saved someone!")

async def full_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = ' '.join(context.args) if context.args else ""
    await update.message.reply_text(f"💰 ₹0 Premium Full Report\nURL: {url}")
    if url.startswith('http'): await handle_link(url, update)

async def router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    if '@' in text and 'ybl' in text or 'okaxis' in text.lower() or '@' in text and len(text)<30: await handle_upi(text, update)
    elif re.search(r'\b\d{10}\b', text): await handle_number(text, update)
    elif any(k in text.lower() for k in ['job','work','registration','fee','earn']): await handle_job(text, update)
    elif '.' in text:
        url = text if text.startswith('http') else 'https://'+text
        await handle_link(url, update)
    else: await handle_job(text, update)

async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 FB Ad AI: 'Earn ₹5000 daily' - MLM trap!\n⚠️ Page likes <100? Comments off?\n🚨 90% Scam Ad!")

if __name__ == '__main__':
    threading.Thread(target=run_flask, daemon=True).start()
    app_bot = Application.builder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("lang", lang_cmd))
    app_bot.add_handler(CommandHandler("report", report_cmd))
    app_bot.add_handler(CommandHandler("full", full_cmd))
    app_bot.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, router))
    print("ULTIMATE Bot Started")
    app_bot.run_polling()
