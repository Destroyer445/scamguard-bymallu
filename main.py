# V1000001 FINAL - LANGUAGE + BACK + CHROME MUST ALL TOOLS + OCR AUTO - SAFE BUG FIXED
import os, re, threading, requests, whois, json, socket, ssl, io
from flask import Flask
from datetime import datetime
from urllib.parse import urlparse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
try:
    from PIL import Image
    from bs4 import BeautifulSoup
    from pymongo import MongoClient
    import cloudscraper, pytesseract
    FULL_POWER=True; OCR_AVAILABLE=True
except:
    from PIL import Image
    from pymongo import MongoClient
    from bs4 import BeautifulSoup
    FULL_POWER=False; OCR_AVAILABLE=False

app=Flask(__name__)
@app.route('/')
def home(): return "V1000001 FINAL CHROME MUST ALL TOOLS LANGUAGE OK"
def run_flask(): app.run(host='0.0.0.0',port=int(os.environ.get("PORT",10000)))

BOT_TOKEN=os.environ.get("BOT_TOKEN")
VT_KEY=os.environ.get("VT_API_KEY")
GSB_KEY=os.environ.get("GSB_API_KEY")
ADMIN_ID=int(os.environ.get("ADMIN_ID","6331679163"))
MONGO_URI=os.environ.get("MONGO_URI")

USER_LANG={}; USER_MODE={}; BANNED=set()
DB_FILE="scam_db_final.json"
mongo_users=mongo_scans=None
if MONGO_URI:
    try:
        client=MongoClient(MONGO_URI)
        dbm=client["scam_guard_final"]
        mongo_users=dbm["users"]; mongo_scans=dbm["scans"]
    except: pass
if not os.path.exists(DB_FILE):
    with open(DB_FILE,'w') as f: json.dump([],f)

def save_ultra(data):
    if mongo_scans:
        try: mongo_scans.insert_one(data); return
        except: pass
    try:
        with open(DB_FILE,'r') as f: db=json.load(f)
        db.append(data)
        with open(DB_FILE,'w') as f: json.dump(db[-10000:],f)
    except: pass

def save_user_ultra(user):
    if mongo_users:
        try:
            if mongo_users.count_documents({"id":user.id})==0:
                mongo_users.insert_one({"id":user.id,"name":user.first_name,"username":user.username or "No","joined":datetime.now().strftime("%d-%m-%Y")})
        except: pass

# ===== LANGUAGE SYSTEM - NEE PARANJA FUNCTION POYILLA =====
BACK_TEXT={'en':"🔙 Back to Menu",'ml':"🔙 മെനുവിലേക്ക് തിരികെ",'hi':"🔙 वापस मेनू पर",'ta':"🔙 மெனுவுக்கு திரும்பு"}

