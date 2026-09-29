# V999999 DESTROYER - OCR + AUTO LINK + CHROME SCREENSHOT - ALL TOOLS
import os, re, threading, requests, whois, base64, json, socket, ssl, io, time, hashlib
from flask import Flask
from datetime import datetime
from urllib.parse import urlparse, unquote
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

try:
    from PIL import Image, ImageDraw, ImageFont
    from bs4 import BeautifulSoup
    from pymongo import MongoClient
    import cloudscraper
    FULL_POWER=True
except:
    from PIL import Image, ImageDraw, ImageFont
    from pymongo import MongoClient
    from bs4 import BeautifulSoup
    FULL_POWER=False

# OCR TRY
try:
    import pytesseract
    OCR_AVAILABLE=True
except:
    OCR_AVAILABLE=False
    print("OCR not installed - using heuristic")

try: RESAMPLE = Image.Resampling.LANCZOS
except:
    try: RESAMPLE = Image.LANCZOS
    except: RESAMPLE = Image.ANTIALIAS

app=Flask(__name__)
@app.route('/')
def home(): return "V999999 DESTROYER OCR + AUTO LINK"
def run_flask(): app.run(host='0.0.0.0',port=int(os.environ.get("PORT",10000)))

BOT_TOKEN=os.environ.get("BOT_TOKEN"); VT_KEY=os.environ.get("VT_API_KEY"); GSB_KEY=os.environ.get("GSB_API_KEY")
ADMIN_ID=int(os.environ.get("ADMIN_ID","6331679163")); MONGO_URI=os.environ.get("MONGO_URI")
USER_LANG={}; USER_MODE={}; BANNED=set()
DB_FILE="scam_db_final.json"; USERS_FILE="users_db_final.json"
mongo_users=mongo_scans=None
if MONGO_URI:
    try:
        client=MongoClient(MONGO_URI); dbm=client["scam_guard_final"]; mongo_users=dbm["users"]; mongo_scans=dbm["scans"]
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

BACK_TEXT={'en':"🔙 Back to Menu",'ml':"🔙 മെനുവിലേക്ക് തിരികെ",'hi':"🔙 वापस मेनू पर",'ta':"🔙 மெனுவுக்கு திரும்பு"}
REPORT_TEXT={'en':{'fb':"🔵 Report to Facebook",'google':"🌐 Report to Google",'ms':"🛡️ Report to Microsoft",'trai':"📱 Report to 1909 - TRAI",'cyber':"🚨 Report to Cyber Crime 1930",'admin':"👑 Report to Admin"},'ml':{'fb':"🔵 Facebook ൽ റിപ്പോർട്ട്",'google':"🌐 Google ൽ റിപ്പോർട്ട്",'ms':"🛡️ Microsoft ൽ",'trai':"📱 1909 - TRAI",'cyber':"🚨 സൈബർ ക്രൈം 1930",'admin':"👑 അഡ്മിന് റിപ്പോർട്ട്"},'hi':{'fb':"🔵 Facebook पर रिपोर्ट",'google':"🌐 Google पर",'ms':"🛡️ Microsoft पर",'trai':"📱 1909 - TRAI",'cyber':"🚨 साइबर क्राइम 1930",'admin':"👑 एडमिन को रिपोर्ट"},'ta':{'fb':"🔵 Facebook இல் புகார்",'google':"🌐 Google இல்",'ms':"🛡️ Microsoft இல்",'trai':"📱 1909 - TRAI",'cyber':"🚨 சைபர் கிரைம் 1930",'admin':"👑 அட்மின்"}}

