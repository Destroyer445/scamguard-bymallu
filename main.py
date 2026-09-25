import os, re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")
USER_LANG = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [
        [InlineKeyboardButton("English 🇬🇧", callback_data="en"), InlineKeyboardButton("മലയാളം 🇮🇳", callback_data="ml")],
        [InlineKeyboardButton("தமிழ்", callback_data="ta"), InlineKeyboardButton("हिंदी", callback_data="hi")]
    ]
    await update.message.reply_text("🛡️ Scam Guard India\nSelect language / ഭാഷ തിരഞ്ഞെടുക്കൂ:", reply_markup=InlineKeyboardMarkup(kb))

async def btn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer("Loading...") # ithu must aanu
    d = q.data
    
    if d in ['en','ml','ta','hi']:
        USER_LANG[q.message.chat.id] = d
        kb2 = [
            [InlineKeyboardButton("🔗 Link", callback_data="link"), InlineKeyboardButton("📱 Number 9999 test", callback_data="number")],
            [InlineKeyboardButton("📸 FB Ad", callback_data="ad")]
        ]
        langtxt = "✅ Malayalam set! Thazhe click cheyyu" if d=='ml' else f"✅ {d} set! Click below"
        await q.edit_message_text(f"{langtxt}\n\n👇 What to check?", reply_markup=InlineKeyboardMarkup(kb2))
    elif d == 'link':
        await q.edit_message_text("🔗 LINK MODE ON ✅\nLink ayakk - eg: offer.com")
    elif d == 'number':
        await q.edit_message_text("📱 NUMBER MODE ON ✅\nNumber ayakk - eg: 9999999999\nIppo 95/100 SPAM varum!")
    elif d == 'ad':
        await q.edit_message_text("📸 FB AD MODE ON ✅\nScreenshot ayakk - Spin The Excitement = 85/100 SCAM!")

async def text_handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = update.message.text or ""
    digits = re.sub(r'\D','',txt)
    if len(digits)>=10:
        n = digits[-10:]
        sc = 95 if n=='9999999999' else 90
        await update.message.reply_text(f"📱 {n} => 🚨 SPAM {sc}/100")
    elif 'spin' in txt.lower() or 'excitement' in txt.lower():
        await update.message.reply_text("📸 FB Ad => 🚨 85/100 SCAM!")
    else:
        await update.message.reply_text(f"Received: {txt}")

if __name__ == '__main__':
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(btn))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handle))
    app.run_polling()