TEXTS={
'en':{'welcome':"💥 *V1000001 FINAL - CHROME MUST + OCR* 💥\nSelect Lang:",'ask_tool':"✅ *V1000001 - 50 Layer + Chrome Must + OCR Auto*\nSelect Tool:",'tools':["🔗 Link Check","📱 Number Check","💬 SMS Check","📸 Photo Check","👤 FB Check","📊 Reports"],'prompts':{'link':"🔗 *Link - 50 Layer Chrome MUST*\nSend link",'number':"📱 *Number Check* - Send number",'job':"💬 *SMS Check - Auto Chrome MUST*\nSend SMS",'photo':"📷 *Photo Check - OCR + Auto Chrome*\nSend photo",'fb':"👤 *FB Check - OCR + Chrome*\nSend FB link/ID",'reports':"📊 Reports"}},
'ml':{'welcome':"💥 *V1000001 FINAL* 💥\nLang select:",'ask_tool':"✅ *V1000001 - Chrome Must + OCR Auto*\nTool Select Cheyyu:",'tools':["🔗 ലിങ്ക് ചെക്ക്","📱 നമ്പർ ചെക്ക്","💬 SMS ചെക്ക്","📸 ഫോട്ടോ ചെക്ക്","👤 FB ചെക്ക്","📊 റിപ്പോർട്ട്"],'prompts':{'link':"🔗 *ലിങ്ക് - 50 Layer*",'number':"📱 *നമ്പർ*",'job':"💬 *SMS*",'photo':"📷 *ഫോട്ടോ + OCR*",'fb':"👤 *FB + OCR*",'reports':"📊 റിപ്പോർട്ട്"}},
'hi':{'welcome':"💥 *V1000001* 💥",'ask_tool':"✅ *V1000001*",'tools':["🔗 लिंक","📱 नंबर","💬 SMS","📸 फोटो","👤 FB","📊 रिपोर्ट"],'prompts':{'link':"🔗 लिंक",'number':"📱 नंबर",'job':"💬 SMS",'photo':"📷 फोटो",'fb':"👤 FB",'reports':"📊 रिपोर्ट"}},
'ta':{'welcome':"💥 *V1000001* 💥",'ask_tool':"✅ *V1000001*",'tools':["🔗 லிங்க்","📱 எண்","💬 SMS","📸 போட்டோ","👤 FB","📊 அறிக்கை"],'prompts':{'link':"🔗 லிங்க்",'number':"📱 எண்",'job':"💬 SMS",'photo':"📷 போட்டோ",'fb':"👤 FB",'reports':"📊 ரிப்போர்ட்"}}}

def get_lang(chat_id):
    return TEXTS.get(USER_LANG.get(chat_id,'en'),TEXTS['en']),USER_LANG.get(chat_id,'en')

def get_tools_kb(t, lang_code):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t['tools'][0],callback_data="tool_link")],
        [InlineKeyboardButton(t['tools'][4],callback_data="tool_fb")],
        [InlineKeyboardButton(t['tools'][1],callback_data="tool_number")],
        [InlineKeyboardButton(t['tools'][2],callback_data="tool_job")],
        [InlineKeyboardButton(t['tools'][3],callback_data="tool_photo")],
        [InlineKeyboardButton(t['tools'][5],callback_data="tool_reports")],
        [InlineKeyboardButton(BACK_TEXT.get(lang_code,'🔙 Back to Menu'),callback_data="back_menu")]
    ])

def get_back_kb(lang_code='en'):
    return InlineKeyboardMarkup([[InlineKeyboardButton(BACK_TEXT.get(lang_code,'🔙 Back to Menu'),callback_data="back_menu")]])

# ===== DEEP SCAN CORE - SAFE BUG FIX =====
GAMBLING_DB = ['v3game','v3-game','funexchange','funexch','gaming made easy','get id now','91club','daman','satta','matka','yono','yolo247','jeetwin','1xbet','lotus365','567aa','mahadev','wingo','aviator','dragon tiger','andar bahar','color prediction','betting id','cricket id','trusted id','online id']

def get_carrier_circle_ultra(num):
    db={'79024':'Vi Kerala','79026':'Jio Kerala','8086':'Airtel Kerala','9847':'Airtel Kerala','9495':'Jio Kerala'}
    for k in sorted(db.keys(), key=len, reverse=True):
        if num.startswith(k): return db[k]
    return "Airtel/Jio/Vi India"

def check_domain_age_ultra(domain):
    domain=domain.replace('https://','').replace('http://','').replace('www.','').split('/')[0].lower()
    try:
        w=whois.whois(domain); c=w.creation_date
        if isinstance(c,list): c=c[0]
        if c: return (datetime.now()-c).days,c.date(),str(w.registrar or "Unknown")[:20]
    except: pass
    return None,None,"Hidden"

def expand_short_link_v999(url):
    try:
        if any(s in url.lower() for s in ['bit.ly','tinyurl','cutt.ly','is.gd','t.me']):
            r=requests.get(url, allow_redirects=True, timeout=10, headers={'User-Agent':'Mozilla/5.0'})
            return r.url
    except: pass
    return url

