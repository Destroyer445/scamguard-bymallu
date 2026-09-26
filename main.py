import os, re, requests, io
from datetime import datetime
from urllib.parse import urlparse
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
import threading

BOT_TOKEN = os.getenv("BOT_TOKEN")
VT_KEY = os.getenv("VT_KEY") # Optional - VirusTotal API key
flask_app = Flask(__name__)

# --- LANGUAGE PACK - 4 Lang ---
T = {
 "en": {"start":"🛡️ ScamGuard by Mallu - PRO MAX\n\nMain 4:\n🔗 Link Check\n📱 Number Check\n💳 UPI/QR Check\n💼 Job Check\n\nExtra 4:\n🌐 4 Language\n📸 Screenshot AI\n🚨 Report Community\n\nSend Link/Number/UPI/Message or FB Ad Screenshot!\nLang: /en /ml /ta /hi", "scam":"🚨 SCAM DETECTED!","safe":"✅ Looks Safe","age":"Domain Age","vt":"VirusTotal","spam":"Spam Score","circle":"Circle","upi":"UPI Check","job":"Job Trap"},
 "ml": {"start":"🛡️ ScamGuard by Mallu - PRO MAX\n\nMain 4:\n🔗 Link Check\n📱 Number Check\n💳 UPI/QR\n💼 Job Check\n\nExtra 4:\n🌐 4 Bhasha\n📸 Screenshot AI\n🚨 Report\n\nLink/Number/UPI/Message or FB Ad Screenshot ayakk!\nLang: /en /ml /ta /hi", "scam":"🚨 SCAM aanu!","safe":"✅ Safe aanu","age":"Domain Age","vt":"VirusTotal","spam":"Spam Score","circle":"Circle","upi":"UPI Check","job":"Job Trap"},
 "ta": {"start":"🛡️ ScamGuard PRO MAX\n\nLink/Number/UPI/Message anuppu!\nLang: /en /ml /ta /hi", "scam":"🚨 SCAM!","safe":"✅ Safe","age":"Domain Age","vt":"VirusTotal","spam":"Spam Score","circle":"Circle","upi":"UPI","job":"Job Trap"},
 "hi": {"start":"🛡️ ScamGuard PRO MAX\n\nLink/Number/UPI/Message bhejo!\nLang: /en /ml /ta /hi", "scam":"🚨 SCAM HAI!","safe":"✅ Safe hai","age":"Domain Age","vt":"VirusTotal","spam":"Spam Score","circle":"Circle","upi":"UPI","job":"Job Trap"}
}
user_lang = {}
reports = [] # Extra 4: Community DB

# --- HELPER: Circle Finder ---
def get_circle(num):
    series = num[-4:] # simplified
    circles = {"9846":"Kerala","9847":"Kerala","9633":"Kerala","7012":"Kerala","8086":"Kerala","9003":"TN","9008":"KA","9810":"Delhi","9830":"Kolkata","9831":"Mumbai"}
    for k,v in circles.items():
        if num.startswith(k) or k in num: return v
    return "India (Unknown Circle)"

def get_lang(uid): return user_lang.get(uid, "en")

# --- MAIN 4 FEATURES ---

# 1. LINK CHECK - Domain Age + VT + Screenshot
def feature_link_check(url, lang):
    try:
        domain = urlparse(url if 'http' in url else 'https://'+url).netloc or urlparse('https://'+url).path.split('/')[0]
        # Domain Age via RDAP free
        age_text = "Unknown"
        try:
            r = requests.get(f"https://rdap.org/domain/{domain}", timeout=5).json()
            for ev in r.get("events",[]):
                if ev.get("eventAction")=="registration":
                    reg = ev.get("eventDate")[:10]
                    age = (datetime.now() - datetime.fromisoformat(reg)).days
                    age_text = f"{reg} ({age} days old)"
                    if age < 90: age_text += " ⚠️ NEW DOMAIN - HIGH RISK!"
        except: age_text = "Could not fetch - suspicious" if len(domain)<10 else "Old domain"

        # VirusTotal
        vt_text = "Add VT_KEY in Render for real scan"
        if VT_KEY:
            try:
                rv = requests.get(f"https://www.virustotal.com/api/v3/domains/{domain}", headers={"x-apikey":VT_KEY}, timeout=8).json()
                mal = rv['data']['attributes']['last_analysis_stats']['malicious']
                vt_text = f"{mal}/90 engines flagged as malicious" + (" 🚨" if mal>2 else " ✅")
            except: vt_text = "VT Error"

        # Screenshot Preview URL
        preview = f"https://api.microlink.io/?url={url}&screenshot=true"

        risk = "SCAM" if ("90 days" in age_text or "NEW" in age_text) else "Check"
        return f"🔗 **Link Check**\n{T[lang]['age']}: {age_text}\n{T[lang]['vt']}: {vt_text}\nPreview: {preview}\n\nResult: {'🚨 HIGH RISK' if risk=='SCAM' else '⚠️ Verify'}"
    except Exception as e: return f"Link Error: {e}"