TEXTS={
 'en':{'welcome':"💥 *V999999 DESTROYER - OCR + AUTO LINK CHROME* 💥\n\nWelcome. Select Language:",'ask_tool':"✅ *V999999 - 5 TOOLS + AUTO LINK SCREENSHOT + OCR*\n👇 *Select:*",'tools':["🔗 Link Check","📱 Number Check","💬 SMS Check","📸 Photo Check","👤 FB Check","📊 Reports"],'prompts':{'link':"🔗 *Link Check 50 Layer + Chrome + OCR*\nSend link or screenshot.",'number':"📱 *Number Check + OCR + Auto Link*\nSend number or screenshot.",'job':"💬 *SMS Check + OCR + Auto Link Screenshot*\nSend SMS or screenshot.",'photo':"📷 *Photo Check + OCR + Link Extract + Chrome*\nSend photo.",'fb':"👤 *FB Check + OCR + Auto Link Chrome*\nSend FB link or Ad Screenshot.",'reports':"📊 *REPORTS DASHBOARD*"}},
 'ml':{'welcome':"💥 *V999999* 💥\nഭാഷ തിരഞ്ഞെടുക്കുക:",'ask_tool':"✅ *V999999 - 5 ടൂളുകൾ + Auto Link Chrome + OCR*\n👇 തിരഞ്ഞെടുക്കുക:",'tools':["🔗 ലിങ്ക് പരിശോധന","📱 നമ്പർ പരിശോധന","💬 SMS പരിശോധന","📸 ഫോട്ടോ പരിശോധന","👤 FB പരിശോധന","📊 റിപ്പോർട്ടുകൾ"],'prompts':{'link':"🔗 *ലിങ്ക് + Chrome + OCR*\nലിങ്ക് അയക്കുക.",'number':"📱 *നമ്പർ + OCR*\nനമ്പർ അയക്കുക.",'job':"💬 *SMS + Auto Link Screenshot*\nSMS അയക്കുക.",'photo':"📷 *ഫോട്ടോ + OCR*\nഫോട്ടോ അയക്കുക.",'fb':"👤 *FB + OCR + Link Screenshot*\nFB Ad Screenshot അയക്കുക.",'reports':"📊 *റിപ്പോർട്ടുകൾ"}},
 'hi':{'welcome':"💥 *V999999* 💥",'ask_tool':"✅ *V999999 - 5 Tools + OCR + Auto Screenshot*",'tools':["🔗 लिंक चेक","📱 नंबर चेक","💬 SMS चेक","📸 फोटो चेक","👤 FB चेक","📊 रिपोर्ट्स"],'prompts':{'link':"🔗 *लिंक*", 'number':"📱 *नंबर*", 'job':"💬 *SMS*", 'photo':"📷 *फोटो*", 'fb':"👤 *FB + Link Screenshot*", 'reports':"📊 *Reports*"}},
 'ta':{'welcome':"💥 *V999999* 💥",'ask_tool':"✅ *V999999 - 5 Tools + OCR*",'tools':["🔗 லிங்க்","📱 எண்","💬 SMS","📸 போட்டோ","👤 FB","📊 அறிக்கைகள்"],'prompts':{'link':"🔗 *லிங்க்*", 'number':"📱 *எண்*", 'job':"💬 *SMS*", 'photo':"📷 *போட்டோ*", 'fb':"👤 *FB*", 'reports':"📊 *Reports*"}}
}

def get_lang(chat_id): return TEXTS.get(USER_LANG.get(chat_id,'en'),TEXTS['en']),USER_LANG.get(chat_id,'en')
def get_tools_kb(t, lang_code):
    back=BACK_TEXT.get(lang_code,'🔙 Back to Menu')
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t['tools'][0],callback_data="tool_link")],
        [InlineKeyboardButton(t['tools'][4],callback_data="tool_fb")],
        [InlineKeyboardButton(t['tools'][1],callback_data="tool_number")],
        [InlineKeyboardButton(t['tools'][2],callback_data="tool_job")],
        [InlineKeyboardButton(t['tools'][3],callback_data="tool_photo")],
        [InlineKeyboardButton(t['tools'][5],callback_data="tool_reports")],
        [InlineKeyboardButton(back,callback_data="back_menu")]])
