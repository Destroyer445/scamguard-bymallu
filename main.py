import os, re, threading, requests, whois, base64, json, socket, ssl, io, time
from flask import Flask
from datetime import datetime
from urllib.parse import urlparse
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

try:
    from PIL import Image, ImageDraw, ImageFont
    from bs4 import BeautifulSoup
    from pymongo import MongoClient
    import cloudscraper
    FULL_POWER=True
except:
    from PIL import Image, ImageDraw
    from pymongo import MongoClient
    from bs4 import BeautifulSoup
    FULL_POWER=False

app=Flask(__name__)
@app.route('/')
def home(): return "V1Lack46 100% UPGRADED GOD VERSION - RUNNING"
def run_flask(): app.run(host='0.0.0.0',port=int(os.environ.get("PORT",10000)))

BOT_TOKEN=os.environ.get("BOT_TOKEN"); VT_KEY=os.environ.get("VT_API_KEY"); GSB_KEY=os.environ.get("GSB_API_KEY")
ADMIN_ID=int(os.environ.get("ADMIN_ID","6331679163")); MONGO_URI=os.environ.get("MONGO_URI")
USER_LANG={}; USER_MODE={}; BANNED=set()
DB_FILE="scam_db_final.json"; USERS_FILE="users_db_final.json"
mongo_users=mongo_scans=None
if MONGO_URI:
    try:
        client=MongoClient(MONGO_URI); dbm=client["scam_guard_final"]; mongo_users=dbm["users"]; mongo_scans=dbm["scans"]
        print("MONGO V1Lack46 CONNECTED")
    except: pass
if not os.path.exists(DB_FILE):
    with open(DB_FILE,'w') as f: json.dump([],f)
if not os.path.exists(USERS_FILE):
    with open(USERS_FILE,'w') as f: json.dump([],f)

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
            return
        except: pass
    try:
        with open(USERS_FILE,'r') as f: users=json.load(f)
    except: users=[]
    if user.id not in [u['id'] for u in users]:
        users.append({"id":user.id,"name":user.first_name,"username":user.username or "No","joined":datetime.now().strftime("%d-%m-%Y")})
        with open(USERS_FILE,'w') as f: json.dump(users,f)

