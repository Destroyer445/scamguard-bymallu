import os, re, threading, logging
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# LOGGING ON
logging.basicConfig(level=logging.INFO)
BOT_TOKEN = os.getenv("BOT_TOKEN")
print(f"BOT_TOKEN loaded: {bool(BOT_TOKEN)} Length: {len(BOT_TOKEN) if BOT_TOKEN else 0}")

app_flask = Flask(__name__)
@app_flask.route('/')
def home(): return "ScamGuard PRO MAX Live - Bot Running!"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛡️ ScamGuard by Mallu - PRO MAX Live!\n\nMain 4:\n🔗 Link Check - link ayakk\n📱 Number Check - number ayakk\n💳 UPI/QR Check - upi ayakk\n💼 Job Check - job msg ayakk\n\nExtra 4:\n/ml Malayalam\n/report number\nAd screenshot ayakk\n/help")

async def handle_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text or ""
    if text.startswith("http") or "bit.ly" in text or "tinyurl" in text:
        await update.message.reply_text("🔍 LINK CHECK:\n⚠️ Short link! High Risk - click venda!\nTip: Expand cheythu nokku")
    elif re.search(r'\+91|^[6-9]\d{9}', text):
        await update.message.reply_text("📱 NUMBER CHECK:\n✅ Format OK\nCircle: Kerala (Example)\n⚠️ Unknown num - OTP kodukkaruthu!")
    elif "@" in text and ("ok" in text or "ybl" in text or "upi" in text):
        await update.message.reply_text("💳 UPI CHECK:\n⚠️ New UPI - first time aano? 1Rs test cheyyu!")
    elif "work from home" in text.lower() or "fee" in text.lower() or "registration" in text.lower():
        await update.message.reply_text("💼 JOB TRAP CHECK:\n🚨 SCAM! Jobinu fee chodikkilla! 100% Thattip!")
    else:
        await update.message.reply_text("✅ Message received! Link/Number/UPI/Job msg ayakk - njan check cheyyam!\n/ml - Malayalam\n/help - Help")

def run_bot():
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN missing in Render!")
        return
    print("Starting Telegram polling...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", start))
    app.add_handler(CommandHandler("ml", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_all))
    print("Bot polling started - go to Telegram and /start")
    app.run_polling()

# Start bot in thread
threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)