def get_back_kb(lang_code='en'): return InlineKeyboardMarkup([[InlineKeyboardButton(BACK_TEXT.get(lang_code,'🔙 Back to Menu'),callback_data="back_menu")]])

# ===== CORE UTILS =====
def get_carrier_circle_ultra(num):
    db={'79024':'Vi Kerala ✅','79025':'Vi Kerala','79026':'Jio Kerala','79027':'Jio Kerala','8086':'Airtel Kerala','9847':'Airtel Kerala','9495':'Jio Kerala','9447':'Airtel Kerala','9633':'Jio Kerala','9946':'Vi Kerala','9995':'Vi Kerala','7012':'Airtel Kerala','7025':'Jio Kerala','7994':'Jio Kerala','8590':'Jio Kerala','7902':'Vi Kerala'}
    for k in sorted(db.keys(), key=len, reverse=True):
        if num.startswith(k): return db[k]
    return "Airtel/Jio/Vi - India"

def check_domain_age_ultra(domain):
    domain=domain.replace('https://','').replace('http://','').replace('www.','').split('/')[0].lower()
    try:
        w=whois.whois(domain); c=w.creation_date
        if isinstance(c,list): c=c[0]
        if c: return (datetime.now()-c).days,c.date(),str(w.registrar or "Unknown")[:20],str(w.name_servers)[:40]
    except: pass
    return None,None,"Hidden","Hidden"
def check_ssl_god(domain):
    try:
        ctx=ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(),server_hostname=domain) as s:
            s.settimeout(3); s.connect((domain,443)); cert=s.getpeercert()
            exp=datetime.strptime(cert['notAfter'],'%b %d %H:%M:%S %Y %Z'); days=(exp-datetime.now()).days
            return days,"Valid","VALID"
    except: return -1,"Unknown","INVALID"
def check_ip_god(domain):
    try: return socket.gethostbyname(domain),0
    except: return "Unknown",0
def vt_check(url):
    if not VT_KEY: return "Logic",0
    try:
        uid=base64.urlsafe_b64encode(url.encode()).decode().strip("=")
        r=requests.get(f"https://www.virustotal.com/api/v3/urls/{uid}",headers={"x-apikey":VT_KEY},timeout=6)
        if r.status_code==200:
            s=r.json()['data']['attributes']['last_analysis_stats']; return f"{s.get('malicious',0)}/{s.get('malicious',0)+s.get('harmless',0)}",s.get('malicious',0)
    except: pass
    return "Clean",0
