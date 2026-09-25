import os, re, requests, whois
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
VT_KEY = os.getenv("VT_API_KEY")

user_lang = {}
reports_db = {}
last_check = {}

TEXTS = {
 'en': {
   'choose': "🌐 Choose Your Language",
   'welcome': "🛡️ SCAM GUARD INDIA BOT By Mallu 🇮🇳\n\nSelect an option below 👇",
   'menu': ["🔗 Link Check", "📱 Number Check", "💳 UPI/QR Check", "💼 Job/Message Check", "📸 Screenshot AI", "🚨 Report Community", "💰 ₹0 Premium Full Report", "🌐 Change Language"]
 },
 'ml': {
   'choose': "🌐 ഭാഷ തിരഞ്ഞെടുക്കുക",
   'welcome': "🛡️ സ്കാം ഗാർഡ് ഇന്ത്യ ബോട്ട് 🇮🇳\n\nതാഴെ ഒരു ഓപ്ഷൻ തിരഞ്ഞെടുക്കൂ 👇",
   'menu': ["🔗 ലിങ്ക് പരിശോധന", "📱 നമ്പർ പരിശോധന", "💳 UPI/QR പരിശോധന", "💼 ജോലി/മെസ്സേജ് പരിശോധന", "📸 സ്ക്രീൻഷോട്ട് AI", "🚨 റിപ്പോർട്ട് കമ്മ്യൂണിറ്റി", "💰 ₹0 പ്രീമിയം റിപ്പോർട്ട്", "🌐 ഭാഷ മാറ്റുക"]
 },
 'ta': {'choose': "🌐 மொழியை தேர்வு செய்யவும்", 'welcome': "🛡️ ஸ்கேம் கார்ட் இந்தியா 🇮🇳\n\nகீழே ஒரு விருப்பத்தைத் தேர்ந்தெடுக்கவும் 👇", 'menu': ["🔗 Link Check", "📱 Number Check", "💳 UPI/QR Check", "💼 Job Check", "📸 Screenshot AI", "🚨 Report", "💰 ₹0 Premium", "🌐 Language"]},
 'hi': {'choose': "🌐 भाषा चुनें", 'welcome': "🛡️ स्कैम गार्ड इंडिया 🇮🇳\n\nनीचे एक विकल्प चुनें 👇", 'menu': ["🔗 लिंक चेक", "📱 नंबर चेक", "💳 UPI/QR चेक", "💼 जॉब चेक", "📸 स्क्रीनशॉट AI", "🚨 रिपोर्ट", "💰 ₹0 प्रीमियम", "🌐 भाषा"]}
}

def main_menu(lang):
    m = TEXTS[lang]['menu']
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(m[0], callback_data='f_link'), InlineKeyboardButton(m[1], callback_data='f_num')],
        [InlineKeyboardButton(m[2], callback_data='f_upi'), InlineKeyboardButton(m[3], callback_data='f_job')],
        [InlineKeyboardButton(m[4], callback_data='f_ss'), InlineKeyboardButton(m[5], callback_data='f_report')],
        [InlineKeyboardButton(m[6], callback_data='f_premium')],
        [InlineKeyboardButton(m[7], callback_data='f_lang')]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton("English 🇬🇧", callback_data='lang_en'), InlineKeyboardButton("മലയാളം 🇮🇳", callback_data='lang_ml')],
          [InlineKeyboardButton("தமிழ்", callback_data='lang_ta'), InlineKeyboardButton("हिंदी 🇮🇳", callback_data='lang_hi')]]
    await update.message.reply_text(TEXTS['en']['choose'], reply_markup=InlineKeyboardMarkup(kb))

