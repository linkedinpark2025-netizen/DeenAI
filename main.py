import os, requests, re, streamlit as st, random, datetime, io
from groq import Groq
from gtts import gTTS 
from streamlit_mic_recorder import mic_recorder

# ==========================================
# 1. INITIALIZATION & SESSION STATE
# ==========================================
if 'messages' not in st.session_state: st.session_state.messages = []
if 'v_list' not in st.session_state: st.session_state.v_list = None
if 'h_text' not in st.session_state: st.session_state.h_text = None
if 'user_city' not in st.session_state: st.session_state.user_city = "London"

# Corrected for Streamlit Cloud Deployment
G_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=G_KEY)

# ==========================================
# 2. MOBILE-FIRST PREMIUM CSS
# ==========================================
st.set_page_config(page_title="DeenAI", layout="wide", page_icon="🕌", initial_sidebar_state="collapsed")

st.markdown("""
    <link rel="manifest" href="manifest.json">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <style>
        /* Force background and hide Streamlit UI elements */
        .stApp { background: linear-gradient(135deg, #001a0f 0%, #002b24 100%); color: #d4af37; }
        [data-testid="stSidebar"] { display: none; }
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Mobile text optimizations */
        @media (max-width: 640px) {
            .arabic-txt { font-size: 26px !important; }
            .hero-box { padding: 15px !important; }
            .stButton > button { height: 55px !important; font-size: 14px !important; }
        }

        .hero-box {
            background: rgba(0,77,64,0.3);
            padding: 25px;
            border-radius: 20px;
            border: 1px solid rgba(212, 175, 55, 0.2);
            margin-bottom: 20px;
            text-align: center;
        }
        .stButton > button {
            background-color: rgba(255, 255, 255, 0.05) !important;
            border: 1px solid rgba(212, 175, 55, 0.3) !important;
            color: #d4af37 !important;
            border-radius: 12px !important;
            height: 60px !important;
            width: 100%;
            font-weight: bold !important;
            transition: 0.3s;
        }
        .stButton > button:hover { border-color: #d4af37 !important; background: rgba(212, 175, 55, 0.1) !important; }
        
        .arabic-txt { font-size: 34px; color: #ffffff; text-align: center; direction: rtl; font-family: 'serif'; line-height: 1.8; }
        .trans-txt { color: #d4af37; font-size: 14px; margin-top: 10px; border-top: 1px solid rgba(212,175,55,0.1); padding-top: 8px; }
        .verse-card { background: rgba(0,0,0,0.2); padding: 20px; border-radius: 15px; margin-bottom: 15px; border-left: 4px solid #d4af37; }
        .prayer-time-box { text-align:center; padding:10px; border:1px solid rgba(212,175,55,0.2); margin-bottom:10px; border-radius:12px; background: rgba(0,0,0,0.3); }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. UTILITIES
# ==========================================
def get_location():
    try:
        res = requests.get("https://ipapi.co/json/", timeout=5).json()
        return res.get("city", "London")
    except: return "London"

def get_prayer_times(city_name):
    try:
        url = f"https://api.aladhan.com/v1/timingsByCity?city={city_name}&country="
        r = requests.get(url, timeout=10).json()
        return r['data']['timings'] if r['code'] == 200 else None
    except: return None

def speak_gtts(text):
    try:
        clean_text = re.sub(r'[*_#]', '', text)
        tts = gTTS(text=clean_text[:1000], lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        return fp.getvalue()
    except: return None

def get_data(s_id, a_id=None):
    target_translations = "131,20" 
    u = f"https://api.quran.com/api/v4/verses/by_key/{s_id}:{a_id}" if a_id else f"https://api.quran.com/api/v4/verses/by_chapter/{s_id}"
    p = {"translations": target_translations, "fields": "text_uthmani", "per_page": 20}
    try:
        r = requests.get(u, params=p).json()
        return [r.get('verse')] if a_id else r.get('verses', [])
    except: return []

def get_daily_verse():
    day_of_year = datetime.datetime.now().timetuple().tm_yday
    keys = ["2:255", "94:5", "2:186", "3:139", "65:3", "55:13"]
    key = keys[day_of_year % len(keys)]
    s_id, v_id = key.split(":")
    data = get_data(s_id, v_id)
    return data[0] if data else None

def get_recitation_url(verse_key):
    try:
        s, ay = verse_key.split(':')
        return f"https://everyayah.com/data/Alafasy_128kbps/{s.zfill(3)}{ay.zfill(3)}.mp3"
    except: return None

# ==========================================
# 4. MAIN APP UI
# ==========================================

# HEADER & PRAYER SECTION
col_logo, col_title = st.columns([1, 4])
with col_title:
    st.markdown("<h2 style='margin:0; color: #d4af37;'>DeenAI</h2>", unsafe_allow_html=True)

with st.expander("📍 Prayer Times & Location"):
    c1, c2 = st.columns([2, 1])
    with c1:
        city_input = st.text_input("Enter City", st.session_state.user_city, label_visibility="collapsed")
    with c2:
        if st.button("🛰️ GPS"):
            st.session_state.user_city = get_location()
            st.rerun()
    
    if city_input:
        st.session_state.user_city = city_input
        pt = get_prayer_times(city_input)
        if pt:
            p_cols = st.columns(3)
            prayers = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha", "Sunrise"]
            for i, p in enumerate(prayers):
                with p_cols[i % 3]:
                    st.markdown(f'<div class="prayer-time-box"><small>{p}</small><br><b>{pt[p]}</b></div>', unsafe_allow_html=True)

# ALWAYS SHOW VERSE OF THE DAY (Unless in Quran/Hadith mode)
if not st.session_state.v_list and not st.session_state.h_text:
    dv = get_daily_verse()
    if dv:
        st.markdown(f"""
        <div class="hero-box">
            <small style="color: #d4af37; text-transform: uppercase; letter-spacing: 2px;">Verse of the Day</small>
            <div class="arabic-txt" style="margin: 15px 0;">{dv.get('text_uthmani', '')}</div>
            <div style="font-weight: bold; font-size: 14px; color: #d4af37;">Surah {dv.get('verse_key', '')}</div>
        </div>
        """, unsafe_allow_html=True)

# MODE 1: QURAN READER
if st.session_state.v_list:
    if st.button("← Back to Dashboard"):
        st.session_state.v_list = None
        st.rerun()
    
    s_choice = st.number_input("Surah Number", 1, 114, 1)
    if st.button("Load Surah"):
        st.session_state.v_list = get_data(s_choice)
        st.rerun()

    for v in st.session_state.v_list:
        st.markdown(f'<div class="verse-card"><div class="arabic-txt">{v.get("text_uthmani")}</div>', unsafe_allow_html=True)
        if 'translations' in v:
            for trans in v['translations']:
                clean_t = re.sub('<[^<]+?>', '', trans['text'])
                st.markdown(f'<div class="trans-txt">{clean_t}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# MODE 2: HADITH SEARCH
elif st.session_state.h_text == "init":
    if st.button("← Back to Dashboard"):
        st.session_state.h_text = None
        st.rerun()
    topic = st.text_input("Search Hadith Topic")
    if st.button("Search Sahihayn"):
        with st.spinner("Consulting Bukhari & Muslim..."):
            res = client.chat.completions.create(
                messages=[{"role":"system","content":"Only provide Sahih Bukhari or Muslim Hadith."},{"role":"user","content":f"Hadith about {topic}"}],
                model="llama-3.3-70b-versatile").choices[0].message.content
            st.info(res)

# MODE 3: DASHBOARD & CHAT
else:
    # Quick Navigation
    nav1, nav2, nav3 = st.columns(3)
    with nav1:
        if st.button("📖 Quran"):
            st.session_state.v_list = get_data(1); st.rerun()
    with nav2:
        if st.button("📜 Hadith"):
            st.session_state.h_text = "init"; st.rerun()
    with nav3:
        if st.button("⭐ Saved"): st.toast("Coming Soon")

    st.markdown("<br>", unsafe_allow_html=True)

    # Chat Display
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    # Voice & Text Input
    prompt = st.chat_input("Ask anything...")
    audio_in = mic_recorder(start_prompt="🎤 Hold to Speak", stop_prompt="⌛ Processing", key='mic', just_once=True)

    if prompt or audio_in:
        u_input = prompt if prompt else "User sent a voice message"
        st.session_state.messages.append({"role": "user", "content": u_input})
        with st.chat_message("user"): st.markdown(u_input)

        with st.chat_message("assistant"):
            hist = [{"role": "system", "content": "You are DeenAI. Strictly use Quran and Sahihayn. Be helpful and concise."}] + st.session_state.messages
            res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=hist).choices[0].message.content
            st.markdown(res)
            st.session_state.messages.append({"role": "assistant", "content": res})
            v_data = speak_gtts(res)
            if v_data: st.audio(v_data, format="audio/mp3", autoplay=True)