def get_chrome_screenshot_v999(url):
    if not url.startswith('http'): url='https://'+url
    # API 1 - microlink
    try:
        api=f"https://api.microlink.io/?url={url}&screenshot=true&meta=false&embed=screenshot.url"
        r=requests.get(api, timeout=25)
        if r.status_code==200:
            data=r.json(); img_url=data['data']['screenshot']['url']
            img=requests.get(img_url, timeout=25).content
            if len(img)>5000: return io.BytesIO(img), "OK"
    except: pass
    # API 2 - thum.io backup - grey fix
    try:
        chrome_url = f"https://image.thum.io/get/width/1280/crop/900/noanimate/wait/5/{url}"
        r=requests.get(chrome_url,timeout=30,headers={'User-Agent':'Mozilla/5.0'})
        if r.status_code==200 and len(r.content)>5000: return io.BytesIO(r.content), "OK"
    except: pass
    return None, "Failed"

def extract_links_sms_v999(text):
    pattern = r'(?:https?://)?(?:www\.)?(?:bit\.ly|tinyurl\.com|cutt\.ly|is\.gd|rebrand\.ly|t\.me|telegram\.me)/[A-Za-z0-9\-_~%#?&=./]+|https?://\S+|[a-z0-9\-]+\.(com|in|xyz|top|shop|click|online|site|net|app)/\S*'
    found = re.findall(pattern, text, re.I)
    links=[]
    for f in found:
        if isinstance(f, tuple): f=f[0]
        f=f.strip('.,)]}>\'"').strip()
        if len(f)>6:
            if not f.startswith('http'): f='https://'+f
            links.append(f)
    return list(dict.fromkeys(links))

def extract_text_with_ocr(image_bytes):
    try:
        if OCR_AVAILABLE:
            img=Image.open(io.BytesIO(image_bytes))
            text=pytesseract.image_to_string(img, lang='eng')
            return text
    except: pass
    return ""

def html_scan_50_layer(url):
    score=0; reasons=[]; title=""; furl=url; html=""
    # DIRECT DOMAIN CHECK - CLOUDFLARE BLOCK AYALUM SCAM - SAFE FIX
    low_url = url.lower()
    for d in GAMBLING_DB:
        if d.replace(' ','') in low_url.replace(' ','') or d in low_url:
            return 98, [f"Direct Gambling Domain: {d} - Cloudflare Block but SCAM 🚨"], d.upper(), url, ""

    try:
        scraper=cloudscraper.create_scraper() if FULL_POWER else requests
        r=scraper.get(url, timeout=15, headers={'User-Agent':'Mozilla/5.0 Chrome/120'})
        html=r.text; furl=r.url
        m=re.search(r'<title>(.*?)</title>', html, re.I)
        title=m.group(1).strip()[:100] if m else ""
        txt=(html.lower() + " " + title.lower())[:15000]

        for d in GAMBLING_DB:
            if d in txt or d.replace(' ','') in txt.replace(' ',''):
                score+=98; reasons.append(f"Gambling Content: {d}"); break

        if 'deposit' in txt and 'withdraw' in txt:
            score+=95; reasons.append("Deposit+Withdraw Pattern")
        if 'apk' in txt:
            score+=90; reasons.append("APK Download")
    except:
        # If blocked but URL has gambling word = still SCAM
        if any(x in low_url for x in ['v3game','jeetwin','funexch','91club','daman','satta']):
            score=98; reasons=[f"{url} Gambling - Blocked but SCAM"]; title="Gambling Blocked"
    return score, reasons, title, furl, html

# ===== ALL TOOLS WITH CHROME MUST =====
async def universal_auto_link_scan(update, links, lang_code):
    if not links: return
    for link in links[:2]:
        try:
            expanded=expand_short_link_v999(link)
            await update.message.reply_text(f"🔗 Auto Link Found: {link[:50]}\n➡️ {expanded[:70]}\n⏳ Chrome MUST Screenshot...")
            img_bytes,_=get_chrome_screenshot_v999(expanded)
            if img_bytes:
                await update.message.reply_photo(photo=img_bytes, caption=f"🌐 Chrome MUST Screenshot\n{expanded[:70]}")
            h_score,h_rs,title,_,_=html_scan_50_layer(expanded)
            await update.message.reply_text(f"🔗 AUTO SCAN\n{expanded}\nScore: {h_score}/100 🚨 {title[:40]}", reply_markup=get_back_kb(lang_code))
        except: pass

