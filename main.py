import telebot
import re

BOT_TOKEN = "8859624294:AAFq2fI5Yi7f1oJa34DWE-EaBL-ovwNTIZs"

bot = telebot.TeleBot(BOT_TOKEN)

# 4 Language Keywords
SCAM_WORDS = ["lottery", "prize", "kyc blocked", "urgent payment", "bank account blocked", "lottery adichu", "sammാനം", "urgent", "click link"]

@bot.message_handler(commands=['start'])
def start(m):
    bot.reply_to(m, "🛡️ SCAM GUARD INDIA BOT By Mallu 🇮🇳\n\nAarum pattikkanda! Oru link/msg ayachaa njan check cheyyum!\n\nJust forward any suspicious message!")

@bot.message_handler(func=lambda m: True)
def check_scam(m):
    text = m.text.lower()
    is_scam = any(word in text for word in SCAM_WORDS) or "http" in text and ("bit.ly" in text or "tinyurl" in text)
    
    if is_scam:
        bot.reply_to(m, "🚨 **DANGER! SCAM AANU!** 🚨\n\n❌ Click cheyyaruthu!\n❌ Cash ayakkaruthu!\n\nIthu fraud aanu aliya!\n\n✅ Safe: Bank-il direct vilikku", parse_mode="Markdown")
    else:
        bot.reply_to(m, "✅ Safe aanu ennu thonnunnu. But doubt undeel bank-il vilichu confirm cheyyu aliya!")

print("Bot Started...")
bot.infinity_polling()
