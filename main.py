import os, re, threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")
USER_LANG = {}
flask_app = Flask(__name__)
@flask_app.route('/')
def home(): return "ScamGuard 4Lang 8Feat Live!"

# --- KEYBOARDS ---
def lang_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("English 🇬🇧", callback_data="lang_en"), InlineKeyboardButton("മലയാളം 🇮🇳", callback_data="lang_ml")],
        [InlineKeyboardButton("தமிழ்", callback_data="lang_ta"), InlineKeyboardButton("हिंदी", callback_data="lang_hi")]
    ])

def tool_kb(lang='ml'):
    if lang=='ml':
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 Link Check", callback_data="tool_link"), InlineKeyboardButton("📱 Number 95/100", callback_data="tool_num")],
            [InlineKeyboardButton("💳 UPI", callback_data="tool_upi"), InlineKeyboardButton("💼 Job Scam", callback_data="tool_job")],
            [InlineKeyboardButton("📸 FB Ad 85/100", callback_data="tool_fb"), InlineKeyboardButton("🏦 Loan", callback_data="tool_loan")],
            [InlineKeyboardButton("🎰 Lottery", callback_data="tool_lot"), InlineKeyboardButton("🛒 Shopping", callback_data="tool_shop")]
        ])
    else:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 Link", callback_data="tool_link"), InlineKeyboardButton("📱 Number", callback_data="tool_num")],
            [InlineKeyboardButton("💳 UPI", callback_data="tool_upi"), InlineKeyboardButton("💼 Job", callback_data="tool_job")],
            [InlineKeyboardButton("📸 FB Ad", callback_data="tool_fb"), InlineKeyboardButton("🏦 Loan", callback_data="tool_loan")],
            [InlineKeyboardButton("🎰 Lottery", callback_data="tool_lot"), InlineKeyboardButton("🛒 Shopping", callback_data="tool_shop")]
        ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🛡️ *Scam Guard India*\nYour anti-scam shield. Select language:", reply_markup=lang_kb(), parse_mode='Markdown')

async def cb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    cid = q.message.chat_id
    data = q.data
    if data.startswith("lang_"):
        lang = data.split("_")[1]
        USER_LANG[cid]=lang
        msg = {"ml":"✅ മലയാളം! താഴെ 8 ഫീച്ചർ 👇","en":"✅ English! 8 Features below 👇","ta":"✅ தமிழ்!","hi":"✅ हिंदी!"}[lang]
        await q.edit_message_text(msg, reply_markup=tool_kb(lang))
    elif data.startswith("tool_"):
        msgs = {
            "tool_link":"🔗 *LINK MODE ON*\nLink ayakk: amazon-offer.com",
            "tool_num":"📱 *NUMBER MODE ON - 95/100 LOGIC ACTIVE*\nNumber ayakk: 9999999999",
            "tool_upi":"💳 *UPI MODE ON*\nUPI ayakk: test@okaxis",
            "tool_job":"💼 *JOB MODE ON*\nMsg ayakk: Work from home earn 5000",
            "tool_fb":"📸 *FB AD MODE - 85/100 LOGIC ACTIVE*\nText ayakk: Spin The Excitement - Register Now",
            "tool_loan":"🏦 *LOAN MODE ON*",
            "tool_lot":"🎰 *LOTTERY MODE ON*",
            "tool_shop":"🛒 *SHOPPING MODE ON*"
        }
        await q.message.reply_text(msgs.get(data,"Mode ON"), parse_mode='Markdown')

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (update.message.text or "").strip()
    cid = update.effective_chat.id
    low = text.lower()
    if not text or text.startswith("/"): return

    # 8 FEATURE LOGIC
    # 1. FB AD 85/100
    if any(x in low for x in ['spin','excitement','register now','try today','fortune awaits']):
        await update.message.reply_text("📸 *85/100 🚨 SCAM LIKELY*\n`Spinning Trap` Casino Ad!\n❌ Click cheyyaruth! Block!", parse_mode='Markdown'); return
    # 2. NUMBER 95/100
    digits = re.sub(r'\D','', text)
    if len(digits)>=10:
        num = digits[-10:]
        if num in ['9999999999','8888888888','0000000000','1234567890'] or re.search(r'(.)\1{5,}', num):
            await update.message.reply_text(f"📱 +91 {num}\n🚨 *95/100 HIGH SPAM!*\nFake / Promo Number!"); return
        await update.message.reply_text(f"📱 +91 {num}\n✅ 40/100 Safe-ish"); return
    # 3. UPI
    if '@' in text and any(x in low for x in ['okaxis','okicici','oksbi','ybl','upi']):
        await update.message.reply_text(f"💳 UPI: {text}\n⚠️ 50/100 - Verify before pay!"); return
    # 4. LINK
    if '.' in text and ('http' in low or len(text)<70):
        sc = 80 if any(x in low for x in ['offer','free','win','prize','amazon-offer']) else 30
        await update.message.reply_text(f"🔗 {text[:60