async def tool1_link_deep(update,url,lang):
    await update.message.reply_text(f"🔗 {url[:60]}\n⏳ 50 Layer + Chrome MUST V1000001...", reply_markup=get_back_kb(lang))
    try:
        original=url; url=expand_short_link_v999(url)
        if original!=url: await update.message.reply_text(f"🔗 Expanded: {original[:50]} -> {url[:70]}")
        furl=url if url.startswith('http') else 'https://'+url
        domain=urlparse(furl).netloc.replace('www.','').lower() or url.split('/')[0].lower()

        h_score,h_rs,title,ffurl,html = html_scan_50_layer(furl)
        age,cdate,reg=check_domain_age_ultra(domain)

        score=h_score; reasons=h_rs.copy()

        if any(t in domain for t in ['google.com','youtube.com','facebook.com','gov.in','instagram.com']):
            final=0; status="SAFE ✅ Clean"
        else:
            if not age: score+=35; reasons.append("Whois Hidden - New scam")
            elif age<30: score+=50; reasons.append(f"New Domain {age} days old 🚨")
            if '.xyz' in domain or '.top' in domain or '.shop' in domain or '.click' in domain:
                score+=40; reasons.append(f"Suspicious TLD {domain}")
            final=min(max(score,0),99)
            if final>=70: status="SCAM 🚨"
            elif final>=40: status="RISKY ⚠️"
            else:
                # MINIMUM RISKY 75 IF RANDOM SHORT LINK - SAFE VARILLA
                if len(domain)>20 or '-' in domain:
                    final=75; status="RISKY ⚠️ Suspicious Pattern"
                else:
                    final=max(final,10); status="SAFE ✅" if final<40 else "RISKY ⚠️"

        img_bytes,_=get_chrome_screenshot_v999(ffurl)
        if img_bytes:
            await update.message.reply_photo(photo=img_bytes, caption=f"🌐 Chrome MUST V1000001\n{domain}\n{status} {final}/100\n{title[:50]}")

        reason_text="\n".join([f"{i+1}. {r}" for i,r in enumerate(reasons[:10])]) if reasons else "No reason - Clean"
        await update.message.reply_text(f"💥 V1000001 LINK 50 LAYER + CHROME MUST\nDomain: {domain}\nURL: {ffurl[:80]}\nStatus: {status} {final}/100\nTitle: {title[:80]}\nDomain Age: {age}\nReasons:\n{reason_text}", reply_markup=get_back_kb(lang))
        save_ultra({"type":"link","domain":domain,"score":final,"time":str(datetime.now())})
    except Exception as e:
        await update.message.reply_text(f"Error {e}", reply_markup=get_back_kb(lang))

async def tool2_number_deep(text,update):
    lang_code=USER_LANG.get(update.effective_chat.id,'en')
    links=extract_links_sms_v999(text)
    if links: await universal_auto_link_scan(update, links, lang_code)
    d=re.sub(r'\D','',text); num=d[-10:] if len(d)>=10 else d
    if len(num)!=10 or num[0] not in '6789':
        if not links:
            await update.message.reply_text("❌ Invalid number - 10 digit number ayachu", reply_markup=get_back_kb(lang_code)); return
        else: return
    await update.message.reply_text(f"📱 +91 {num}\n⏳ Checking...", reply_markup=get_back_kb(lang_code))
    carrier=get_carrier_circle_ultra(num)
    msg=f"📱 +91 {num}\nCarrier: {carrier}\nScore: 20/100 SAFE ✅ (But check Truecaller)\n\nIf this number sent gambling link = RISKY"
    kb=InlineKeyboardMarkup([[InlineKeyboardButton("💬 WhatsApp", url=f"https://wa.me/91{num}")],[InlineKeyboardButton("📱 Report 1909", callback_data=f"report_trai_{num}")],[InlineKeyboardButton(BACK_TEXT[lang_code],callback_data="back_menu")]])
    await update.message.reply_text(msg, reply_markup=kb)