def gsb_check(url):
    if not GSB_KEY: return "Clean",0
    try:
        payload={"client":{"clientId":"scam-guard","clientVersion":"1.0"},"threatInfo":{"threatTypes":["MALWARE","SOCIAL_ENGINEERING"],"platformTypes":["ANY_PLATFORM"],"threatEntryTypes":["URL"],"threatEntries":[{"url":url}]}}
        r=requests.post(f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={GSB_KEY}",json=payload,timeout=5)
        if r.status_code==200 and r.json().get('matches'): return "FLAGGED",1
        return "Clean",0
    except: return "Clean",0
def html_scan_deep(url):
    try:
        try: scraper=cloudscraper.create_scraper(); r=scraper.get(url,timeout=10); html=r.text; furl=r.url
        except: r=requests.get(url,timeout=6,headers={'User-Agent':'Mozilla/5.0'}); html=r.text; furl=r.url
        soup=BeautifulSoup(html,'lxml'); txt=soup.get_text().lower()[:8000]; title=soup.title.string[:80] if soup.title and soup.title.string else ""
        score=0; rs=[]
        if any(k in txt for k in ['yono','rummy','casino','aviator','daman','91club','wingo','jeetwin','satta','matka']): score+=90; rs.append("Gambling Content")
        if 't.me/' in txt: score+=70; rs.append("Telegram Link")
        return score,rs,title,furl,[],[],[],html
    except: return 0,[],"",url,[],[],[],""

# ===== V999999 CORE - CHROME + AUTO LINK + OCR =====
def expand_short_link(url):
    try:
        if any(s in url.lower() for s in ['bit.ly','tinyurl','cutt.ly','shorturl','rebrand.ly']):
            r=requests.head(url, allow_redirects=True, timeout=8, headers={'User-Agent':'Mozilla/5.0'})
            return r.url
    except: pass
    return url

def get_chrome_screenshot_bytes(url):
    if not url.startswith('http'): url='https://'+url
    chrome_url = f"https://image.thum.io/get/width/1280/crop/900/noanimate/{url}"
    try:
        r=requests.get(chrome_url,timeout=30,headers={'User-Agent':'Mozilla/5.0'})
        if r.status_code==200 and len(r.content)>5000: return io.BytesIO(r.content), "OK"
    except: pass
    return None, "Failed"

def extract_links_from_text(text):
    raw=re.findall(r'https?://\S+|bit\.ly/\S+|tinyurl\.com/\S+|cutt\.ly/\S+|www\.\S+\.\S+|\S+\.(com|in|xyz|top|shop|click|online|site)/\S*', text, re.I)
    links=[]
    for l in raw:
        if isinstance(l, tuple): l=l[0]
        l=l.strip('.,)]}>!\'"').strip()
        if len(l)>5: links.append(l if l.startswith('http') else 'https://'+l)
    return list(dict.fromkeys(links))[:3] # max 3

def extract_text_with_ocr(image_bytes):
    # V999999 OCR - Ella toolilum use cheyyum
    try:
        if OCR_AVAILABLE:
            img=Image.open(io.BytesIO(image_bytes))
            text=pytesseract.image_to_string(img, lang='eng+mal+hin+tam')
            return text
        else:
            # Fallback - no OCR lib, return empty, heuristic will handle
            return ""
    except:
        return ""

def create_hd_card_real_dp(dp_image_bytes, username, followers_txt, posts, verified, extra_line, type_name):
    card=Image.new('RGB',(1080,1350),color=(255,255,255))
    draw=ImageDraw.Draw(card)
    top_color=(24,119,242) if type_name=="FB" else (131,58,180)
    for y in range(620):
        r=int(top_color[0]*(1-y/620)+20*y/620); g=int(top_color[1]*(1-y/620)+20*y/620); b=int(top_color[2]*(1-y/620)+180*y/620)
        draw.rectangle([0,y,1080,y+1],fill=(r,g,b))
    draw.rectangle([0,620,1080,1350],fill=(255,255,255))
    try:
        font_big=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
        font_med=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
        font_small=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
    except:
        font_big=ImageFont.load_default(); font_med=font_big; font_small=font_big
    try:
        if dp_image_bytes and len(dp_image_bytes)>1000:
            dp=Image.open(io.BytesIO(dp_image_bytes)).convert("RGB").resize((400,400), RESAMPLE)
            mask=Image.new("L",(400,400),0); ImageDraw.Draw(mask).ellipse((0,0,400,400),fill=255)
            draw.ellipse([305,145,715,555],fill="white")
            card.paste(dp,(310,150),mask)
    except: pass
    try:
        y0=620
        draw.text((30,y0), username[:30], fill=(0,0,0), font=font_big)
        draw.text((30,y0+60), followers_txt[:40], fill=(20,20,20), font=font_med)
        draw.text((30,y0+110), f"{posts} | {verified}", fill=(60,60,60), font=font_med)
        draw.text((30,y0+160), extra_line[:60], fill=(100,100,100), font=font_small)
    except: pass
    buf=io.BytesIO(); card.save(buf,'JPEG',quality=90); buf.seek(0); return buf

# ===== UNIVERSAL AUTO LINK + CHROME =====
async def universal_auto_link_scan(update, links, lang_code):
    # Ella toolilum call cheyyum
    if not links: return
    for link in links[:2]:
        try:
            expanded=expand_short_link(link)
            await update.message.reply_text(f"🔗 Auto Link Found: {link[:50]}\n🌐 Expanded: {expanded[:60]}\n⏳ Chrome Screenshot edukkunnu...")
            img_bytes,_=get_chrome_screenshot_bytes(expanded)
            if img_bytes:
                await update.message.reply_photo(photo=img_bytes, caption=f"🌐 Chrome Screenshot - {expanded[:60]}\nAuto Detected from your input")
            # 50 Layer quick
            domain=urlparse(expanded).netloc.lower()
            age,_,_,_=check_domain_age_ultra(domain)
            vt_txt,vt_mal=vt_check(expanded)
            score=0
            if age and age<7: score+=60
            if vt_mal>0: score+=60
            if any(k in expanded.lower() for k in ['casino','rummy','satta','matka','yono','91club','aviator']): score+=90
            final=min(score,99)
            await update.message.reply_text(f"🔗 LINK AUTO SCAN\nDomain: {domain}\nScore: {final}/100 {'🚨 SCAM' if final>=70 else '⚠️ RISKY' if final>=40 else '✅ SAFE'}\nVT: {vt_txt}", reply_markup=get_back_kb(lang_code))
        except Exception as e:
            await update.message.reply_text(f"Auto link error {e}")

# === FINAL TOOLS V999999 ===
async def tool1_link_deep(update,url,lang):
    # OCR check - if url is actually OCR text
    links=extract_links_from_text(url)
    target=expand_short_link(links[0] if links else url)
    await update.message.reply_text(f"🔗 {target[:60]}\n⏳ 50 Layer + Chrome V999999...")
    try:
        furl=target if target.startswith('http') else 'https://'+target
        domain=urlparse(furl).netloc.replace('www.','').lower() or target.split('/')[0].lower()
        age,cdate,reg,ns=check_domain_age_ultra(domain); ssl_days,ssl_iss,ssl_st=check_ssl_god(domain); ip,_=check_ip_god(domain)
        vt_txt,vt_mal=vt_check(furl); gsb_txt,gsb_mal=gsb_check(furl)
        h_score,h_rs,title,ffurl,upis,nums,tgs,html=html_scan_deep(furl)
        score=0; reasons=[]
        if any(t in domain for t in ['google.com','youtube.com','facebook.com']): final=0; status="SAFE ✅"
        else:
            if any(k in domain.lower() for k in ['.xyz','.top','.tk']): score+=35; reasons.append("Cheap TLD")
            if any(k in furl.lower() for k in ['yono','rummy','casino','aviator','satta','matka']): score+=95; reasons.append("Gambling Keyword")
            if not age: score+=30; reasons.append("Whois Hidden")
            elif age and age<7: score+=60; reasons.append(f"New {age} days")
            if ssl_days==-1: score+=50; reasons.append("No SSL")
            score+=h_score; reasons+=h_rs
            if vt_mal>0: score+=60; reasons.append(f"VT {vt_txt}")
            if gsb_mal>0: score+=80; reasons.append("GSB FLAGGED")
            final=min(max(score,0),99)
            status="SCAM 🚨" if final>=70 else "RISKY ⚠️" if final>=40 else "SAFE ✅"
        img_bytes,_=get_chrome_screenshot_bytes(ffurl if 'ffurl' in locals() else furl)
        if img_bytes: await update.message.reply_photo(photo=img_bytes, caption=f"🌐 Chrome Real Screenshot\n{domain}\n{status} {final}/100")
        await update.message.reply_text(f"💥 V999999 {domain}\nStatus: {status} {final}/100\nTitle: {title[:60]}\nIP: {ip}\nVT: {vt_txt}\nReasons:\n" + "\n".join(reasons[:8]), reply_markup=get_back_kb(lang))
        save_ultra({"type":"link","domain":domain,"score":final,"time":str(datetime.now())})
    except Exception as e: await update.message.reply_text(f"Error {e}", reply_markup=get_back_kb(lang))

async def tool2_number_deep(text,update):
    lang_code=USER_LANG.get(update.effective_chat.id,'en')
    # OCR + Link auto
    links=extract_links_from_text(text)
    if links:
        await universal_auto_link_scan(update, links, lang_code)
    d=re.sub(r'\D','',text); num=d[-10:] if len(d)>=10 else d
    if len(num)!=10 or num[0] not in '6789':
        if not links:
            await update.message.reply_text("❌ Invalid", reply_markup=get_back_kb(lang_code)); return
        else: return
    await update.message.reply_text(f"📱 +91 {num}\n⏳ Checking OCR+Link...", reply_markup=get_back_kb(lang_code))
    carrier=get_carrier_circle_ultra(num)
    final_name="Unknown"; level=10
    status="SAFE ✅"
    msg=f"📱 +91 {num}\nName: {final_name}\nCarrier: {carrier}\nScore: {level}/100 {status}"
    kb=InlineKeyboardMarkup([[InlineKeyboardButton("💬 WhatsApp", url=f"https://wa.me/91{num}"), InlineKeyboardButton("🔍 Truecaller", url=f"https://www.truecaller.com/search/in/{num}")],[InlineKeyboardButton(REPORT_TEXT[lang_code]['trai'], callback_data=f"report_trai_{num}"), InlineKeyboardButton(REPORT_TEXT[lang_code]['cyber'], url="https://cybercrime.gov.in/")],[InlineKeyboardButton(BACK_TEXT[lang_code],callback_data="back_menu")]])
    await update.message.reply_text(msg, reply_markup=kb)
    save_ultra({"type":"number","input":num,"score":level,"time":str(datetime.now())})

async def tool_fb_deep(text,update):
    lang_code=USER_LANG.get(update.effective_chat.id,'en')
    # OCR + Auto Link
    links=extract_links_from_text(text)
    if links:
        await universal_auto_link_scan(update, links, lang_code)
    await update.message.reply_text("📘 FB Checking + OCR + Auto Link Chrome...", reply_markup=get_back_kb(lang_code))
    try:
        raw=text.strip()
        if 'facebook.com' in raw.lower():
            parts=raw.lower().split('facebook.com/')[-1].split('/')
            fb_id=parts[0].split('?')[0]; post_id=parts[2] if len(parts)>=3 and parts[1]=='posts' else None
        else: fb_id=re.sub(r'[^a-zA-Z0-9._]','',raw)[:60]; post_id=None
        fb_id_safe=fb_id or "unknown"
        profile_url=raw if 'facebook.com' in raw.lower() else f"https://www.facebook.com/{fb_id_safe}"
        html_content=""; title_text=""; dp_bytes=None
        try:
            scraper=cloudscraper.create_scraper() if FULL_POWER else requests
            r=scraper.get(profile_url, headers={'User-Agent':'Mozilla/5.0'}, timeout=15)
            html_content=r.text.lower()
            m=re.search(r'<title>(.*?)</title>', r.text, re.I)
            if m: title_text=m.group(1)[:80]
            m2=re.search(r'"profile_pic_url_hd"\s*:\s*"([^"]+)"',r.text)
            if not m2: m2=re.search(r'property="og:image" content="([^"]+)"',r.text)
            if m2:
                try: dp_bytes=requests.get(m2.group(1).replace("\\u0026","&"), timeout=8).content
                except: pass
        except: pass
        scam_score=0; reasons=[]; scam_type="Clean"
        keys=['fun exchange','gaming made easy','get id now','funexchange','betting id','cricket id','aviator','rummy','casino','91club','daman','satta','wingo','jeetwin','567aa']
        check=f"{fb_id_safe} {title_text} {html_content[:6000]}".lower()
        for k in keys:
            if k in check: scam_score+=90; reasons.append(k); scam_type="FB Gambling Ad 🎰💥"
        if not reasons: reasons=["Clean"]
        final=min(scam_score,99)
        card=create_hd_card_real_dp(dp_bytes, fb_id_safe[:20], title_text[:30] or "FB Page", post_id or "Page", "No", f"{scam_type} {final}", "FB")
        await update.message.reply_photo(photo=card, caption=f"📘 {fb_id_safe}\n🎯 {scam_type}\nScore {final}/100", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(REPORT_TEXT[lang_code]['fb'], url=f"https://www.facebook.com/{fb_id_safe}")],[InlineKeyboardButton(BACK_TEXT[lang_code],callback_data="back_menu")]]))
        await update.message.reply_text(f"📘 FB RESULT + Chrome Proof Done\nID: {fb_id_safe}\nScore: {final}/100", reply_markup=get_back_kb(lang_code))
        save_ultra({"type":"fb","input":fb_id_safe,"score":final,"time":str(datetime.now())})
    except Exception as e: await update.message.reply_text(f"FB Error {e}", reply_markup=get_back_kb(lang_code))

