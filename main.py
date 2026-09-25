import os, re
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")
USER_LANG = {}

# 4 Language Keyboard
LANG_KB = ReplyKeyboardMarkup([["English 🇬🇧", "മലയാളം 🇮🇳"], ["தமிழ்", "हिंदी"]], resize_keyboard=True, one_time_keyboard=True)

# 8 Features Keyboard
TOOL_KB_ML = ReplyKeyboardMarkup([
    ["🔗 Link", "📱 Number"],
    ["💳 UPI", "💼 Job"],
    ["📸 FB Ad", "🏦 Loan"],
    ["🎰 Lottery", "🛒 Shopping"]
], resize_keyboard=True)
TOOL_KB_EN = ReplyKeyboardMarkup([
    ["🔗 Link", "📱 Number"],
    ["💳 UPI", "💼 Job"],
    ["📸 FB Ad", "🏦 Loan"],
    ["🎰 Lottery", "🛒 Shopping"]
], resize_keyboard=True)

def t(chat_id, ml, en, ta=None, hi=None):
    l = USER_LANG.get(chat_id, 'ml')
    if l == 'en': return en
    if l == 'ta': return ta or en
    if l == 'hi': return hi or en
    return ml

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛡️ *Scam Guard India*\n\n4 Language | 8 Scam Check\n\nSelect Language / ഭാഷ തിരഞ്ഞെടുക്കൂ 👇",
        reply_markup=LANG_KB, parse_mode='Markdown')

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    chat_id = update.effective_chat.id
    low = text.lower()

    # LANGUAGE SELECT - Reply keyboard so 100% works
    if "മലയാളം" in text: USER_LANG[chat_id]='ml'; await update.message.reply_text("✅ മലയാളം!\n\n8 ഫീച്ചർ താഴെ 👇", reply_markup=TOOL_KB_ML); return
    if "english" in low: USER_LANG[chat_id]='en'; await update.message.reply_text("✅ English!\n\n8 Features below 👇", reply_markup=TOOL_KB_EN); return
    if "தமிழ்" in text or "tamil" in low: USER_LANG[chat_id]='ta'; await update.message.reply_text("✅ தமிழ்!", reply_markup=TOOL_KB_EN); return
    if "हिंदी" in text or "hindi" in low: USER_LANG[chat_id]='hi'; await update.message.reply_text("✅ हिंदी!", reply_markup=TOOL_KB_EN); return
    if text.startswith("/start"): await start(update, context); return

    # FEATURE SELECT
    if "link" in low: await update.message.reply_text(t(chat_id, "🔗 *LINK MODE ON*\nLink ayakk: amazon-offer.com", "🔗 *LINK MODE ON*\nSend link: amazon-offer.com")); return
    if "number" in low or "നമ്പർ" in text: await update.message.reply_text(t(chat_id, "📱 *NUMBER MODE ON - 95/100 SPAM LOGIC ACTIVE*\nNumber ayakk: 9999999999", "📱 *NUMBER MODE ON*\nSend number: 9999999999")); return
    if "upi" in low: await update.message.reply_text(t(chat_id, "💳 *UPI MODE*\nUPI ayakk: user@okaxis", "💳 *UPI MODE*\nSend UPI: user@okaxis")); return
    if "job" in low or "ജോലി" in text: await update.message.reply_text(t(chat_id, "💼 *JOB SCAM MODE*\nJob msg ayakk", "💼 *JOB SCAM MODE*\nSend job msg")); return
    if "fb" in low or "പരസ്യം" in text or "ad" in low: await update.message.reply_text(t(chat_id, "📸 *FB AD MODE - 85/100 LOGIC ACTIVE*\nScreenshot text ayakk: Spin The Excitement", "📸 *FB AD MODE*\nSend ad text: Spin The Excitement")); return
    if "loan" in low or "വായ്പ" in text: await update.message.reply_text(t(chat_id, "🏦 *LOAN MODE*\nLoan msg ayakk", "🏦 *LOAN MODE*\nSend loan msg")); return
    if "lottery" in low or "ലോട്ടറി" in text: await update.message.reply_text(t(chat_id, "🎰 *LOTTERY MODE*\nLottery msg ayakk", "🎰 *LOTTERY MODE*\nSend lottery msg")); return
    if "shop" in low or "ഷോപ്പിംഗ്" in text: await update.message.reply_text(t(chat_id, "🛒 *SHOPPING MODE*\nShopping link ayakk", "🛒 *SHOPPING MODE*\nSend shopping link")); return

    # --- 8 FEATURE DETECTION LOGIC ---
    # 1. FB Ad 85/100 - Spin The Excitement
    if any(x in low for x in ['spin','excitement','register now','try today','fortune awaits']):
        await update.message.reply_text(f"📸 *Result: 85/100 🚨 SCAM LIKELY*\n\n`t(Spinning Trap)` Casino Ad!\n{t(chat_id, '❌ Click cheyyaruth!', '❌ Do not click!')}", parse_mode='Markdown'); return

    # 2. Number 95/100
    digits = re.sub(r'\D','', text)
    if len(digits) >= 10:
        num = digits[-10:]
        if num in ['9999999999','8888888888','0000000000','1234567890'] or re.search(r'(.)\1{5,}', num):
            await update.message.reply_text(f"📱 +91 {num}\n🚨 *95/100 HIGH SPAM!*\n{t(chat_id,'Fake number!','Fake number!')}", parse_mode='Markdown'); return
        else:
            await update.message.reply_text(f"📱 +91 {num}\n✅ 40/100 Safe-ish"); return

    # 3. UPI
    if '@' in text and any(x in low for x in ['okaxis','okicici','oksbi','okhdfc','ybl','upi']):
        await update.message.reply_text(f"💳 UPI: {text[:30]}\n⚠️ 50/100 Check sender!"); return

    # 4. Link
    if '.' in text and ('http' in low or len(text)<60):
        score = 80 if any(x in low for x in ['offer','free','win','prize','amazon-offer','flipkart-offer']) else 40
        await update.message.reply_text(f"🔗 {text[:50]}\n{'🚨' if score>60 else '✅'} {score}/100"); return

    # 5-8. Others
    if any(x in low for x in ['job','work from home','earn 5000','typing job']): await update.message.reply_text("💼 Job: 🚨 75/100 Likely Scam - Advance fee?"); return
    if any(x in low for x in ['loan','instant loan','low cibil']): await update.message.reply_text("🏦 Loan: 🚨 80/100 Check RBI registered?"); return
    if any(x in low for x in ['lottery','kbc','you won','congratulations']): await update.message.reply_text("🎰 Lottery: 🚨 90/100 SCAM!"); return
    if any(x in low for x in ['shopping','big sale','90% off']): await update.message.reply_text("🛒 Shopping: ⚠️ 60/100 Check COD?"); return

    await update.message.reply_text(t(chat_id, "👇 Thazhe button select cheyyu", "👇 Select button below"), reply_markup=TOOL_KB_ML if USER_LANG.get(chat_id)=='ml' else TOOL_KB_EN)

if __name__ == '__main__':
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, handle))
    print("4 LANG 8 FEATURE BOT LIVE")
    app.run_polling(drop_pending_updates=True)