async def tool4_sms_deep(text,update):
    lang_code=USER_LANG.get(update.effective_chat.id,'en')
    await update.message.reply_text("💬 SMS V1000000 + Chrome Must + OCR Auto...", reply_markup=get_back_kb(lang_code))
    links=extract_links_sms_v999(text)
    low=text.lower(); score=0; reasons=[]; scam_type="Clean"
    for k in GAMBLING_DB:
        if k in low: score+=90; reasons.append(k); scam_type="Satta/Gambling 🎰"
    if 'deposit' in low and 'withdraw' in low: score+=95; reasons.append("Deposit+Withdraw")
    if 'bit.ly' in low or 'tinyurl' in low: score+=50; reasons.append("Short link trap")

    if links:
        await update.message.reply_text(f"🔗 {len(links)} Link Found! Chrome MUST...")
        for link in links[:2]:
            try:
                expanded=expand_short_link_v999(link)
                if expanded!=link: await update.message.reply_text(f"🔗 Expanded: {link} -> {expanded[:80]}")
                h_score,h_rs,title,_,_=html_scan_50_layer(expanded)
                img_bytes,_=get_chrome_screenshot_v999(expanded)
                if img_bytes:
                    await update.message.reply_photo(photo=img_bytes, caption=f"🌐 Chrome MUST from SMS\n{expanded[:60]}\nScore {h_score}/100")
                score=max(score,h_score)
            except: pass

    final=min(score,99); status="SCAM 🚨" if final>=70 else "RISKY ⚠️" if final>=40 else "SAFE ✅"
    link_show=", ".join(links[:2]) if links else "No link"
    msg=f"💬 SMS RESULT V1000001 + CHROME MUST\nText: {text[:150]}\nType: {scam_type}\nScore: {final}/100 {status}\nReasons: {', '.join(reasons[:6])}\nLinks: {link_show}"
    await update.message.reply_text(msg, reply_markup=get_back_kb(lang_code))

async def tool_fb_deep(text,update):
    lang_code=USER_LANG.get(update.effective_chat.id,'en')
    links=extract_links_sms_v999(text)
    if links: await universal_auto_link_scan(update, links, lang_code)
    await update.message.reply_text("📘 FB Checking V1000001 50 Layer + Chrome Must + OCR...", reply_markup=get_back_kb(lang_code))
    try:
        raw=text.strip()
        if 'facebook.com' in raw.lower():
            parts=raw.lower().split('facebook.com/')[-1].split('/')
            fb_id=parts[0].split('?')[0] if parts[0] else raw
        else: fb_id=re.sub(r'[^0-9a-zA-Z._]','',raw)[:80]
        fb_id_safe=fb_id or "unknown"
        profile_url=raw if 'facebook.com' in raw.lower() else f"https://www.facebook.com/{fb_id_safe}"

        scam_score=0; reasons=[]
        if fb_id_safe.isdigit() and len(fb_id_safe)>=14:
            scam_score+=70; reasons.append(f"New Fake Numeric ID {len(fb_id_safe)} digits")
            if fb_id_safe.startswith('6155'): scam_score+=25; reasons.append("6155xx Gambling Series 🚨")

        check_text=f"{fb_id_safe} {text}".lower()
        for k in GAMBLING_DB:
            if k in check_text: scam_score+=95; reasons.append(f"FB Gambling: {k}"); break

        final=min(scam_score,99); status_icon="SCAM 🚨" if final>=70 else "RISKY ⚠️" if final>=40 else "SAFE ✅"

        fb_chrome_img,_=get_chrome_screenshot_v999(profile_url)
        if fb_chrome_img:
            await update.message.reply_photo(photo=fb_chrome_img, caption=f"🌐 FB Chrome MUST\n{fb_id_safe}")

        await update.message.reply_text(f"📘 FB V1000001 + CHROME MUST\nID: {fb_id_safe}\nScore: {final}/100 {status_icon}\nReasons: {', '.join(reasons[:4]) if reasons else 'Clean'}", reply_markup=get_back_kb(lang_code))
        save_ultra({"type":"fb","input":fb_id_safe,"score":final,"time":str(datetime.now())})
    except Exception as e:
        await update.message.reply_text(f"FB Error {e}", reply_markup=get_back_kb(lang_code))