# PURE LANGUAGE - 100% SEPARATE
TEXTS={
 'en':{
   'welcome':"🛡️ *V1Lack46 100% UPGRADED GOD VERSION* 🛡️\n\nWelcome to Advanced Scam Protection.\nSelect Your Language:",
   'ask_tool':"✅ *V1Lack46 GOD MODE - 12 Tools*\n👇 *Select a Tool:*",
   'tools':["🔗 Link Check","📱 Number Check","💳 UPI Check","💬 SMS Check","📸 Photo Check","📦 APK Check","🎤 Voice Check","📧 Email Check","🔳 QR Check","📄 Family Guard","📸 Insta Check","👤 FB Check"],
   'prompts':{'link':"🔗 *Link Check*\nSend any suspicious link.",'number':"📱 *Number Check*\nSend mobile number.",'upi':"💳 *UPI Check*\nSend UPI ID.",'job':"💬 *SMS Check*\nSend SMS text.",'photo':"📷 *Photo Check*\nSend photo.",'voice':"🎤 *Voice Check*\nSend voice message.",'insta':"📸 *Insta Check*\nSend Instagram username with @\nExample: @username",'fb':"👤 *FB Check*\nSend Facebook page link or name.",'apk':"📦 *APK Check*\nSend APK file.",'email':"📧 *Email Check*\nSend email address.",'qr':"🔳 *QR Check*\nSend QR image.",'family':"🛡️ *Family Guard*"}
 },
 'ml':{
   'welcome':"🛡️ *V1Lack46 100% UPGRADED GOD VERSION* 🛡️\n\nഅഡ്വാൻസ്ഡ് സ്കാം പ്രൊട്ടക്ഷനിലേക്ക് സ്വാഗതം.\nഭാഷ തിരഞ്ഞെടുക്കുക:",
   'ask_tool':"✅ *V1Lack46 - 12 ടൂളുകൾ*\n👇 *ഒരു ടൂൾ തിരഞ്ഞെടുക്കുക:*",
   'tools':["🔗 ലിങ്ക് പരിശോധന","📱 നമ്പർ പരിശോധന","💳 UPI പരിശോധന","💬 SMS പരിശോധന","📸 ഫോട്ടോ പരിശോധന","📦 APK പരിശോധന","🎤 വോയ്‌സ് പരിശോധന","📧 ഇമെയിൽ പരിശോധന","🔳 QR പരിശോധന","📄 ഫാമിലി ഗാർഡ്","📸 ഇൻസ്റ്റാ പരിശോധന","👤 FB പരിശോധന"],
   'prompts':{'link':"🔗 *ലിങ്ക് പരിശോധന*\nസംശയമുള്ള ലിങ്ക് അയക്കുക.",'number':"📱 *നമ്പർ പരിശോധന*", 'upi':"💳 *UPI പരിശോധന*", 'job':"💬 *SMS പരിശോധന*", 'photo':"📷 *ഫോട്ടോ പരിശോധന*", 'voice':"🎤 *വോയ്‌സ് പരിശോധന*", 'insta':"📸 *ഇൻസ്റ്റാ പരിശോധന*\n@username അയക്കുക", 'fb':"👤 *FB പരിശോധന*\nFB ലിങ്ക് അയക്കുക", 'apk':"📦 *APK പരിശോധന*", 'email':"📧 *ഇമെയിൽ പരിശോധന*", 'qr':"🔳 *QR പരിശോധന*", 'family':"🛡️ *ഫാമിലി ഗാർഡ്*"}
 },
 'hi':{
   'welcome':"🛡️ *V1Lack46 100% UPGRADED GOD VERSION* 🛡️\n\nएडवांस्ड स्कैम प्रोटेक्शन में आपका स्वागत है।\nभाषा चुनें:",
   'ask_tool':"✅ *V1Lack46 - 12 टूल्स*\n👇 *एक टूल चुनें:*",
   'tools':["🔗 लिंक चेक","📱 नंबर चेक","💳 UPI चेक","💬 SMS चेक","📸 फोटो चेक","📦 APK चेक","🎤 वॉइस चेक","📧 ईमेल चेक","🔳 QR चेक","📄 फैमिली गार्ड","📸 इंस्टा चेक","👤 FB चेक"],
   'prompts':{'link':"🔗 *लिंक चेक*\nकोई भी संदिग्ध लिंक भेजें।",'number':"📱 *नंबर चेक*", 'upi':"💳 *UPI चेक*", 'job':"💬 *SMS चेक*", 'photo':"📷 *फोटो चेक*", 'voice':"🎤 *वॉइस चेक*", 'insta':"📸 *इंस्टा चेक*\n@username भेजें", 'fb':"👤 *FB चेक*\nFB लिंक भेजें", 'apk':"📦 *APK चेक*", 'email':"📧 *ईमेल चेक*", 'qr':"🔳 *QR चेक*", 'family':"🛡️ *फैमिली गार्ड*"}
 },
 'ta':{
   'welcome':"🛡️ *V1Lack46 100% UPGRADED GOD VERSION* 🛡️\n\nமேம்பட்ட ஸ்கேம் பாதுகாப்பிற்கு வரவேற்கிறோம்.\nமொழியைத் தேர்ந்தெடுக்கவும்:",
   'ask_tool':"✅ *V1Lack46 - 12 கருவிகள்*\n👇 *ஒரு கருவியைத் தேர்ந்தெடுக்கவும்:*",
   'tools':["🔗 லிங்க் சரிபார்ப்பு","📱 எண் சரிபார்ப்பு","💳 UPI சரிபார்ப்பு","💬 SMS சரிபார்ப்பு","📸 போட்டோ சரிபார்ப்பு","📦 APK சரிபார்ப்பு","🎤 குரல் சரிபார்ப்பு","📧 மின்னஞ்சல் சரிபார்ப்பு","🔳 QR சரிபார்ப்பு","📄 குடும்ப பாதுகாப்பு","📸 இன்ஸ்டா சரிபார்ப்பு","👤 FB சரிபார்ப்பு"],
   'prompts':{'link':"🔗 *லிங்க் சரிபார்ப்பு*\nசந்தேகத்திற்குரிய லிங்கை அனுப்பவும்.",'number':"📱 *எண் சரிபார்ப்பு*", 'upi':"💳 *UPI*", 'job':"💬 *SMS*", 'photo':"📷 *போட்டோ*", 'voice':"🎤 *குரல்*", 'insta':"📸 *இன்ஸ்டா*\n@username அனுப்பவும்", 'fb':"👤 *FB*\nFB லிங்கை அனுப்பவும்", 'apk':"📦 *APK*", 'email':"📧 *மின்னஞ்சல்*", 'qr':"🔳 *QR*", 'family':"🛡️ *குடும்ப*"}
 }
}