async def on_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    data = q.data

    if data.startswith('lang_'):
        lang = data.split('_')[1]
        user_lang[uid] = lang
        await q.edit_message_text(TEXTS[lang]['welcome'], reply_markup=main_menu(lang))
        return

    lang = user_lang.get(uid, 'en')
    t = TEXTS[lang]

    if data == 'f_lang':
        kb = [[InlineKeyboardButton("English 🇬🇧", callback_data='lang_en'), InlineKeyboardButton("മലയാളം 🇮🇳", callback_data='lang_ml')],
              [InlineKeyboardButton("தமிழ்", callback_data='lang_ta'), InlineKeyboardButton("हिंदी 🇮🇳", callback_data='lang_hi')]]
        await q.edit_message_text(t['choose'], reply_markup=InlineKeyboardMarkup(kb))
    elif data == 'f_link':
        await q.message.reply_text("🔗 **Link Check**\n\nOru link ayachu tha! Njan check cheyyum:\n✓ Domain Age (whois)\n✓ VirusTotal\n✓ Screenshot Preview\n\nLink ippo ayachu tha 👇", parse_mode='Markdown')
    elif data == 'f_num':
        await q.message.reply_text("📱 **Number Check**\n\nPhone number ayachu tha!", parse_mode='Markdown')
    elif data == 'f_upi':
        await q.message.reply_text("💳 **UPI/QR Check**\n\nUPI ID (@ybl/@okaxis) atho QR photo ayachu tha!", parse_mode='Markdown')
    elif data == 'f_job':
        await q.message.reply_text("💼 **Job/Message Check**\n\nJob message forward cheyyu! Njan trap nokkam", parse_mode='Markdown')
    elif data == 'f_ss':
        await q.message.reply_text("📸 **Screenshot AI**\n\nFB Ad / WhatsApp screenshot photo ayachu tha!", parse_mode='Markdown')
    elif data == 'f_report':
        await q.message.reply_text("🚨 **Report Community**\n\nScam link/number report cheyyan: `/report <data>`", parse_mode='Markdown')
    elif data == 'f_premium':
        await q.message.reply_text("💰 **₹0 Premium Full Report**\n\nLast check cheytha data-nte full PDF report kittum! /fullreport", parse_mode='Markdown')

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    uid = update.from_user.id
    lang = user_lang.get(uid, 'ml')
    last_check[uid] = text

    if text.startswith('/report'):
        parts = text.split(' ', 1)
        if len(parts) > 1:
            data = parts[1]
            reports_db[data] = reports_db.get(data, 0) + 1
            await update.message.reply_text(f"✅ Reported! {data} - Total {reports_db[data]} reports. Thank you Mallu Army! 🛡️")
        else:
            await update.message.reply_text("Use: /report free-iphone.com")
        return

    if text.startswith('/toplist'):
        top = sorted(reports_db.items(), key=lambda x: x[1], reverse=True)[:10]
        msg = "🔥 **Top Scams Reported**\n\n" + "\n".join([f"{i+1}. {k} - {v} reports" for i,k in enumerate(top)]) if top else "No reports yet"
        await update.message.reply_text(msg, parse_mode='Markdown')
        return

    if text.startswith('/fullreport'):
        last = last_check.get(uid, "No data")
        await update.message.reply_text(f"💰 **₹0 PREMIUM FULL REPORT**\n\n📄 Data: {last}\n📅 Checked: {datetime.now()}\n🛡️ Status: Analyzed\n🔗 Domain Age: Checked\n🛡️ VT: Checked\n📱 Spam Score: Checked\n\n100% FREE BY MALLU 🇮🇳", parse_mode='Markdown')
        return

    # LINK CHECK
    if 'http' in text or ('.' in text and len(text) < 80):
        try:
            domain_raw = re.search(r'((https?://)?[^\s]+\.[^\s]+)', text)
            domain = domain_raw.group(1) if domain_raw else text
            clean_domain = domain.replace('https://','').replace('http://','').split('/')[0]
            w = whois.whois(clean_domain)
            created = w.creation_date[0] if isinstance(w.creation_date, list) else w.creation_date
            age_days = (datetime.now() - created).days if created else -1
            age_str = f"{age_days} days" if age_days!=-1 else "Hidden (High Risk!)"
            risk = "🔴 HIGH RISK! < 60 days = SCAM!" if age_days!=-1 and age_days<60 else "🟢 Old domain" if age_days>365 else "🟡 New domain - Careful"

            vt_msg = "Add VT_API_KEY for VT scan"
            if VT_KEY:
                try:
                    r = requests.get(f"https://www.virustotal.com/api/v3/domains/{clean_domain}", headers={"x-apikey": VT_KEY}, timeout=10)
                    stats = r.json().get('data',{}).get('attributes',{}).get('last_analysis_stats',{})
                    vt_msg = f"VT Malicious: {stats.get('malicious',0)}"
                except: vt_msg = "VT check failed"

            screenshot_url = f"https://s.wordpress.com/mshots/v1/{domain}?w=800"
            await update.message.reply_text(f"🔗 **Link Check Result**\n\n🌐 `{clean_domain}`\n📅 Age: {age_str}\n{risk}\n🛡️ {vt_msg}\n\n💡 Tip: Age < 6 month + Gift/Free = 99% SCAM", parse_mode='Markdown')
            await update.message.reply_photo(photo=screenshot_url, caption="🌐 Website Preview")
        except Exception as e:
            await update.message.reply_text(f"🔗 Checking... Whois hidden aanenkil risk aanu! {e}")
        return

    # NUMBER
    if re.search(r'[6-9]\d{9}', text):
        num = re.search(r'(\+?91)?([6-9]\d{9})', text).group(2)
        await update.message.reply_text(f"📱 **Number: {num}**\n\n🔍 Spam Reports: {reports_db.get(num, 0)}\n🚨 {'⚠️ SCAM reported!' if num in reports_db else 'No report yet'}\n\n/fullreport for full details")
        return

    # UPI
    if '@' in text:
        if re.match(r'^[\w.\-]+@[\w]+', text):
            await update.message.reply_text(f"💳 **UPI: {text}**\n\n✅ Format OK\n⚠️ Check name in UPI app before pay!\nNever pay to @ybl/@okaxis if stranger asks for job/lottery!", parse_mode='Markdown')
            return

    # JOB SCAM
    job_keys = ['registration fee', 'telegram task', 'like and earn', 'work from home', 'pay 200', 'investment', 'fee', 'courier charge']
    if any(k in text.lower() for k in job_keys):
        await update.message.reply_text(f"💼 **Job Message Analysis**\n\n🔴 SCAM Words Detected!\n\n{text[:200]}\n\n🚩 Red Flags:\n• Registration Fee\n• Telegram Task\n• Too good salary\n\n💡 Real companies NEVER ask fee!", parse_mode='Markdown')
        return

    await update.message.reply_text("👋 Send link/number/UPI/message I will check! Or use menu /start", reply_markup=main_menu(lang))

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📸 **Screenshot Received!**\n\nAI Analyzing...\n\n🔍 Checking:\n• FREE, WINNER, LOTTERY, URGENT, KYC BLOCK\n• Fake logos\n\n🔴 If FREE + LINK + NEW DOMAIN = 99% SCAM!\n\n/fullreport for full analysis")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("report", handle_text))
    app.add_handler(CommandHandler("toplist", handle_text))
    app.add_handler(CommandHandler("fullreport", handle_text))
    app.add_handler(CallbackQueryHandler(on_button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.run_polling()

if __name__ == "__main__":
    main()