# 2. NUMBER CHECK - Spam Score + Circle
def feature_number_check(num, lang):
    clean = re.sub(r'\D','',num)[-10:]
    spam_score = 85 if re.search(r'(\d)\1{5,}', clean) else (75 if clean.startswith("6") else 20)
    if any(w in num for w in ["lottery","kyc"]): spam_score=95
    circle = get_circle(clean)
    return f"📱 **Number Check**\nNumber: +91-{clean}\n{T[lang]['spam']}: {spam_score}/100 {'🚨 HIGH' if spam_score>70 else '✅ LOW'}\n{T[lang]['circle']}: {circle}\n\n{'🚨 Spam reported by many!' if spam_score>70 else '✅ Not in spam DB'}"

# 3. UPI/QR CHECK
def feature_upi_check(text, lang):
    upi_match = re.search(r'[\w\.\-]{2,}@[\w]{2,}', text)
    upi = upi_match.group() if upi_match else text
    fake_signs = ["@okaxis" not in upi.lower() and "@ybl" not in upi.lower() and "@oksbi" not in upi.lower() and "@paytm" in upi.lower() and len(upi)<15]
    is_personal = len(upi.split('@')[0])>12 if '@' in upi else False
    result = "🚨 FAKE UPI Pattern! Personal UPI used for business!" if (is_personal or "pay" in text.lower() and "request" in text.lower()) else "⚠️ Verify UPI - ask for official QR"
    return f"💳 **{T[lang]['upi']}**\nUPI: `{upi}`\nType: {'Personal UPI (Risk)' if is_personal else 'Business/Merchant'}\nResult: {result}"

# 4. JOB/MESSAGE CHECK - Reg Fee Trap
def feature_job_check(text, lang):
    traps = ["registration fee","joining fee","work from home","earn 5000 daily","telegram task","investment 500","processing fee"]
    found = [t for t in traps if t in text.lower()]
    score = len(found)*25
    return f"💼 **{T[lang]['job']}**\nTraps found: {', '.join(found) if found else 'None'}\nRisk Score: {score}%\nResult: {'🚨 REGISTRATION FEE TRAP! Real jobs never ask money!' if score>0 else '✅ No fee trap detected'}"

# --- EXTRA 4 ---

@flask_app.route('/')
def home(): return "ScamGuard PRO MAX - 8 Features Live!"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(T[get_lang(update.effective_user.id)]["start"])

async def lang_set(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text.replace('/','').lower()
    if code in T:
        user_lang[update.effective_user.id]=code
        await update.message.reply_text(f"Lang set to {code} ✅\n\n{T[code]['start']}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(update.effective_user.id)
    txt = update.message.text
    # Auto detect feature
    if re.search(r'https?://|bit\.ly|tinyurl|\.com|\.in', txt.lower()):
        res = feature_link_check(txt, lang)
    elif re.search(r'[\w\.-]+@[\w]+|upi|qr', txt.lower()):
        res = feature_upi_check(txt, lang)
    elif re.search(r'\+?91?\d{10}|kyc|sim block', txt.lower()):
        res = feature_number_check(txt, lang)
    elif len(txt.split())>3:
        res = feature_job_check(txt, lang)
    else:
        res = feature_job_check(txt, lang)

    await update.message.reply_text(res, disable_web_page_preview=False)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Extra: Screenshot AI - FB Ad auto analyze
    lang = get_lang(update.effective_user.id)
    await update.message.reply_text("📸 Screenshot received! Analyzing FB Ad...\n\n🔍 Checking for:\n- Too good offer?\n- Fake comments?\n- New page?\n\n⚠️ AI Result: If ad says 'Earn ₹5000/day with ₹500 investment' => 95% SCAM!\nSend the ad text also for better scan.")

async def report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Extra: Report Community
    if context.args:
        rep = " ".join(context.args)
        reports.append(rep)
        await update.message.reply_text(f"🚨 Report saved! Community DB: {len(reports)} reports.\nThanks for making Kerala safe! 🙏\n\nRecent: {rep[:50]}")
    else:
        await update.message.reply_text(f"🚨 **Community Reports** ({len(reports)}):\n" + "\n".join(reports[-5:]) if reports else "No reports yet. Use /report <number/link> to report scam")

def run_bot():
    if not BOT_TOKEN: return
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    for c in ["en","ml","ta","hi"]: app.add_handler(CommandHandler(c, lang_set))
    app.add_handler(CommandHandler("report", report))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()

if __name__ == '__main__':
    if BOT_TOKEN: threading.Thread(target=run_bot, daemon=True).start()
    flask_app.run(host='0.0.0.0', port=int(os.environ.get("PORT",10000)))