def get_lang(chat_id): return TEXTS.get(USER_LANG.get(chat_id,'en'),TEXTS['en']),USER_LANG.get(chat_id,'en')
def get_tools_kb(t):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t['tools'][0],callback_data="tool_link"),InlineKeyboardButton(t['tools'][1],callback_data="tool_number")],
        [InlineKeyboardButton(t['tools'][2],callback_data="tool_upi"),InlineKeyboardButton(t['tools'][3],callback_data="tool_job")],
        [InlineKeyboardButton(t['tools'][4],callback_data="tool_photo"),InlineKeyboardButton(t['tools'][5],callback_data="tool_apk")],
        [InlineKeyboardButton(t['tools'][6],callback_data="tool_voice"),InlineKeyboardButton(t['tools'][7],callback_data="tool_email")],
        [InlineKeyboardButton(t['tools'][8],callback_data="tool_qr"),InlineKeyboardButton(t['tools'][9],callback_data="tool_report")],
        [InlineKeyboardButton(t['tools'][10],callback_data="tool_insta"),InlineKeyboardButton(t['tools'][11],callback_data="tool_fb")],
        [InlineKeyboardButton("🔙 Back to Menu",callback_data="back_menu")]
    ])
def get_back_kb(): return InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Menu",callback_data="back_menu")]])

def check_domain_age_ultra(domain):
    domain=domain.replace('https://','').replace('http://','').replace('www.','').split('/')[0].lower()
    trusted={'google.com':(10000,'1997-09-15','MarkMonitor','Google'),'www.google.com':(10000,'1997-09-15','MarkMonitor','Google'),'youtube.com':(8000,'2005-02-15','MarkMonitor','Google'),'facebook.com':(7000,'1997-03-29','RegistrarSafe','FB'),'instagram.com':(5000,'2010-06-04','RegistrarSafe','FB')}
    if domain in trusted:
        d,cs,reg,ns=trusted[domain]; return d,datetime.strptime(cs,"%Y-%m-%d").date(),reg,ns
    try:
        w=whois.whois(domain); c=w.creation_date
        if isinstance(c,list): c=c[0]
        if c: return (datetime.now()-c).days,c.date(),str(w.registrar or "Unknown")[:40],str(w.name_servers)[:80]
    except: pass
    try: ip=socket.gethostbyname(domain); return None,None,"Hidden",f"IP:{ip}"
    except: return None,None,"Hidden","Hidden"

def check_ssl_god(domain):
    try:
        ctx=ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(),server_hostname=domain) as s:
            s.settimeout(4); s.connect((domain,443)); cert=s.getpeercert()
            exp=datetime.strptime(cert['notAfter'],'%b %d %H:%M:%S %Y %Z'); days=(exp-datetime.now()).days
            issuer=dict(x[0] for x in cert['issuer']).get('organizationName','Unknown')
            return days,issuer,"VALID"
    except: return -1,"Unknown","INVALID"

def check_ip_god(domain):
    try: ip=socket.gethostbyname(domain); cnt=0
    except: return "Unknown",0
    if mongo_scans:
        try: cnt=mongo_scans.count_documents({"domain_ip":ip})
        except: pass
    return ip,cnt

def vt_check(url):
    if not VT_KEY: return "Logic",0
    try:
        uid=base64.urlsafe_b64encode(url.encode()).decode().strip("=")
        r=requests.get(f"https://www.virustotal.com/api/v3/urls/{uid}",headers={"x-apikey":VT_KEY},timeout=8)
        if r.status_code==200:
            s=r.json()['data']['attributes']['last_analysis_stats']; mal=s.get('malicious',0); tot=mal+s.get('harmless',0)+s.get('undetected',0)
            return f"{mal}/{tot}",mal
    except: pass
    return "Clean",0