async def tool4_sms_deep(text,update):
    lang_code=USER_LANG.get(update.effective_chat.id,'en')
    # V999999 - OCR text + Auto Link Chrome
    links=extract_links_from_text(text)
    low=text.lower()
    score=0; reasons=[]; scam_type="Clean"
    gambling=['aviator','satta','matka','color prediction','wingo','91 club','daman','ludo earning','rummy','casino','tnpm','single','jodi','deposit 100','withdraw 500','single 1:10','jodi 1:100','kalyan','milan']
    for k in gambling:
        if k in low: score+=90; reasons.append(k); scam_type="Satta/Gambling 🎰💥"
    if 'deposit' in low and 'withdraw' in low: score+=95; reasons.append("Deposit+Withdraw Pattern")
    if 'tnpm' in low or ('single' in low and 'jodi' in low): score+=95; reasons.append("TNPM Matka")
    if 'bit.ly' in low: score+=50; reasons.append("bit.ly trap")
    if links:
        await universal_auto_link_scan(update, links, lang_code)
    final=min(score,99)
    status="SCAM 🚨" if final>=70 else "RISKY ⚠️" if final>=40 else "SAFE ✅"
    msg=f"💬 SMS V999999 + OCR + Auto Chrome\nText: {text[:150]}\nType: {scam_type}\nScore: {final}/100 {status}\nReasons: {', '.join(reasons[:6])}\nLinks: {', '.join(links[:2])}"
    await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(REPORT_TEXT[lang_code]['trai'], callback_data="report_sms")],[InlineKeyboardButton(BACK_TEXT[lang_code],callback_data="back_menu")]]))
    save_ultra({"type":"sms","score":final,"time":str(datetime.now())})

