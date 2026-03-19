import os, requests, re, streamlit as st, datetime, io
from groq import Groq
from gtts import gTTS 
from streamlit_mic_recorder import mic_recorder
from datetime import datetime
from streamlit_js_eval import streamlit_js_eval

# ==========================================
# 1. INITIALIZATION & SESSION STATE
# ==========================================
if 'messages' not in st.session_state: st.session_state.messages = []
if 'v_list' not in st.session_state: st.session_state.v_list = None
if 'user_city' not in st.session_state: st.session_state.user_city = "London"
if 'trans_lang' not in st.session_state: st.session_state.trans_lang = "131" 
if 'app_mode' not in st.session_state: st.session_state.app_mode = "Dashboard"

# Accessing the key via secrets for Cloud or environment for local/replit
G_KEY = st.secrets["GROQ_API_KEY"] if "GROQ_API_KEY" in st.secrets else os.environ.get("GROQ_API_KEY")
client = Groq(api_key=G_KEY)

# ==========================================
# 2. PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(page_title="DeenAI", page_icon="🕌", layout="wide", initial_sidebar_state="collapsed")

# Load fonts and material icons
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600&family=Amiri:wght@400;700&display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
""", unsafe_allow_html=True)

# Apply custom CSS to match the mockups
st.markdown("""
<style>
/* Base Styles */
:root {
    --primary: #f2ca50;
    --primary-container: #d4af37;
    --on-primary: #3c2f00;
    --surface: #00180d;
    --surface-container-low: #042015;
    --surface-container: #082419;
    --surface-container-high: #142f23;
    --surface-container-highest: #1f3a2d;
    --on-surface: #cbead7;
    --on-surface-variant: #d0c5af;
}

/* Reset Streamlit */
.stApp {
    background-color: var(--surface) !important;
    color: var(--on-surface);
    font-family: 'Inter', sans-serif;
}

/* Hide Streamlit elements */
#MainMenu, header, footer {visibility: hidden;}
.stDeployButton {display:none;}

/* Typography */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700;
    color: var(--on-surface);
}

/* Material Icons */
.material-symbols-outlined {
    font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}

/* Top App Bar */
.app-header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 4rem;
    background: rgba(0, 24, 13, 0.6);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 1.5rem;
    z-index: 1000;
    box-shadow: 0 4px 30px rgba(0, 26, 15, 0.6);
}

/* Bottom Navigation */
.bottom-nav {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 5rem;
    background: rgba(0, 24, 13, 0.8);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    display: flex;
    justify-content: space-around;
    align-items: center;
    padding: 0 1rem;
    z-index: 1000;
    border-top-left-radius: 2rem;
    border-top-right-radius: 2rem;
    box-shadow: 0 -4px 40px rgba(0, 26, 15, 0.6);
}

.nav-item {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    color: rgba(203, 234, 215, 0.5);
    transition: all 0.3s;
    cursor: pointer;
    padding: 0.5rem;
}

.nav-item:hover {
    color: #dac58d;
}

.nav-item.active {
    color: #f2ca50;
    background: #142f23;
    border-radius: 9999px;
    padding: 0.25rem 1rem;
    box-shadow: 0 0 15px rgba(242, 202, 80, 0.2);
}

.nav-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.625rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 500;
    margin-top: 0.25rem;
}

/* Main Content Padding */
.main-content {
    padding-top: 5rem;
    padding-bottom: 7rem;
    max-width: 48rem;
    margin: 0 auto;
    padding-left: 1.5rem;
    padding-right: 1.5rem;
}

/* Cards */
.card {
    background: var(--surface-container-low);
    border: 1px solid rgba(242, 202, 80, 0.1);
    border-radius: 1rem;
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: all 0.3s ease;
}

.glass-card {
    background: rgba(20, 47, 35, 0.6);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(242, 202, 80, 0.1);
    border-radius: 1rem;
}

/* Gold Gradient */
.gold-gradient {
    background: linear-gradient(135deg, #f2ca50 0%, #d4af37 100%);
}

/* Arabic Text */
.arabic-txt {
    font-family: 'Amiri', serif;
    font-size: 2rem;
    line-height: 1.8;
    text-align: right;
    direction: rtl;
    color: var(--on-surface);
}

/* Chat Input */
.chat-input {
    position: fixed;
    bottom: 6rem;
    left: 1.5rem;
    right: 1.5rem;
    z-index: 900;
}

/* Prayer Times Cards */
.prayer-time-card {
    background: var(--surface-container-high);
    padding: 1rem;
    border-radius: 0.75rem;
    text-align: center;
    border: 1px solid rgba(77, 70, 53, 0.2);
    transition: transform 0.2s;
}

.prayer-time-card.active {
    background: linear-gradient(135deg, #f2ca50 0%, #d4af37 100%);
    color: var(--on-primary);
    box-shadow: 0 0 20px rgba(242, 202, 80, 0.3);
}

.prayer-time-card:hover {
    transform: translateY(-2px);
}

/* Verse Card */
.verse-card {
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(242, 202, 80, 0.2);
}

.verse-card::before {
    content: "";
    position: absolute;
    inset: -0.5rem;
    background: linear-gradient(135deg, #f2ca50 0%, #d4af37 100%);
    opacity: 0.1;
    z-index: -1;
    filter: blur(12px);
    transition: opacity 1s;
}

.verse-card:hover::before {
    opacity: 0.2;
}

/* Hadith Collection Cards */
.hadith-card {
    background: var(--surface-container-low);
    border: 1px solid rgba(77, 70, 53, 0.1);
    border-radius: 0.75rem;
    transition: background-color 0.3s;
}

.hadith-card:hover {
    background: var(--surface-container-high);
}

/* Quran Reader Styles */
.ayah-card {
    padding: 1.5rem;
    border-radius: 0.75rem;
    background: var(--surface-container-low);
    transition: background-color 0.3s;
    margin-bottom: 1.5rem;
}

.ayah-card:hover {
    background: var(--surface-container-high);
}

/* Fix button styling */
.stButton > button {
    background-color: transparent;
    color: var(--on-surface);
    border: 1px solid rgba(242, 202, 80, 0.2);
    border-radius: 9999px;
}

.stButton > button:hover {
    border-color: var(--primary);
    color: var(--primary);
}

/* Input styling */
.stTextInput > div > div > input {
    background-color: var(--surface-container-low);
    border: 1px solid rgba(242, 202, 80, 0.1);
    color: var(--on-surface);
    border-radius: 9999px;
}

/* Chat message styling */
.user-msg {
    background: var(--surface-container-highest);
    border-radius: 1rem 1rem 0 1rem;
    padding: 1rem;
    margin-left: auto;
    max-width: 85%;
}

.ai-msg {
    background: linear-gradient(135deg, #142f23 0%, #082419 100%);
    border: 1px solid rgba(242, 202, 80, 0.15);
    border-radius: 1rem 1rem 1rem 0;
    padding: 1rem;
    max-width: 85%;
    box-shadow: 0 0 20px rgba(242, 202, 80, 0.15);
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