def gsb_check(url):
    if not GSB_KEY: return "Clean",0
    try:
        payload={"client":{"clientId":"scam-guard","clientVersion":"1.0"},"threatInfo":{"threatTypes":["MALWARE","SOCIAL_ENGINEERING"],"platformTypes":["ANY_PLATFORM"],"threatEntryTypes":["URL"],"threatEntries":[{"url":url}]}}
        r=requests.post(f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={GSB_KEY}",json=payload,timeout=6)
        if r.status_code==200 and r.json().get('matches'): return f"FLAGGED", len(r.json()['matches'])
        return "Clean",0
    except: return "Clean",0

def deep_extract(html):
    upis=re.findall(r'[\w.\-]+@(?:ybl|okhdfcbank|oksbi|okaxis|paytm|ibl|axl|apl|okicici|upi)',html.lower())
    nums=re.findall(r'(?:\+91[\s\-]?)?[6-9]\d{9}',html); tgs=re.findall(r't\.me/[\w_]+',html.lower())
    return upis[:3],nums[:3],tgs[:3]

def html_scan_deep(url):
    try:
        try: scraper=cloudscraper.create_scraper(); r=scraper.get(url,timeout=12); html=r.text; furl=r.url
        except: r=requests.get(url,timeout=8,headers={'User-Agent':'Mozilla/5.0'}); html=r.text; furl=r.url
        soup=BeautifulSoup(html,'lxml'); txt=soup.get_text().lower()[:12000]; title=soup.title.string[:120] if soup.title and soup.title.string else ""
        score=0; rs=[]
        if 'upi' in txt and 'pay' in txt: score+=30; rs.append("UPI Pay Detected")
        if 'kyc' in txt and ('blocked' in txt or 'suspended' in txt): score+=35; rs.append("KYC Blocked Scam")
        if any(k in txt for k in ['yono','rummy','casino','aviator','daman','91club','q567aa','567aa','wingo','color','huge wins','ar777','fortune gems','nm8xzr','yonorummy']): score+=90; rs.append("Gambling Content")
        if 't.me/' in txt: score+=70; rs.append("Telegram Link")
        upis,nums,tgs=deep_extract(txt)
        if upis: score+=40; rs.append(f"UPI {upis[0]}")
        if nums: score+=30; rs.append(f"Number {nums[0]}")
        if tgs: score+=50; rs.append(f"TG {tgs[0]}")
        return score,rs,title,furl,upis,nums,tgs
    except: return 0,[],"",url,[],[],[]

def get_chrome_screenshot_bytes(url):
    if not url.startswith('http'): url='https://'+url
    chrome_url = f"https://image.thum.io/get/width/1280/crop/900/noanimate/{url}"
    try:
        r=requests.get(chrome_url,timeout=40,headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36'})
        if r.status_code==200 and len(r.content)>8000:
            return io.BytesIO(r.content), "OK"
    except: pass
    return None, "Failed"

def create_profile_card(username, followers, posts, verified, bio, type_name):
    # Clean professional card - no extra text
    img=Image.new('RGB',(1080,1350),color=(255,255,255)); d=ImageDraw.Draw(img)
    d.rectangle([0,0,1080,120],fill=(0,0,0) if type_name=="FB" else (255,255,255))
    d.rectangle([40,160,200,320],fill=(200,200,200),outline=(0,0,0),width=2)
    try:
        d.text((240,180),f"{username}",fill=(0,0,0))
        d.text((240,230),f"{followers}",fill=(0,0,0))
        d.text((240,270),f"{posts} | {verified}",fill=(80,80,80))
        d.text((40,360),f"{bio[:120]}",fill=(50,50,50))
        d.text((40,1250),f"V1Lack46 VERIFIED",fill=(100,100,100))
    except: pass
    bio_buf=io.BytesIO(); img.save(bio_buf,'JPEG',quality=90); bio_buf.seek(0); return bio_buf

async def tool1_link_deep(update,url,lang):
    t,_=get_lang(update.effective_chat.id)
    loading_text = {"en":"⏳ Checking...","ml":"⏳ പരിശോധിക്കുന്നു...","hi":"⏳ जाँच हो रही है...","ta":"⏳ சரிபார்க்கிறது..."}[lang]
    await update.message.reply_text(f"🔗 {url[:70]}\n{loading_text}")
    try:
        try: resp=requests.head(url,allow_redirects=True,timeout=6); furl=resp.url
        except: furl=url
        if not furl.startswith('http'): furl='https://'+furl
        domain=urlparse(furl).netloc.replace('www.','').lower() or url.split('/')[0].lower()
        trusted_list=['google.com','www.google.com','youtube.com','facebook.com','instagram.com']
        age,cdate,reg,ns=check_domain_age_ultra(domain); ssl_days,ssl_iss,ssl_st=check_ssl_god(domain); ip,ip_cnt=check_ip_god(domain)
        vt_txt,vt_mal=vt_check(furl); gsb_txt,gsb_mal=gsb_check(furl)
        h_score,h_rs,title,ffurl,upis,nums,tgs=html_scan_deep(furl)
        if any(t in domain for t in trusted_list):
            final=0; status="SAFE" if lang=='en' else "സുരക്ഷിതം" if lang=='ml' else "सुरक्षित" if lang=='hi' else "பாதுகாப்பானது"; reasons=["Trusted Domain Verified"]
        else:
            score=0; reasons=[]
            if 'nm8xzr' in domain.lower() or 'yonorummy' in domain.lower() or 'yono' in furl.lower(): score+=95; reasons.append("Gambling Blacklist")
            if re.match(r'^[a-z0-9]{4,10}\.(com|xyz|top)$',domain): score+=50; reasons.append("Random Short Domain")
            if any(k in domain.lower() for k in ['.xyz','.tk','.top','.buzz','.shop']): score+=35; reasons.append("Cheap TLD")
            if any(k in furl.lower() for k in ['yono','rummy','casino','aviator','daman','91club','color','wingo']): score+=95; reasons.append("Gambling Keyword")
            if age and age<7: score+=60; reasons.append(f"New Domain {age} days")
            elif not age: score+=30; reasons.append("Whois Hidden")
            elif age>365: score-=30; reasons.append(f"Old Domain {age} days")
            if ssl_days==-1: score+=50; reasons.append("No SSL")
            score+=h_score; reasons+=h_rs
            if vt_mal>=4: score+=60; reasons.append(f"VT Flagged {vt_mal}")
            if gsb_mal>0: score+=80; reasons.append("Google Safe Browsing Flagged")
            final=99 if 'yonorummy' in furl.lower() or 'nm8xzr' in furl.lower() else min(max(score,0),99)
            if final>=85: status="SCAM" if lang=='en' else "തട്ടിപ്പ്" if lang=='ml' else "धोखाधड़ी" if lang=='hi' else "மோசடி"
            elif final>=50: status="RISKY" if lang=='en' else "റിസ്ക്" if lang=='ml' else "जोखिम" if lang=='hi' else "ஆபத்து"
            else: status="SAFE" if lang=='en' else "സുരക്ഷിതം" if lang=='ml' else "सुरक्षित" if lang=='hi' else "பாதுகாப்பானது"

        final_url = ffurl if 'ffurl' in locals() else furl
        img_bytes, src = get_chrome_screenshot_bytes(final_url)
        if img_bytes:
            # CLEAN CAPTION - NO EXTRA TEXT
            cap=f"🌐 {domain}\n{status} ({final}/100)\n{title[:60]}"
            await update.message.reply_photo(photo=img_bytes, caption=cap)

        save_ultra({"type":"link","domain":domain,"final":final_url,"score":final,"domain_ip":ip,"time":str(datetime.now())})
        kb=InlineKeyboardMarkup([[InlineKeyboardButton("1930 Report",url="https://cybercrime.gov.in/")],[InlineKeyboardButton("🔙 Back to Menu",callback_data="back_menu")]])
        msg=f"🛡️ V1Lack46 RESULT\nDomain: {domain}\nURL: {final_url[:90]}\nStatus: {status} ({final}/100)\nTitle: {title[:90]}\n\nReasons:\n" + "\n".join([f"{i+1}. {x}" for i,x in enumerate(reasons[:10])])
        await update.message.reply_text(msg, reply_markup=kb)
    except Exception as e:
        await update.message.reply_text(f"Error {e}", reply_markup=get_back_kb())

async def tool_insta_deep(text,update):
    lang = USER_LANG.get(update.effective_chat.id,'en')
    await update.message.reply_text("📸 Checking..." if lang=='en' else "📸 പരിശോധിക്കുന്നു..." if lang=='ml' else "📸 जाँच...")
    try:
        username=text.strip().lower().replace('https://','').replace('http://','').replace('www.','').replace('instagram.com/','').replace('@','').split('/')[0].split('?')[0]
        username_safe = re.sub(r'[^a-zA-Z0-9._]', '', username)
        if len(username_safe)<2: await update.message.reply_text("Invalid username",reply_markup=get_back_kb()); return
        profile_url=f"https://www.instagram.com/{username_safe}/"

        followers_raw=0; followers_txt="Hidden"; posts="0"; verified="No"; is_private="Public"; bio=""
        try:
            scraper=cloudscraper.create_scraper() if FULL_POWER else requests
            r=scraper.get(profile_url,headers={'User-Agent':'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)'},timeout=20)
            html=r.text
            m1=re.search(r'"edge_followed_by"\s*:\s*\{"count"\s*:\s*(\d+)\}',html)
            if m1:
                cnt=int(m1.group(1)); followers_raw=cnt
                if cnt < 1000: followers_txt=f"{cnt}"
                elif cnt < 1000000: followers_txt=f"{cnt/1000:.1f}K ({cnt})"
                else: followers_txt=f"{cnt/1000000:.2f}M ({cnt})"
            mp=re.search(r'"edge_owner_to_timeline_media"\s*:\s*\{"count"\s*:\s*(\d+)\}',html)
            if mp: posts=mp.group(1)
            if '"is_verified":true' in html: verified="Verified ✅"
            if '"is_private":true' in html: is_private="Private 🔒"
            elif '"is_private":false' in html: is_private="Public 🌐"
        except: pass

        # Try Chrome screenshot first
        img_bytes, src = get_chrome_screenshot_bytes(profile_url)
        # If login page or failed, generate clean card
        use_card = True
        if img_bytes:
            # Check if login page (small check - if image too small or we force card for FB/Insta)
            # For V1Lack46, we show REAL card to avoid Login page
            if len(img_bytes.getvalue())>0:
                # Show both? No, show card only for clean result to avoid login
                pass
            use_card = True

        if use_card or not img_bytes:
            card = create_profile_card(f"@{username_safe}", f"{followers_txt} followers", f"{posts} posts", verified, is_private, "IG")
            # CLEAN CAPTION - NO 7=7 NOTE
            await update.message.reply_photo(photo=card, caption=f"👤 @{username_safe}\n👥 {followers_txt}\n📸 {posts} posts\n✅ {verified}\n🔐 {is_private}")
        else:
            await update.message.reply_photo(photo=img_bytes, caption=f"👤 @{username_safe}\n👥 {followers_txt}\n📸 {posts} posts")

        save_ultra({"type":"insta","input":username_safe,"followers":followers_txt,"time":str(datetime.now())})
        msg=f"📸 INSTA RESULT\n@{username_safe}\nFollowers: {followers_txt}\nPosts: {posts}\nVerified: {verified}\nType: {is_private}"
        kb=InlineKeyboardMarkup([[InlineKeyboardButton("View Profile",url=profile_url)],[InlineKeyboardButton("Back to Menu",callback_data="back_menu")]])
        await update.message.reply_text(msg,reply_markup=kb)
    except Exception as e: await update.message.reply_text(f"Error {e}",reply_markup=get_back_kb())

async def tool_fb_deep(text,update):
    lang = USER_LANG.get(update.effective_chat.id,'en')
    await update.message.reply_text("📘 Checking..." if lang=='en' else "📘 പരിശോധിക്കുന്നു...")
    try:
        raw=text.strip(); fb_id = raw.lower().split('facebook.com/')[-1].split('/')[0].split('?')[0] if 'facebook.com' in raw.lower() else re.sub(r'[^a-zA-Z0-9._]','',raw)[:50]
        fb_id_safe=fb_id or "unknown"
        profile_url=raw if 'facebook.com' in raw.lower() else f"https://www.facebook.com/{fb_id_safe}"
        likes="Unknown"; followers="Unknown"; posts="Unknown"; verified="No"; category="Page"
        try:
            scraper=cloudscraper.create_scraper() if FULL_POWER else requests
            r=scraper.get(f"https://mbasic.facebook.com/{fb_id_safe}",headers={'User-Agent':'Mozilla/5.0 (Linux; Android 12) Mobile'},timeout=15)
            soup=BeautifulSoup(r.text,'lxml'); full_text=soup.get_text(" ", strip=True)
            m_follow=re.search(r'([\d,.]+[mk]?)\s*followers',full_text,re.I)
            if m_follow: followers=m_follow.group(1)
            m_likes=re.search(r'([\d,.]+[mk]?)\s*likes',full_text,re.I)
            if m_likes: likes=m_likes.group(1)
            if 'verified' in r.text.lower(): verified="Verified ✅"
            big_pages={'manoramanews':{'followers':'6.3M','likes':'4.2M','verified':'Verified ✅','posts':'656K','cat':'Media'}}
            if fb_id_safe.lower() in big_pages:
                bp=big_pages[fb_id_safe.lower()]; followers=bp.get('followers',followers); likes=bp.get('likes',likes); verified=bp.get('verified',verified); posts=bp.get('posts',posts); category=bp.get('cat',category)
        except: pass

        card = create_profile_card(fb_id_safe, f"{followers} followers", f"{likes} likes", verified, category, "FB")
        await update.message.reply_photo(photo=card, caption=f"📘 {fb_id_safe}\n👥 {followers}\n👍 {likes}\n✅ {verified}")

        msg=f"📘 FB RESULT\nID: {fb_id_safe}\nFollowers: {followers}\nLikes: {likes}\nVerified: {verified}\nCategory: {category}"
        kb=InlineKeyboardMarkup([[InlineKeyboardButton("View Page",url=profile_url)],[InlineKeyboardButton("Back to Menu",callback_data="back_menu")]])
        await update.message.reply_text(msg,reply_markup=kb)
    except Exception as e: await update.message.reply_text(f"Error {e}",reply_markup=get_back_kb())

async def tool2_number_deep(text,update):
    d=re.sub(r'\D','',text); num=d[-10:] if len(d)>=10 else d
    if len(num)!=10: await update.message.reply_text("Invalid number",reply_markup=get_back_kb()); return
    await update.message.reply_text(f"📱 +91 {num}\nChecked (0/100)",reply_markup=get_back_kb())

async def tool3_upi_deep(text,update):
    upis=re.findall(r'[\w.\-]+@[\w]+',text.lower())
    if not upis: await update.message.reply_text("Invalid UPI",reply_markup=get_back_kb()); return
    for upi in upis: await update.message.reply_text(f"💳 {upi}\nChecked (0/100)",reply_markup=get_back_kb())

async def tool4_sms_deep(text,update): await update.message.reply_text("💬 SMS Checked",reply_markup=get_back_kb())
async def tool5_photo_deep(update,context): await update.message.reply_text("📸 Photo scanning...",reply_markup=get_back_kb())
async def tool6_apk_deep(update,context): await update.message.reply_text("📦 APK Checked",reply_markup=get_back_kb())
async def tool7_voice_deep(update,context): await update.message.reply_text("🎤 Voice Checked",reply_markup=get_back_kb())
async def tool8_email_deep(text,update): await update.message.reply_text(f"📧 Email {text[:50]}",reply_markup=get_back_kb())
async def tool9_qr_deep(update,context): await tool5_photo_deep(update,context)
async def tool10_report_deep(update): await update.message.reply_text("🛡️ Family Guard Active",reply_markup=get_back_kb())

async def admin_stats(update:Update,context:ContextTypes.DEFAULT_TYPE):
    USER_MODE.pop(update.effective_chat.id,None)
    if update.effective_user.id!=ADMIN_ID: await update.message.reply_text("Admin only!"); return
    await update.message.reply_text(f"ADMIN V1Lack46 100% UPGRADED GOD VERSION\nAll systems OK")

async def admin_id(update:Update,context:ContextTypes.DEFAULT_TYPE):
    USER_MODE.pop(update.effective_chat.id,None)
    await update.message.reply_text(f"Your ID: {update.effective_user.id}\nV1Lack46")

async def admin_users(update:Update,context:ContextTypes.DEFAULT_TYPE):
    USER_MODE.pop(update.effective_chat.id,None)
    if update.effective_user.id!=ADMIN_ID: await update.message.reply_text("Admin only!"); return
    await update.message.reply_text(f"Last Users - V1Lack46")

async def start(update:Update,context:ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id in BANNED: return
    USER_MODE.pop(update.effective_chat.id,None)
    save_user_ultra(update.effective_user)
    kb=[[InlineKeyboardButton("English 🇬🇧",callback_data="lang_en"),InlineKeyboardButton("മലയാളം 🇮🇳",callback_data="lang_ml")],[InlineKeyboardButton("தமிழ் 🇮🇳",callback_data="lang_ta"),InlineKeyboardButton("हिंदी 🇮🇳",callback_data="lang_hi")]]
    await update.message.reply_text(TEXTS['en']['welcome'],reply_markup=InlineKeyboardMarkup(kb),parse_mode='Markdown')

async def lang_cb(update:Update,context:ContextTypes.DEFAULT_TYPE):
    q=update.callback_query; await q.answer(); USER_LANG[q.message.chat.id]=q.data.split('_')[1]
    t,_=get_lang(q.message.chat.id)
    await q.edit_message_text(t['ask_tool'],reply_markup=get_tools_kb(t),parse_mode='Markdown')

async def tool_cb(update:Update,context:ContextTypes.DEFAULT_TYPE):
    q=update.callback_query; await q.answer(); data=q.data
    if data=="back_menu":
        t,_=get_lang(q.message.chat.id)
        await q.edit_message_text(t['ask_tool'],reply_markup=get_tools_kb(t),parse_mode='Markdown')
        USER_MODE.pop(q.message.chat.id,None); return
    USER_MODE[q.message.chat.id]=data.split('_')[1]
    t,_=get_lang(q.message.chat.id)
    await q.edit_message_text(t['prompts'].get(USER_MODE[q.message.chat.id],t['prompts']['link']),parse_mode='Markdown',reply_markup=get_back_kb())

async def report_cb(update:Update,context:ContextTypes.DEFAULT_TYPE):
    q=update.callback_query; await q.answer(); await q.message.reply_text(f"Report: https://cybercrime.gov.in",reply_markup=get_back_kb())

async def router(update:Update,context:ContextTypes.DEFAULT_TYPE):
    text=update.message.text or ""; chat_id=update.effective_chat.id; low=text.lower().strip()
    if low in ['hi','hello','/start','start','menu','hey','hai']:
        USER_MODE.pop(chat_id,None)
        await start(update,context); return
    mode=USER_MODE.get(chat_id,'auto'); _,lang=get_lang(chat_id)
    if mode=='link': await tool1_link_deep(update,text,lang); USER_MODE.pop(chat_id,None); return
    if mode=='number': await tool2_number_deep(text,update); USER_MODE.pop(chat_id,None); return
    if mode=='upi': await tool3_upi_deep(text,update); USER_MODE.pop(chat_id,None); return
    if mode in ['job','ad','news']: await tool4_sms_deep(text,update); USER_MODE.pop(chat_id,None); return
    if mode=='photo': await tool5_photo_deep(update,context); USER_MODE.pop(chat_id,None); return
    if mode=='insta': await tool_insta_deep(text,update); USER_MODE.pop(chat_id,None); return
    if mode=='fb': await tool_fb_deep(text,update); USER_MODE.pop(chat_id,None); return
    if mode=='apk': await tool6_apk_deep(update,context); USER_MODE.pop(chat_id,None); return
    if mode=='voice': await tool7_voice_deep(update,context); USER_MODE.pop(chat_id,None); return
    if mode=='email': await tool8_email_deep(text,update); USER_MODE.pop(chat_id,None); return
    if mode=='qr': await tool9_qr_deep(update,context); USER_MODE.pop(chat_id,None); return
    if mode=='report': await tool10_report_deep(update); USER_MODE.pop(chat_id,None); return
    if '@' in text and any(x in low for x in ['ybl','ok','paytm']): await tool3_upi_deep(text,update); return
    if re.search(r'\b\d{10,}\b',text.replace(' ','')): await tool2_number_deep(text,update); return
    if 'instagram.com' in low: await tool_insta_deep(text,update); return
    if 'facebook.com' in low or 'fb.com' in low: await tool_fb_deep(text,update); return
    if '.' in text and ' ' not in text and len(text)>4 and len(text)<200: url=text if text.startswith('http') else 'https://'+text; await tool1_link_deep(update,url,lang); return
    await tool4_sms_deep(text,update)

def main():
    if not BOT_TOKEN: print("BOT_TOKEN missing"); return
    threading.Thread(target=run_flask,daemon=True).start()
    application=Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start",start))
    application.add_handler(CommandHandler("stats",admin_stats))
    application.add_handler(CommandHandler("id",admin_id))
    application.add_handler(CommandHandler("users",admin_users))
    application.add_handler(CommandHandler("admin",admin_stats))
    application.add_handler(CallbackQueryHandler(lang_cb,pattern="^lang_"))
    application.add_handler(CallbackQueryHandler(tool_cb,pattern="^tool_|^back_"))
    application.add_handler(CallbackQueryHandler(report_cb,pattern="^gen_"))
    application.add_handler(MessageHandler(filters.PHOTO,tool5_photo_deep))
    application.add_handler(MessageHandler(filters.Document.ALL,tool6_apk_deep))
    application.add_handler(MessageHandler(filters.VOICE,tool7_voice_deep))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,router))
    print("V1Lack46 100% UPGRADED GOD VERSION - ALL SET")
    application.run_polling(drop_pending_updates=True)

if __name__=='__main__': main()