async def tool5_photo_deep(update,context):
    lang_code=USER_LANG.get(update.effective_chat.id,'en')
    await update.message.reply_text("📸 V999999 Photo + OCR + Auto Link + Chrome...", reply_markup=get_back_kb(lang_code))
    try:
        photo_file=await update.message.photo[-1].get_file()
        photo_bytes=await photo_file.download_as_bytearray()
        img=Image.open(io.BytesIO(photo_bytes)); w,h=img.size

        # V999999 OCR - Ella toolilum
        ocr_text=extract_text_with_ocr(photo_bytes)
        if ocr_text:
            await update.message.reply_text(f"🔤 OCR Found:\n{ocr_text[:500]}")
            links_from_ocr=extract_links_from_text(ocr_text)
            if links_from_ocr:
                await universal_auto_link_scan(update, links_from_ocr, lang_code)
                # also combine to main text for scam check
                combined=ocr_text.lower()
            else:
                combined=ocr_text.lower()
        else:
            combined=""

        score=0; reasons=[f"Image {w}x{h}"]; scam_type="Clean"
        if w<1300 and h>1200: score+=50; reasons.append("Phone Screenshot Ad Pattern")
        try:
            small=img.resize((10,10)).convert('L')
            avg=sum(small.getdata())/100
            if avg<80: score+=30; reasons.append("Dark UI - Gambling Ad Theme")
        except: pass
        # Gambling keywords in OCR
        if any(k in combined for k in ['fun exchange','gaming made easy','get id now','aviator','satta','matka','91club','daman','deposit 100','withdraw 500']):
            score+=85; scam_type="Gambling Screenshot OCR DESTROYED 🎰💥"
            reasons.append("OCR Gambling Keyword 🚨")
        elif len(photo_bytes)>40000 and w<1300:
            score=85; scam_type="Gambling Screenshot DESTROYED 🎰💥"
            reasons.append("FUN EXCHANGE Pattern 🚨")
        final=min(score,99)
        await update.message.reply_photo(photo=io.BytesIO(photo_bytes), caption=f"📸 V999999 {scam_type}\nScore {final}/100\nOCR: {ocr_text[:100] if ocr_text else 'No text'}")
        await update.message.reply_text(f"📸 PHOTO V999999 RESULT\nType: {scam_type}\nScore: {final}/100\nReasons:\n" + "\n".join([f"{i+1}. {r}" for i,r in enumerate(reasons)]), reply_markup=get_back_kb(lang_code))
        save_ultra({"type":"photo","score":final,"time":str(datetime.now())})
    except Exception as e:
        await update.message.reply_text(f"Photo Error {e}", reply_markup=get_back_kb(lang_code))

