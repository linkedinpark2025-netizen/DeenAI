import os, requests, re, streamlit as st, datetime, io
from groq import Groq
from gtts import gTTS 
from streamlit_mic_recorder import mic_recorder
from datetime import datetime
from streamlit_js_eval import streamlit_js_eval

# ==========================================
# 1. INITIALIZATION & SESSION STATE
# ==========================================
if 'messages' not in st.session_state:
st.session_state.messages = []
if 'v_list' not in st.session_state:
st.session_state.v_list = None
if 'user_city' not in st.session_state:
st.session_state.user_city = "London"
if 'trans_lang' not in st.session_state:
st.session_state.trans_lang = "131" 
if 'app_mode' not in st.session_state:
st.session_state.app_mode = "Dashboard"

# Accessing the key via secrets for Cloud or environment for local/replit
G_KEY = st.secrets["GROQ_API_KEY"] if "GROQ_API_KEY" in st.secrets else os.environ.get("GROQ_API_KEY")
client = Groq(api_key=G_KEY)

# ==========================================
# 2. PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(page_title="DeenAI", page_icon="🕌", layout="wide", initial_sidebar_state="collapsed")

# Apply custom CSS for modern UI
st.markdown("""
<style>
/* Base Theme */
:root {
    --primary: #f2ca50;
    --primary-container: #d4af37;
    --surface: #00180d;
    --surface-container-low: #042015;
    --surface-container-high: #142f23;
    --on-surface: #cbead7;
    --on-surface-variant: #d0c5af;
}

/* App Styling */
.stApp {
    background: linear-gradient(135deg, #001a0f 0%, #002b24 100%);
    color: var(--on-surface);
}

/* Hide Streamlit elements */
#MainMenu, header, footer {visibility: hidden;}
.stDeployButton {display:none;}

/* Load Fonts */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600&family=Amiri:wght@400;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

h1, h2, h3 {
    font-family: 'Plus Jakarta Sans', sans-serif;
    color: var(--primary);
}

/* Cards */
.hero-box {
    background: rgba(0,77,64,0.3);
    padding: 25px;
    border-radius: 20px;
    border: 1px solid rgba(212, 175, 55, 0.2);
    text-align: center;
    margin-bottom: 20px;
}

.arabic-txt {
    font-family: 'Amiri', serif;
    font-size: 32px;
    color: #ffffff;
    text-align: center;
    direction: rtl;
    line-height: 1.8;
}

.trans-txt {
    color: #d4af37;
    font-size: 16px;
    margin-top: 10px;
    opacity: 0.9;
    border-top: 1px solid rgba(212,175,55,0.1);
    padding-top: 8px;
}

.verse-card {
    background: rgba(0,0,0,0.3);
    padding: 20px;
    border-radius: 15px;
    margin-bottom: 15px;
    border-left: 4px solid #d4af37;
}

.prayer-time-box {
    text-align:center;
    padding:10px;
    border:1px solid rgba(212,175,55,0.2);
    border-radius:12px;
    background: rgba(0,0,0,0.3);
}

.prayer-time-active {
    background: linear-gradient(135deg, #f2ca50 0%, #d4af37 100%);
    color: #3c2f00;
    box-shadow: 0 0 20px rgba(242, 202, 80, 0.3);
}

/* Bottom Navigation */
.nav-container {
    display: flex;
    justify-content: space-around;
    background: rgba(0, 24, 13, 0.8);
    backdrop-filter: blur(12px);
    padding: 10px;
    border-radius: 20px;
    margin-top: 20px;
    border-top: 1px solid rgba(212, 175, 55, 0.1);
}

.nav-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: rgba(203, 234, 215, 0.5);
    padding: 8px 20px;
    border-radius: 999px;
}

.nav-item.active {
    color: #f2ca50;
    background: #142f23;
    box-shadow: 0 0 15px rgba(242, 202, 80, 0.2);
}

.material-symbols-outlined {
    font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. UTILITIES
# ==========================================
def get_prayer_times(city_name):
try:
    url = f"https://api.aladhan.com/v1/timingsByCity?city={city_name}&country="
    r = requests.get(url, timeout=10).json()
    return r['data']['timings'] if r['code'] == 200 else None
except:
    return None

def speak_gtts(text):
try:
    clean_text = re.sub(r'[*_#]', '', text)
    tts = gTTS(text=clean_text[:1000], lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    return fp.getvalue()
except:
    return None

def get_data(s_id, a_id=None):
try:
    u = f"https://api.quran.com/api/v4/verses/by_key/{s_id}:{a_id}" if a_id else f"https://api.quran.com/api/v4/verses/by_chapter/{s_id}"
    p = {"translations": st.session_state.trans_lang, "fields": "text_uthmani", "per_page": 20}
    r = requests.get(u, params=p).json()
    return [r.get('verse')] if a_id else r.get('verses', [])
except:
    return []

def get_audio_url(verse_key):
try:
    s, ay = verse_key.split(':')
    return f"https://everyayah.com/data/Alafasy_128kbps/{s.zfill(3)}{ay.zfill(3)}.mp3"
except:
    return None

# ==========================================
# 4. HEADER & NAVIGATION
# ==========================================
st.markdown("<h1 style='text-align: center; color: #d4af37;'>DeenAI</h1>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
if col1.button("🏠 Home", use_container_width=True):
st.session_state.app_mode = "Dashboard"
st.rerun()
if col2.button("📖 Quran", use_container_width=True):
st.session_state.app_mode = "Quran Reader"
st.rerun()
if col3.button("📜 Hadith", use_container_width=True):
st.session_state.app_mode = "Hadith Search"
st.rerun()

# ==========================================
# 5. APP MODES
# ==========================================
# --- DASHBOARD / HOME ---
if st.session_state.app_mode == "Dashboard":
# Language Selector
lang_map = {"English": "131", "Urdu": "158", "Bengali": "161", "Indonesian": "33", "Turkish": "77", "Hindi": "122", "Persian": "135"}
col_l1, col_l2 = st.columns([2, 1])
with col_l1:
    st.write("🌍 Translation Language:")
with col_l2:
    current_idx = list(lang_map.values()).index(st.session_state.trans_lang) if st.session_state.trans_lang in lang_map.values() else 0
    sel_lang = st.selectbox("Lang", list(lang_map.keys()), index=current_idx, label_visibility="collapsed")
    st.session_state.trans_lang = lang_map[sel_lang]

# Prayer Times Section
with st.expander("📍 Prayer Times"):
    c1, c2 = st.columns([3, 1])
    with c1:
        city_input = st.text_input("City", st.session_state.user_city, label_visibility="collapsed")
    with c2:
        if st.button("🎯 Auto"):
            loc = streamlit_js_eval(js_expressions="navigator.geolocation.getCurrentPosition((pos) => { return pos.coords.latitude + ',' + pos.coords.longitude; })", want_output=True)
            if loc:
                lat, lon = loc.split(',')
                geo_url = f"https://api.aladhan.com/v1/address?latitude={lat}&longitude={lon}"
                geo_data = requests.get(geo_url).json()
                if geo_data['code'] == 200:
                    st.session_state.user_city = geo_data['data']['city'] or geo_data['data']['region']
                    st.rerun()
    
    if city_input:
        st.session_state.user_city = city_input
        pt = get_prayer_times(city_input)
        if pt:
            cols = st.columns(5)
            prayers = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]
            for i, p in enumerate(prayers):
                cols[i].markdown(f'<div class="prayer-time-box"><small>{p}</small><br><b>{pt[p]}</b></div>', unsafe_allow_html=True)

# Daily verse of the day
day_of_year = datetime.now().timetuple().tm_yday
rotation_keys = ["2:153", "3:139", "94:5", "2:186", "8:30", "29:69", "39:53", "48:4", "55:13", "65:3"]
todays_key = rotation_keys[day_of_year % len(rotation_keys)]
s_id, a_id = todays_key.split(':')

dv_list = get_data(s_id, a_id)
if dv_list and dv_list[0]:
    dv = dv_list[0]
    text_ar = dv.get('text_uthmani', 'Arabic text unavailable')
    trans_text = re.sub('<[^<]+?>', '', dv.get('translations', [{}])[0].get('text', ''))
    
    st.markdown(f"""
    <div class="hero-box">
        <small style="color: #d4af37;">Daily Verse • {datetime.now().strftime('%B %d')}</small>
        <div class="arabic-txt">{text_ar}</div>
        <div class="trans-txt">{trans_text}</div>
        <p style='font-size: 12px; margin-top:5px; opacity:0.6;'>[Surah {todays_key}]</p>
    </div>
    """, unsafe_allow_html=True)

# AI Chat
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

prompt = st.chat_input("Ask DeenAI...")
audio_bytes = mic_recorder(start_prompt="🎤 Speak", stop_prompt="🛑 Stop", key='mic', just_once=True)

if prompt or audio_bytes:
    u_input = prompt
    if audio_bytes:
        with open("temp.wav", "wb") as f:
            f.write(audio_bytes['bytes'])
        with open("temp.wav", "rb") as af:
            u_input = client.audio.transcriptions.create(model="whisper-large-v3", file=af).text
    
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"):
        st.markdown(u_input)

    with st.chat_message("assistant"):
        sys_p = "You are DeenAI, a devout Muslim companion. Answer strictly from Quran and Sahih Hadith. Cite [Surah:Ayah] and Hadith numbers."
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"system","content": sys_p}] + st.session_state.messages).choices[0].message.content
        st.markdown(res)
        audio_out = speak_gtts(res)
        if audio_out:
            st.audio(audio_out, autoplay=True)
        st.session_state.messages.append({"role": "assistant", "content": res})

# --- QURAN READER ---
elif st.session_state.app_mode == "Quran Reader":
st.subheader("📖 Quran Reader")
s_choice = st.number_input("Surah", 1, 114, 1)
v_list = get_data(s_choice)
for v in v_list:
    with st.container():
        st.markdown(f'<div class="verse-card"><div class="arabic-txt">{v.get("text_uthmani", "")}</div>', unsafe_allow_html=True)
        for trans in v.get('translations', []):
            st.markdown(f'<div class="trans-txt">{re.sub("<[^<]+?>", "", trans.get("text", ""))}</div>', unsafe_allow_html=True)
        st.audio(get_audio_url(v.get('verse_key', '')))
        st.markdown('</div>', unsafe_allow_html=True)

# --- HADITH SEARCH ---
elif st.session_state.app_mode == "Hadith Search":
st.subheader("📜 Hadith Library")
topic = st.text_input("Search Hadith by Topic (e.g. Fasting, Parents)")
if topic:
    with st.spinner("Searching Sahihayn..."):
        res = client.chat.completions.create(
            messages=[
                {"role":"system","content":"Answer only using Sahih Bukhari and Sahih Muslim. Provide Hadith numbers."},
                {"role":"user","content":topic}
            ],
            model="llama-3.3-70b-versatile"
        ).choices[0].message.content
        st.info(res)

# ==========================================
# 6. FOOTER NAVIGATION
# ==========================================
st.markdown("""
<div class="nav-container">
<div class="nav-item {}">
    <span class="material-symbols-outlined">home</span>
    <small>Home</small>
</div>
<div class="nav-item {}">
    <span class="material-symbols-outlined">menu_book</span>
    <small>Quran</small>
</div>
<div class="nav-item {}">
    <span class="material-symbols-outlined">auto_stories</span>
    <small>Hadith</small>
</div>
</div>
""".format(
"active" if st.session_state.app_mode == "Dashboard" else "",
"active" if st.session_state.app_mode == "Quran Reader" else "",
"active" if st.session_state.app_mode == "Hadith Search" else ""
), unsafe_allow_html=True)
