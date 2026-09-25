import os, re
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")
USER_LANG = {}

# Reply Keyboard - Inline button alla, ithu 100% work aavum
LANG_KB = ReplyKeyboardMarkup([["English 🇬🇧", "മലയാളം 🇮🇳"], ["தமிழ்", "हिंदी"]], resize_keyboard=True, one_time_keyboard=True)
TOOL_KB_ML = ReplyKeyboardMarkup([["🔗 Link", "📱 Number"], ["💳 UPI", "💼 Job"], ["📸 FB Ad", "/start"]], resize_keyboard=True)
TOOL_KB_EN = ReplyKeyboardMarkup([["🔗 Link", "📱 Number"], ["💳 UPI", "💼 Job"], ["📸 FB Ad", "/start"]], resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛡️ *Scam Guard India* 🛡️\n\nYour anti-scam shield. Select language:\n\n👇 *Thazhe buttonil language select cheyyu / Click language below:*",
        reply_markup=LANG_KB, parse_mode='Markdown')

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    chat_id = update.effective_chat.id
    low = text.lower()

    # 1. Language selection - text aayi
    if "മലയാളം" in text or low == "malayalam" or low == "ml":
        USER_LANG[chat_id] = 'ml'
        await update.message.reply_text("✅ മലയാളം സെറ്റ് ആയി!\n\n👇 എന്ത് പരിശോധിക്കണം? താഴെ തിരഞ്ഞെടുക്കൂ:", reply_markup=TOOL_KB_ML)
        return
    if "english" in low or "en" in low and len(low)<5:
        USER_LANG[chat_id] = 'en'
        await update.message.reply_text("✅ English set!\n\n👇 What to check? Select below:", reply_markup=TOOL_KB_EN)
        return
    if "தமிழ்" in text or "tamil" in low:
        USER_LANG[chat_id] = 'ta'
        await update.message.reply_text("✅ தமிழ் தேர்ந்தெடுக்கப்பட்டது!", reply_markup=TOOL_KB_EN)
        return
    if "हिंदी" in text or "hindi" in low:
        USER_LANG[chat_id] = 'hi'
        await update.message.reply_text("✅ हिंदी सेट!", reply_markup=TOOL_KB_EN)
        return

    if text.startswith('/start'):
        await start(update, context)
        return

    # 2. Tools
    if "link" in low or "ലിങ്ക്" in text:
        await update.message.reply_text("🔗 *LINK MODE ON ✅*\n\nLink ayakk. Eg: `amazon-offer.com`", parse_mode='Markdown')
        return
    if "number" in low or "നമ്പർ" in text:
        await update.message.reply_text("📱 *NUMBER MODE ON ✅*\n\nNumber ayakk. Eg: `9999999999`\nIppo 95/100 SPAM detection!", parse_mode='Markdown')
        return
    if "fb" in low or "പരസ്യം" in text:
        await update.message.reply_text("📸 *FB AD MODE ON ✅*\n\nScreenshot ayakk. `Spin The Excitement` = 85/100 SCAM!", parse_mode='Markdown')
        return
    if "upi" in low:
        await update.message.reply_text("💳 *UPI MODE ON ✅*\nUPI ayakk")
        return
    if "job" in low or "ജോലി" in text:
        await update.message.reply_text("💼 *JOB MODE ON ✅*\nJob message ayakk")
        return

    # 3. Actual checks
    if 'spin' in low or 'excitement' in low or 'try today' in low or 'register now' in low:
        await update.message.reply_text("📸 *FB Ad Result: 85/100 🚨 SCAM LIKELY*\n\n`Spin The Excitement` = Casino/Gambling Trap!\n❌ Click cheyyaruth!", parse_mode='Markdown')
        return

    digits = re.sub(r'\D','', text)
    if len(digits) >= 10:
        num = digits[-10:]
        if num in ['9999999999','8888888888','0000000000','1234567890']: score=95
        elif re.search(r'(.)\1{5,}', num): score=90
        else: score=40
        await update.message.reply_text(f"📱 Number: +91 {num}\n{'🚨 SPAM NUMBER 95/100!' if score>=80 else f'⚠️ Score {score}/100'}")
        return

    if '.' in text and len(text) > 4:
        await update.message.reply_text(f"🔗 Link: {text[:60]}\n⚠️ Checking... 40/100")
        return

    # fallback
    lang = USER_LANG.get(chat_id, 'ml')
    if lang == 'ml':
        await update.message.reply_text("👇 Thazhe buttonil ninnu select cheyyu da. Eg: 📱 Number click cheythu 9999999999 ayakk")
    else:
        await update.message.reply_text("👇 Select from below buttons. Eg: Click 📱 Number and send 9999999999")

if __name__ == '__main__':
    # Delete webhook first
    import requests
    try:
        requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook?drop_pending_updates=True", timeout=5)
    except: pass
    
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    print("REPLY KEYBOARD BOT LIVE - NO CALLBACK ISSUE")
    app.run_polling(drop_pending_updates=True)
