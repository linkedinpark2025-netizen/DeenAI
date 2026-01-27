import os, requests, re, streamlit as st, datetime, io, asyncio
from groq import Groq
from gtts import gTTS 
from streamlit_mic_recorder import mic_recorder
from datetime import datetime

# ==========================================
# 1. INITIALIZATION & SESSION STATE
# ==========================================
if 'messages' not in st.session_state: st.session_state.messages = []
if 'v_list' not in st.session_state: st.session_state.v_list = None
if 'h_text' not in st.session_state: st.session_state.h_text = None
if 'user_city' not in st.session_state: st.session_state.user_city = "London"
if 'trans_lang' not in st.session_state: st.session_state.trans_lang = "158"
if 'app_mode' not in st.session_state: st.session_state.app_mode = "Dashboard"

G_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=G_KEY)

# ==========================================
# 2. MOBILE-FIRST PREMIUM CSS
# ==========================================
st.set_page_config(page_title="DeenAI", layout="wide", page_icon="🕌", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        .stApp { background: linear-gradient(135deg, #001a0f 0%, #002b24 100%); color: #d4af37; }
        [data-testid="stSidebar"] { background-color: #001a0f; }
        .hero-box {
            background: rgba(0,77,64,0.3); padding: 25px; border-radius: 20px;
            border: 1px solid rgba(212, 175, 55, 0.2); text-align: center; margin-bottom: 20px;
        }
        .arabic-txt { font-size: 32px; color: #ffffff; text-align: center; direction: rtl; font-family: 'serif'; line-height: 1.8; }
        .trans-txt { color: #d4af37; font-size: 16px; margin-top: 10px; opacity: 0.9; border-top: 1px solid rgba(212,175,55,0.1); padding-top: 8px; }
        .verse-card { 
            background: rgba(0,0,0,0.3); padding: 20px; border-radius: 15px; 
            margin-bottom: 15px; border-left: 4px solid #d4af37; 
        }
        .prayer-time-box { text-align:center; padding:10px; border:1px solid rgba(212,175,55,0.2); border-radius:12px; background: rgba(0,0,0,0.3); }
        .qibla-circle { 
            border: 4px solid #d4af37; border-radius: 50%; width: 150px; height: 150px; 
            margin: 20px auto; display: flex; align-items: center; justify-content: center; color: white;
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
    u = f"https://api.quran.com/api/v4/verses/by_key/{s_id}:{a_id}" if a_id else f"https://api.quran.com/api/v4/verses/by_chapter/{s_id}"
    p = {"translations": st.session_state.trans_lang, "fields": "text_uthmani", "per_page": 20}
    try:
        r = requests.get(u, params=p).json()
        return [r.get('verse')] if a_id else r.get('verses', [])
    except: return []

def get_audio_url(verse_key):
    try:
        s, ay = verse_key.split(':')
        return f"https://everyayah.com/data/Alafasy_128kbps/{s.zfill(3)}{ay.zfill(3)}.mp3"
    except: return None

# ==========================================
# 4. TOPBAR & NAVIGATION
# ==========================================
st.markdown("<h2 style='text-align: center; color: #d4af37;'>DeenAI</h2>", unsafe_allow_html=True)

nav_col = st.columns(4)
if nav_col[0].button("🏠 Home"): st.session_state.app_mode = "Dashboard"; st.rerun()
if nav_col[1].button("📖 Quran"): st.session_state.app_mode = "Quran Reader"; st.rerun()
if nav_col[2].button("🔍 Topics"): st.session_state.app_mode = "Search Topic"; st.rerun()
if nav_col[3].button("🧭 Qibla"): st.session_state.app_mode = "Qibla Finder"; st.rerun()

# ==========================================
# 5. APP MODES
# ==========================================

# --- QIBLA FINDER (FIXED WITH HEADERS) ---
if st.session_state.app_mode == "Qibla Finder":
    st.subheader("🧭 Qibla Direction")
    q_city = st.text_input("Enter City for Qibla", st.session_state.user_city)
    if q_city:
        # User-Agent header is mandatory for Nominatim
        headers = {'User-Agent': 'DeenAI_App_v1.0'}
        try:
            geo_res = requests.get(f"https://nominatim.openstreetmap.org/search?q={q_city}&format=json", headers=headers, timeout=10)
            if geo_res.status_code == 200:
                geo_data = geo_res.json()
                if geo_data:
                    lat, lon = geo_data[0]['lat'], geo_data[0]['lon']
                    q_res = requests.get(f"https://api.aladhan.com/v1/qibla/{lat}/{lon}").json()
                    deg = q_res['data']['direction']
                    st.markdown(f'<div class="qibla-circle"><h1>{round(deg)}°</h1></div>', unsafe_allow_html=True)
                    st.info(f"Qibla is {round(deg)}° from North in {q_city}.")
                else:
                    st.warning("City not found.")
            else:
                st.error("Service busy. Please try again.")
        except:
            st.error("Error connecting to location services.")

elif st.session_state.app_mode == "Search Topic":
    st.subheader("🔍 Search by Topic")
    topic_query = st.text_input("Enter keyword (e.g. Mercy, Patience)")
    if topic_query:
        search_res = requests.get(f"https://api.quran.com/api/v4/search?q={topic_query}&size=5&language=en").json()
        for res in search_res.get('search', {}).get('results', []):
            v_key = res['verse_key']
            v_data = get_data(v_key.split(':')[0], v_key.split(':')[1])[0]
            st.markdown(f'<div class="verse-card"><div class="arabic-txt">{v_data["text_uthmani"]}</div>', unsafe_allow_html=True)
            st.audio(get_audio_url(v_key))

elif st.session_state.app_mode == "Quran Reader":
    s_choice = st.number_input("Surah Number", 1, 114, 1)
    v_list = get_data(s_choice)
    for v in v_list:
        st.markdown(f'<div class="verse-card"><div class="arabic-txt">{v.get("text_uthmani", "")}</div>', unsafe_allow_html=True)
        st.audio(get_audio_url(v.get('verse_key', '')))

# --- DASHBOARD (HOME) ---
else:
    # --- ROUND ROBIN LOGIC ---
    day_of_year = datetime.now().timetuple().tm_yday
    rotation_keys = ["2:153", "3:139", "94:5", "2:186", "8:30", "29:69", "39:53", "48:4", "55:13", "65:3"]
    todays_key = rotation_keys[day_of_year % len(rotation_keys)]
    s_id, a_id = todays_key.split(':')
    
    dv_list = get_data(s_id, a_id)
    if dv_list and dv_list[0]:
        dv = dv_list[0]
        raw_trans = dv.get('translations', [{}])[0].get('text', 'Translation loading...')
        clean_trans = re.sub('<[^<]+?>', '', raw_trans)
        
        st.markdown(f"""
        <div class="hero-box">
            <small style="color: #d4af37;">Verse of the Day • {datetime.now().strftime('%d %B')}</small>
            <div class="arabic-txt">{dv.get('text_uthmani', '')}</div>
            <div class="trans-txt">{clean_trans}</div>
            <p style='font-size:12px; opacity:0.6; margin-top:5px;'>[Surah {todays_key}]</p>
        </div>
        """, unsafe_allow_html=True)

    # Chat Interface
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    prompt = st.chat_input("Ask DeenAI...")
    audio_bytes = mic_recorder(start_prompt="🎤 Speak to Deen AI", stop_prompt="🛑 Stop", key='mic', just_once=True)

    if prompt or audio_bytes:
        u_input = prompt
        if audio_bytes:
            with open("temp.wav", "wb") as f: f.write(audio_bytes['bytes'])
            with open("temp.wav", "rb") as af:
                u_input = client.audio.transcriptions.create(model="whisper-large-v3", file=af).text
        
        st.session_state.messages.append({"role": "user", "content": u_input})
        with st.chat_message("user"): st.markdown(u_input)

        with st.chat_message("assistant"):
            sys_p = "You are DeenAI, a devout Muslim companion. Guidance strictly from Quran & Sahih Hadith. Cite [Surah:Ayah] and Hadith numbers."
            res = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role":"system","content": sys_p}] + st.session_state.messages
            ).choices[0].message.content
            st.markdown(res)
            audio_out = speak_gtts(res)
            if audio_out: st.audio(audio_out, autoplay=True)
            st.session_state.messages.append({"role": "assistant", "content": res})
