import os, requests, re, streamlit as st, datetime, io
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
# Default translation to English (Sahih International)
if 'trans_lang' not in st.session_state: st.session_state.trans_lang = "131"

G_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=G_KEY)

# ==========================================
# 2. MOBILE-FIRST PREMIUM CSS
# ==========================================
st.set_page_config(page_title="DeenAI", layout="wide", page_icon="🕌", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        .stApp { background: linear-gradient(135deg, #001a0f 0%, #002b24 100%); color: #d4af37; }
        [data-testid="stSidebar"] { display: none; }
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
    # API v4 call using the globally selected translation language
    u = f"https://api.quran.com/api/v4/verses/by_key/{s_id}:{a_id}" if a_id else f"https://api.quran.com/api/v4/verses/by_chapter/{s_id}"
    p = {"translations": st.session_state.trans_lang, "fields": "text_uthmani", "per_page": 20}
    try:
        r = requests.get(u, params=p).json()
        return [r.get('verse')] if a_id else r.get('verses', [])
    except: return []

def get_audio_url(verse_key):
    try:
        s, ay = verse_key.split(':')
        # Audio from Mishary Rashid Alafasy
        return f"https://everyayah.com/data/Alafasy_128kbps/{s.zfill(3)}{ay.zfill(3)}.mp3"
    except: return None

# ==========================================
# 4. MAIN APP UI
# ==========================================

st.markdown("<h2 style='text-align: center; color: #d4af37;'>DeenAI</h2>", unsafe_allow_html=True)

# Language Mapping (IDs from Quran.com API)
lang_map = {
    "English": "131",
    "Urdu": "158",
    "Turkish": "77",
    "Sindhi": "836",
    "Russian": "79",
    "Uzbek": "101",
    "French": "31"
}

# --- GLOBAL LANGUAGE SELECTOR ---
with st.container():
    col_l1, col_l2 = st.columns([2, 1])
    with col_l1:
        st.write("🌍 Select Translation Language:")
    with col_l2:
        selected_lang_name = st.selectbox("Lang", list(lang_map.keys()), index=0, label_visibility="collapsed")
        st.session_state.trans_lang = lang_map[selected_lang_name]

# Prayer Times Expansion
with st.expander("📍 Prayer Times"):
    city_input = st.text_input("City", st.session_state.user_city)
    if city_input:
        st.session_state.user_city = city_input
        pt = get_prayer_times(city_input)
        if pt:
            cols = st.columns(5)
            prayers = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]
            for i, p in enumerate(prayers):
                cols[i].markdown(f'<div class="prayer-time-box"><small>{p}</small><br><b>{pt[p]}</b></div>', unsafe_allow_html=True)

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
        with st.container():
            st.markdown(f'<div class="verse-card"><div class="arabic-txt">{v.get("text_uthmani")}</div>', unsafe_allow_html=True)
            for trans in v.get('translations', []):
                clean_t = re.sub('<[^<]+?>', '', trans['text'])
                st.markdown(f'<div class="trans-txt"><b>[{selected_lang_name}]</b>: {clean_t}</div>', unsafe_allow_html=True)
            
            audio_url = get_audio_url(v.get('verse_key'))
            if audio_url: st.audio(audio_url)
            st.markdown('</div>', unsafe_allow_html=True)

# MODE 2: HADITH SEARCH
elif st.session_state.h_text == "init":
    if st.button("← Back to Dashboard"):
        st.session_state.h_text = None
        st.rerun()
    topic = st.text_input("Search Hadith Topic")
    if st.button("Search Sahihayn"):
        with st.spinner("Searching..."):
            res = client.chat.completions.create(
                messages=[{"role":"system","content":"Only use Sahih Bukhari or Muslim."},{"role":"user","content":topic}],
                model="llama-3.3-70b-versatile").choices[0].message.content
            st.info(res)

# MODE 3: DASHBOARD & CHAT
else:
    # Verse of the Day (Dynamically loading based on selected language)
    dv_list = get_data(2, 255) # Ayat al-Kursi as placeholder
    if dv_list:
        dv = dv_list[0]
        st.markdown(f"""
        <div class="hero-box">
            <small style="color: #d4af37;">Ayat al-Kursi</small>
            <div class="arabic-txt">{dv.get('text_uthmani')}</div>
            <div class="trans-txt">{re.sub('<[^<]+?>', '', dv['translations'][0]['text'])}</div>
        </div>
        """, unsafe_allow_html=True)

    nav1, nav2, nav3 = st.columns(3)
    with nav1:
        if st.button("📖 Quran Reader"): st.session_state.v_list = get_data(1); st.rerun()
    with nav2:
        if st.button("📜 Hadith Search"): st.session_state.h_text = "init"; st.rerun()
    with nav3:
        if st.button("⭐ Saved"): st.toast("Coming Soon")

    st.markdown("<br>", unsafe_allow_html=True)

    # Chat Display
    for m in st.session_state.messages:
        with st.chat_message(m["role"]): st.markdown(m["content"])

    # Voice & Text Input
    prompt = st.chat_input("Ask DeenAI...")
    audio_bytes = mic_recorder(start_prompt="🎤 Hold to Speak", stop_prompt="🛑 Stop", key='mic', just_once=True)

    if prompt or audio_bytes:
        u_input = prompt
        if audio_bytes:
            with st.spinner("Processing Voice..."):
                f_name = "temp_audio.wav"
                with open(f_name, "wb") as f: f.write(audio_bytes['bytes'])
                with open(f_name, "rb") as af:
                    transcription = client.audio.transcriptions.create(model="whisper-large-v3", file=af)
                    u_input = transcription.text
        
        st.session_state.messages.append({"role": "user", "content": u_input})
        with st.chat_message("user"): st.markdown(u_input)

        with st.chat_message("assistant"):
            res = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role":"system","content":"Islamic scholar assistant."}] + st.session_state.messages
            ).choices[0].message.content
            st.markdown(res)
            st.session_state.messages.append({"role": "assistant", "content": res})
            audio_data = speak_gtts(res)
            if audio_data: st.audio(audio_data, format="audio/mp3", autoplay=True)
