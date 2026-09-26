import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
print(f"BOT_TOKEN loaded: {bool(BOT_TOKEN)} Length: {len(BOT_TOKEN) if BOT_TOKEN else 0}")

app = Flask(__name__)

@app.route('/')
def home():
    return "Scam Guard Bot is Running!"

@app.route('/health')
def health():
    return "OK", 200

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛡️ Welcome to Scam Guard India!\n\n"
        "Send me any link and I will check if it's scam or safe!\n"
        "Just paste the link here!"
    )

async def check_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "http" in text.lower() or "www" in text.lower():
        await update.message.reply_text(f"🔍 Checking link:\n{text}\n\n✅ Analysis: This looks safe! (Demo)\n\nSend another link to check!")
    else:
        await update.message.reply_text("Please send a valid link! Ex: https://google.com")

def run_flask():
    app.run(host='0.0.0.0', port=10000)

async def run_bot():
    print("Starting Telegram polling...")
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_link))
    print("Bot polling started SUCCESS!")
    await application.run_polling()

def main():
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    import asyncio
    asyncio.run(run_bot())

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("ERROR: BOT_TOKEN missing!")
    else:
        main()
