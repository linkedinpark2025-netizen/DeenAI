import os, requests, re, streamlit as st, datetime, io
from groq import Groq
from gtts import gTTS 
from streamlit_mic_recorder import mic_recorder

# ==========================================
# 1. INITIALIZATION & SESSION STATE
# ==========================================
if 'messages' not in st.session_state: st.session_state.messages = []
if 'page' not in st.session_state: st.session_state.page = "Home"
if 'user_city' not in st.session_state: st.session_state.user_city = "London"
if 'bookmarks' not in st.session_state: st.session_state.bookmarks = []

G_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=G_KEY)

# ==========================================
# 2. DESIGN ENGINE (CSS)
# ==========================================
st.set_page_config(page_title="DEEN AI", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        .stApp { background-color: #F7F7FB; color: #333333; font-family: sans-serif; }
        [data-testid="stHeader"], [data-testid="stSidebar"] { display: none; }
        .block-container { padding-top: 0rem; padding-bottom: 6rem; max-width: 480px; margin: auto; }

        /* Navigation Styling */
        .top-header {
            background-color: #1B3243; padding: 32px 24px 70px 24px;
            border-bottom-left-radius: 28px; border-bottom-right-radius: 28px;
            color: #FFFFFF; position: relative;
        }
        .search-container {
            position: absolute; left: 50%; bottom: -26px; transform: translateX(-50%);
            width: calc(100% - 48px); background: #FFFFFF; padding: 12px 18px;
            border-radius: 22px; box-shadow: 0 6px 16px rgba(0,0,0,0.1);
            display: flex; justify-content: space-between; align-items: center;
        }
        
        /* Cards */
        .cat-card {
            background: #FFFFFF; padding: 22px 10px; border-radius: 20px;
            text-align: center; box-shadow: 0 1px 6px rgba(0,0,0,0.04);
            cursor: pointer;
        }
        .cat-icon { font-size: 26px; color: #1B3243; margin-bottom: 10px; }
        .cat-label { font-size: 13px; color: #3A3D43; font-weight: 500; }

        /* Bottom Nav */
        .bottom-nav {
            position: fixed; bottom: 0; left: 50%; transform: translateX(-50%);
            max-width: 480px; width: 100%; background: #1B3243;
            display: flex; justify-content: space-around; padding: 10px 0;
            border-top-left-radius: 22px; border-top-right-radius: 22px; z-index: 999;
        }
        .nav-btn { background: none; border: none; color: white; opacity: 0.7; font-size: 11px; text-align: center; }
        .nav-btn.active { opacity: 1; font-weight: bold; }

        /* Verse Card */
        .verse-card-main {
            background: #FFFFFF; margin: 0 24px; padding: 20px;
            border-radius: 22px; box-shadow: 0 1px 6px rgba(0,0,0,0.04);
            display: flex; align-items: center; gap: 16px;
        }
        .arabic-badge { background: #F5E1D5; color: #7B4A2A; padding: 15px; border-radius: 50%; font-size: 18px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. UTILITIES & API LOGIC
# ==========================================

def get_prayer_times(city):
    try:
        r = requests.get(f"https://api.aladhan.com/v1/timingsByCity?city={city}&country=").json()
        return r['data']['timings']
    except: return None

def speak(text):
    tts = gTTS(text=text[:500], lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    return fp.getvalue()

def get_quran_verse():
    # Placeholder for Daily Verse (Surah 94:6)
    return {"ar": "فَإِنَّ مَعَ الْعُسْرِ يُسْرًا", "en": "Indeed, with hardship comes ease."}

# ==========================================
# 4. PAGE RENDERING FUNCTIONS
# ==========================================

def change_page(name):
    st.session_state.page = name
    st.rerun()

def render_top_header():
    st.markdown(f"""
    <div class="top-header">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div style="display: flex; align-items: center; gap: 14px;">
                <div style="width:52px; height:52px; background:#0E202C; border-radius:50%; display:flex; align-items:center; justify-content:center; color:#F9C663;">
                    <i class="fa-solid fa-mosque"></i>
                </div>
                <div><b>Welcome</b><br><span style="font-size:14px; opacity:0.9;">to DEEN AI</span></div>
            </div>
        </div>
        <div class="search-container">
            <span style="color:#B0B5C0; font-size:14px;">Ask any question?</span>
            <i class="fa-solid fa-magnifying-glass" style="color:#7E57C2;"></i>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_bottom_nav():
    cols = st.columns(4)
    with cols[0]:
        if st.button("🏠\nHome", key="nav_home"): change_page("Home")
    with cols[1]:
        if st.button("🎤\nAI", key="nav_ai"): change_page("Talk to AI")
    with cols[2]:
        if st.button("🕌\nPray", key="nav_pray"): change_page("Prayer times")
    with cols[3]:
        if st.button("📞\nSupport", key="nav_supp"): change_page("Support")

# ==========================================
# 5. PAGES
# ==========================================

# --- HOME PAGE ---
if st.session_state.page == "Home":
    render_top_header()
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    st.write("### Categories")
    c1, c2, c3 = st.columns(3)
    with c1: 
        if st.button("👥\nTalk to AI"): change_page("Talk to AI")
    with c2: 
        if st.button("⏰\nPrayer Time"): change_page("Prayer times")
    with c3: 
        if st.button("📚\nHadith"): change_page("Hadith Search")
        
    c4, c5, c6 = st.columns(3)
    with c4: 
        if st.button("📖\nQuran"): change_page("Quran Reader")
    with c5: 
        if st.button("⭐\nSaved"): change_page("Saved Knowledge")
    with c6: 
        if st.button("🔗\nVerse"): change_page("Home")

    st.write("### Verse of the day")
    v = get_quran_verse()
    st.markdown(f"""
        <div class="verse-card-main">
            <div class="arabic-badge">﷽</div>
            <div>
                <div style="font-size:18px; font-weight:bold; direction:rtl;">{v['ar']}</div>
                <div style="font-size:14px; color:#555;">{v['en']}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# --- TALK TO AI ---
elif st.session_state.page == "Talk to AI":
    st.button("← Back", on_click=change_page, args=("Home",))
    st.title("🎤 Talk to AI")
    
    audio = mic_recorder(start_prompt="Tap to Record", stop_prompt="Stop", just_once=True, key='recorder')
    
    if audio:
        st.success("Transcribing voice...")
        # (In a full app, you'd send audio to Groq Whisper here)
        # For now, we simulate the text input:
        user_text = "What is the importance of Salah?" 
        st.session_state.messages.append({"role": "user", "content": user_text})
        
        res = client.chat.completions.create(
            messages=[{"role": "system", "content": "Concise Islamic assistant."}] + st.session_state.messages,
            model="llama-3.3-70b-versatile"
        ).choices[0].message.content
        
        st.write(f"**DeenAI:** {res}")
        st.audio(speak(res), format="audio/mp3", autoplay=True)

# --- PRAYER TIMES ---
elif st.session_state.page == "Prayer times":
    st.button("← Back", on_click=change_page, args=("Home",))
    st.title("📍 Prayer Times")
    pt = get_prayer_times(st.session_state.user_city)
    if pt:
        for p, t in pt.items():
            if p in ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]:
                st.write(f"**{p}:** {t}")

# --- HADITH SEARCH ---
elif st.session_state.page == "Hadith Search":
    st.button("← Back", on_click=change_page, args=("Home",))
    st.title("📜 Hadith Search")
    query = st.text_input("Search for a topic (e.g. Patience)")
    if query:
        res = client.chat.completions.create(
            messages=[{"role": "system", "content": "Provide Sahih Bukhari or Muslim only."},{"role":"user","content":query}],
            model="llama-3.3-70b-versatile"
        ).choices[0].message.content
        st.info(res)

# --- QURAN READER ---
elif st.session_state.page == "Quran Reader":
    st.button("← Back", on_click=change_page, args=("Home",))
    st.title("📖 Quran Reader")
    st.write("Surah Al-Fatiha")
    st.audio("https://server8.mp3quran.net/afs/001.mp3")
    st.markdown("<div style='direction:rtl; font-size:24px;'>بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ</div>", unsafe_allow_html=True)

# --- SUPPORT ---
elif st.session_state.page == "Support":
    st.button("← Back", on_click=change_page, args=("Home",))
    st.title("🤝 Support Us")
    st.write("Please share the app with friends and family via this link:")
    st.code("https://deenai.streamlit.app")

# FOOTER NAVIGATION (Always visible)
st.markdown("<br><br><br>", unsafe_allow_html=True)
render_bottom_nav()