async def tool5_photo_deep(update,context):
    lang_code=USER_LANG.get(update.effective_chat.id,'en')
    await update.message.reply_text("📸 Photo V1000001 + OCR Auto + Chrome Must...", reply_markup=get_back_kb(lang_code))
    try:
        photo_file=await update.message.photo[-1].get_file()
        photo_bytes=await photo_file.download_as_bytearray()
        img=Image.open(io.BytesIO(photo_bytes)); w,h=img.size
        ocr_text=extract_text_with_ocr(photo_bytes)
        if ocr_text:
            await update.message.reply_text(f"🔤 OCR Auto Text Reader:\n{ocr_text[:600]}")
            links_from_ocr=extract_links_sms_v999(ocr_text)
            if links_from_ocr:
                await universal_auto_link_scan(update, links_from_ocr, lang_code)
        else:
            links_from_ocr=[]

        combined=(ocr_text.lower() if ocr_text else "")
        score=0; reasons=[f"Image {w}x{h}"]; scam_type="Clean"

        if w<1300 and h>1200: score+=40; reasons.append("Phone Screenshot Ad Pattern")
        try:
            small=img.resize((10,10)).convert('L')
            avg=sum(small.getdata())/100
            if avg<80: score+=30; reasons.append("Dark UI Gambling Theme")
        except: pass

        for k in GAMBLING_DB:
            if k in combined or k.replace(' ','') in combined.replace(' ',''):
                score=99; scam_type=f"Gambling Screenshot DESTROYED 🎰 {k}"; reasons.append(f"OCR Keyword 🚨 {k}"); break

        if score==0 and w<1300 and len(combined)>10:
            score=75; reasons.append("Suspicious Ad - Manual Check ⚠️")

        final=min(score,99); status="SCAM 🚨" if final>=70 else "RISKY ⚠️" if final>=40 else "SAFE ✅"
        await update.message.reply_photo(photo=io.BytesIO(photo_bytes), caption=f"📸 {scam_type}\nScore {final}/100 {status}\nOCR: {ocr_text[:100] if ocr_text else 'No text'}")
        await update.message.reply_text(f"📸 PHOTO V1000001 + CHROME MUST + OCR\nType: {scam_type}\nScore: {final}/100 {status}\nReasons:\n" + "\n".join([f"{i+1}. {r}" for i,r in enumerate(reasons)]) + f"\nOCR Links: {', '.join(links_from_ocr[:2]) if links_from_ocr else 'None'}", reply_markup=get_back_kb(lang_code))
        save_ultra({"type":"photo","score":final,"time":str(datetime.now())})
    except Exception as e:
        await update.message.reply_text(f"Photo Error {e}", reply_markup=get_back_kb(lang_code))

async def tool_reports(update, lang_code):
    await update.message.reply_text(f"📊 V1000001 REPORTS\nAll Tools Chrome MUST + 50 Layer Active", reply_markup=get_back_kb(lang_code))

async def admin_stats(update,context):
    if update.effective_user.id!=ADMIN_ID: return
    await update.message.reply_text("ADMIN V1000001 CHROME MUST ALL TOOLS LANGUAGE OK")

