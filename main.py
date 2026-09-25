import os, re, requests, whois
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
VT_KEY = os.getenv("VT_API_KEY") # optional

user_lang = {}
reports_db = {} # simple in-memory, later DB aakkam

# --- 4 LANGUAGE TEXT ---
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
        await q.edit_message_text("🔗 **Link Check**\n\nOru link ayachu tha! Njan check cheyyum:\n✓ Domain Age (whois)\n✓ VirusTotal\n✓ Screenshot Preview\n\nLink ippo ayachu tha 👇", parse_mode='Markdown', reply_markup=main_menu(lang))
    elif data == 'f_num':
        await q.edit_message_text("📱 **Number Check**\n\nPhone number ayachu tha!\n✓ Spam Score\n✓ Circle/Operator\n✓ Community Reports\n\nNumber ayachu tha 👇", parse_mode='Markdown', reply_markup=main_menu(lang))
    elif data == 'f_upi':
        await q.edit_message_text("💳 **UPI/QR Check**\n\nUPI ID (@ybl/@okaxis) atho QR photo ayachu tha!\n✓ Fake vs Original\n✓ QR decode\n\nIppo ayachu tha 👇", parse_mode='Markdown', reply_markup=main_menu(lang))
    elif data == 'f_job':
        await q.edit_message_text("💼 **Job/Message Check**\n\nJob message forward cheyyu! Njan trap nokkam:\n✓ Registration Fee\n✓ Telegram Task Scam\n\nMessage ayachu tha 👇", parse_mode='Markdown', reply_markup=main_menu(lang))
    elif data == 'f_ss':
        await q.edit_message_text("📸 **Screenshot AI - FB Ad Auto Analyze**\n\nFB Ad / WhatsApp screenshot photo ayachu tha! AI scam words detect cheyyum!", reply_markup=main_menu(lang))
    elif data == 'f_report':
        await q.edit_message_text("🚨 **Report Community**\n\nScam link/number report cheyyan: `/report <data>`\nExample: `/report free-iphone.com scam`\n\nTop scams kanan: /toplist", reply_markup=main_menu(lang))
    elif data == 'f_premium':
        await q.edit_message_text("💰 **₹0 Premium Full Report**\n\nLast check cheytha data-nte full PDF report kittum! Link ayachathinu shesham /fullreport adikkuka\n\n100% FREE!", reply_markup=main_menu(lang))

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    uid = update.from_user.id
    lang = user_lang.get(uid, 'ml')

    # LINK CHECK - Domain Age + VT + Screenshot
    if 'http' in text or '.' in text and len(text) < 80:
        domain = re.search(r'((https?://)?[^\s]+\.[^\s]+)', text).group(1) if re.search(r'[^\s]+\.[^\s]+', text) else text
        try:
            clean_domain = domain.replace('https://','').replace('http://','').split('/')[0]
            w = whois.whois(clean_domain)
            created = w.creation_date[0] if isinstance(w.creation_date, list) else w.creation_date
            age_days = (datetime.now() - created).days if created else -1
            age_str = f"{age_days} days" if age_days!=-1 else "Hidden"
            risk = "🔴 HIGH RISK! < 60 days!" if age_days!=-1 and age_days<60 else "🟢 Old domain"

            vt_msg = "Add VT_API_KEY for VT scan"
            if VT_KEY:
                try:
                    r = requests.get(f"https://www.virustotal.com/api/v3/domains/{clean_domain}", headers={"x-apikey": VT_KEY}, timeout=10)
                    vt_msg = f"VT: {r.json().get('data',{}).get('attributes',{}).get('last_analysis_stats','')}"
                except: vt_msg = "VT check failed"

            screenshot_url = f"https://s.wordpress.com/mshots/v1/{domain}?w=800"

            await update.message.reply_text(f"🔗 **Link Check Result**\n\n🌐 `{clean_domain}`\n📅 Domain Age: {age_str}\n{risk}\n🛡️ {vt_msg}\n\n📸 Preview:\n{screenshot_url}\n\n💡 Tip: Age < 6 month + Gift/Free offer = 99% SCAM", parse_mode='Markdown')
            await update.message.reply_photo(photo=screenshot_url, caption="🌐 Website Preview")
        except Exception as e:
            await update.message.reply_text(f"🔗 Checking {domain}... Whois hidden aanenkil risk aanu!")
        return

    # NUMBER CHECK
    if re.search(r'[6-9]\d{9}', text):
        num = re.search(r'(\+?91)?([6-9]\d{9})', text).group(2)
        await update.message.reply_text(f"📱 **Number: {num}**\n\n🔍 Spam Score: {reports_db.get(num, 0)} reports\n📍 Circle: Kerala (Sample - API add cheythal real kittum)\n🚨 Community: {'⚠️ SCAM reported!' if num in reports_db else 'No report yet - Be first to /report'}\n\n/fullreport adichal full details kittum!")
        return

    # UPI CHECK
    if '@' in text:
        if re.match(r'^[\w.-]+@[\w]+