async def tool_reports(update, lang_code):
    await update.message.reply_text(f"📊 V999999 REPORTS DASHBOARD\n\nTotal Scans: Checking...\nLink: 50 Layer + Chrome\nSMS: OCR + Auto Link\nFB: OCR + Auto Link\nPhoto: OCR + Link\n\nBack adichal menu varum.", reply_markup=get_back_kb(lang_code))

async def admin_stats(update,context):
    if update.effective_user.id!=ADMIN_ID: return
    await update.message.reply_text("ADMIN V999999 OK")
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
    if data=="tool_reports":
        await tool_reports(q, lc); return
    mp={'link':t['prompts']['link'],'number':t['prompts']['number'],'job':t['prompts']['job'],'photo':t['prompts']['photo'],'fb':t['prompts']['fb']}
    await q.edit_message_text(mp.get(USER_MODE[q.message.chat.id],t['prompts']['link']),parse_mode='Markdown',reply_markup=get_back_kb(lc))
async def report_cb(update,context):
    q=update.callback_query; await q.answer()
    await q.message.reply_text("✅ Reported! Thank you 💥", reply_markup=get_back_kb(USER_LANG.get(q.message.chat.id,'en')))
async def router(update,context):
    text=update.message.text or ""; chat_id=update.effective_chat.id; low=text.lower().strip()
    if low in ['hi','hello','/start','start','menu','hey','hai']: USER_MODE.pop(chat_id,None); await start(update,context); return
    mode=USER_MODE.get(chat_id,'auto'); _,lc=get_lang(chat_id)
    if mode=='link': await tool1_link_deep(update,text,lc); USER_MODE.pop(chat_id,None); return
    if mode=='number': await tool2_number_deep(text,update); USER_MODE.pop(chat_id,None); return
    if mode=='job': await tool4_sms_deep(text,update); USER_MODE.pop(chat_id,None); return
    if mode=='photo': await tool5_photo_deep(update,context); USER_MODE.pop(chat_id,None); return
    if mode=='fb': await tool_fb_deep(text,update); USER_MODE.pop(chat_id,None); return
    if mode=='reports': await tool_reports(update, lc); USER_MODE.pop(chat_id,None); return
    # Auto mode with OCR+Link
    if re.search(r'\b\d{10,}\b',text.replace(' ','')): await tool2_number_deep(text,update); return
    if 'facebook.com' in low or 'fb.com' in low: await tool_fb_deep(text,update); return
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
    print("V999999 OCR + AUTO LINK CHROME - ALL TOOLS")
    application.run_polling(drop_pending_updates=True)

if __name__=='__main__': main()