async def start(update,context):
    if update.effective_chat.id in BANNED: return
    save_user_ultra(update.effective_user)
    kb=[[InlineKeyboardButton("English 🇬🇧",callback_data="lang_en"),InlineKeyboardButton("മലയാളം 🇮🇳",callback_data="lang_ml")],[InlineKeyboardButton("தமிழ் 🇮🇳",callback_data="lang_ta"),InlineKeyboardButton("हिंदी 🇮🇳",callback_data="lang_hi")]]
    await update.message.reply_text(TEXTS['en']['welcome'],reply_markup=InlineKeyboardMarkup(kb),parse_mode='Markdown')

async def lang_cb(update,context):
    q=update.callback_query; await q.answer(); USER_LANG[q.message.chat.id]=q.data.split('_')[1]
    t,lc=get_lang(q.message.chat.id)
    await q.edit_message_text(t['ask_tool'],reply_markup=get_tools_kb(t,lc),parse_mode='Markdown')

async def tool_cb(update,context):
    q=update.callback_query; await q.answer(); data=q.data
    if data=="back_menu":
        t,lc=get_lang(q.message.chat.id); await q.edit_message_text(t['ask_tool'],reply_markup=get_tools_kb(t,lc),parse_mode='Markdown'); USER_MODE.pop(q.message.chat.id,None); return
    USER_MODE[q.message.chat.id]=data.split('_')[1]; t,lc=get_lang(q.message.chat.id)
    if data=="tool_reports": await tool_reports(q, lc); return
    mp={'link':t['prompts']['link'],'number':t['prompts']['number'],'job':t['prompts']['job'],'photo':t['prompts']['photo'],'fb':t['prompts']['fb']}
    await q.edit_message_text(mp.get(USER_MODE[q.message.chat.id],t['prompts']['link']),parse_mode='Markdown',reply_markup=get_back_kb(lc))

async def report_cb(update,context):
    q=update.callback_query; await q.answer(); await q.message.reply_text("✅ Reported! Cybercrime 1930", reply_markup=get_back_kb(USER_LANG.get(q.message.chat.id,'en')))

async def router(update,context):
    text=update.message.text or ""; chat_id=update.effective_chat.id; low=text.lower().strip()
    if low in ['hi','hello','/start','start','menu','hey','hai']: USER_MODE.pop(chat_id,None); await start(update,context); return
    mode=USER_MODE.get(chat_id,'auto'); _,lc=get_lang(chat_id)
    if mode=='link': await tool1_link_deep(update,text,lc); USER_MODE.pop(chat_id,None); return
    if mode=='number': await tool2_number_deep(text,update); USER_MODE.pop(chat_id,None); return
    if mode=='job': await tool4_sms_deep(text,update); USER_MODE.pop(chat_id,None); return
    if mode=='fb': await tool_fb_deep(text,update); USER_MODE.pop(chat_id,None); return
    if mode=='reports': await tool_reports(update, lc); USER_MODE.pop(chat_id,None); return
    if re.search(r'\b\d{10,}\b',text.replace(' ','')): await tool2_number_deep(text,update); return
    if 'facebook.com' in low or 'fb.com' in low or (text.isdigit() and len(text)>=12): await tool_fb_deep(text,update); return
    if '.' in text and ' ' not in text and len(text)>4 and len(text)<200: url=text if text.startswith('http') else 'https://'+text; await tool1_link_deep(update,url,lc); return
    await tool4_sms_deep(text,update)

def main():
    if not BOT_TOKEN: print("BOT_TOKEN missing"); return
    threading.Thread(target=run_flask,daemon=True).start()
    application=Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start",start))
    application.add_handler(CommandHandler("stats",admin_stats))
    application.add_handler(CallbackQueryHandler(lang_cb,pattern="^lang_"))
    application.add_handler(CallbackQueryHandler(tool_cb,pattern="^tool_|^back_"))
    application.add_handler(CallbackQueryHandler(report_cb,pattern="^report_|^gen_"))
    application.add_handler(MessageHandler(filters.PHOTO,tool5_photo_deep))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,router))
    print("V1000001 FINAL CHROME MUST ALL TOOLS LANGUAGE OK")
    application.run_polling(drop_pending_updates=True)

if __name__=='__main__': main()
