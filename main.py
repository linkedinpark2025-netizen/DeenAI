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

G_KEY = st.secrets["GROQ_API_KEY"]
client = Groq(api_key=G_KEY)

# ==========================================
# 2. THE DESIGN ENGINE (CSS)
# ==========================================
st.set_page_config(page_title="DEEN AI", layout="wide", initial_sidebar_state="collapsed")

# Inject FontAwesome for the specific icons requested
st.markdown("""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        /* Main App Container */
        .stApp { background-color: #F5F5F5; color: #333333; font-family: 'SF Pro', 'Roboto', sans-serif; }
        [data-testid="stHeader"], [data-testid="stSidebar"] { display: none; }
        .block-container { padding-top: 0rem; padding-bottom: 5rem; }

        /* Top Header Panel */
        .top-header {
            background-color: #1A237E; /* Dark Blue */
            padding: 40px 20px 60px 20px;
            border-bottom-left-radius: 30px;
            border-bottom-right-radius: 30px;
            color: white;
            position: relative;
            margin-bottom: 20px;
        }
        .header-content { display: flex; align-items: center; justify-content: space-between; }
        .logo-section { display: flex; align-items: center; gap: 12px; }
        .logo-circle { width: 45px; height: 45px; background: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #1A237E; font-size: 20px; }
        .welcome-text b { font-size: 20px; display: block; }
        .welcome-text span { font-size: 14px; opacity: 0.8; }

        /* Search Bar */
        .search-container {
            position: absolute;
            bottom: -25px;
            left: 50%;
            transform: translateX(-50%);
            width: 85%;
            background: white;
            padding: 12px 20px;
            border-radius: 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .search-placeholder { color: #BDBDBD; font-size: 14px; }
        .search-icon { color: #7E57C2; font-size: 18px; }

        /* Section Titles */
        .section-row { display: flex; justify-content: space-between; padding: 30px 20px 10px 20px; }
        .section-title { color: #424242; font-weight: 600; font-size: 16px; }
        .show-all { color: #757575; font-size: 14px; }

        /* Category Grid */
        .category-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            padding: 0 20px;
        }
        .cat-card {
            background: white;
            padding: 20px 10px;
            border-radius: 20px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            transition: 0.3s;
        }
        .cat-icon { font-size: 24px; color: #1A237E; margin-bottom: 8px; display: block; }
        .cat-label { font-size: 11px; color: #424242; font-weight: 500; }

        /* Verse of the Day Card */
        .verse-card-main {
            background: white;
            margin: 10px 20px;
            padding: 20px;
            border-radius: 20px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .arabic-badge { background: #F3E5F5; color: #1A237E; padding: 10px; border-radius: 12px; font-size: 18px; }
        .star-icon { color: #FFD600; font-size: 14px; }
        .verse-placeholder { color: #757575; font-size: 13px; font-style: italic; }

        /* Bottom Nav Bar */
        .bottom-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            background: #1A237E;
            display: flex;
            justify-content: space-around;
            padding: 12px 0;
            border-top-left-radius: 20px;
            border-top-right-radius: 20px;
            z-index: 999;
        }
        .nav-item { text-align: center; color: white; opacity: 0.7; font-size: 10px; text-decoration: none; }
        .nav-item.active { opacity: 1; font-weight: bold; }
        .nav-item i { font-size: 20px; display: block; margin-bottom: 4px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. COMPONENTS
# ==========================================

def render_header():
    st.markdown(f"""
    <div class="top-header">
        <div class="header-content">
            <div class="logo-section">
                <div class="logo-circle"><i class="fa-solid fa-mosque"></i></div>
                <div class="welcome-text">
                    <span>Welcome</span>
                    <b>to DEEN AI</b>
                </div>
            </div>
            <div class="logo-circle" style="width:35px; height:35px; opacity:0.8;"><i class="fa-solid fa-star-and-crescent"></i></div>
        </div>
        <div class="search-container">
            <span class="search-placeholder">Ask any question?</span>
            <i class="fa-solid fa-magnifying-glass search-icon"></i>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_nav():
    st.markdown("""
    <div class="bottom-nav">
        <div class="nav-item active"><i class="fa-solid fa-house"></i>Home</div>
        <div class="nav-item"><i class="fa-solid fa-stethoscope"></i>Talk to AI</div>
        <div class="nav-item"><i class="fa-solid fa-calendar-days"></i>Prayer times</div>
        <div class="nav-item"><i class="fa-solid fa-circle-user"></i>Support</div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 4. MAIN LAYOUT
# ==========================================

render_header()

# Categories Section
st.markdown("""
    <div class="section-row">
        <span class="section-title">Categories</span>
        <span class="show-all">Show All</span>
    </div>
""", unsafe_allow_html=True)

# 2x3 Grid using standard Streamlit columns but styled via CSS
row1 = st.columns(3)
with row1[0]:
    st.markdown('<div class="cat-card"><i class="fa-solid fa-user-group cat-icon"></i><div class="cat-label">Talk to AI</div></div>', unsafe_allow_html=True)
with row1[1]:
    st.markdown('<div class="cat-card"><i class="fa-solid fa-clock cat-icon"></i><div class="cat-label">Prayer time</div></div>', unsafe_allow_html=True)
with row1[2]:
    st.markdown('<div class="cat-card"><i class="fa-solid fa-file-lines cat-icon"></i><div class="cat-label">Hadith Search</div></div>', unsafe_allow_html=True)

st.markdown('<div style="margin-top:15px;"></div>', unsafe_allow_html=True)

row2 = st.columns(3)
with row2[0]:
    st.markdown('<div class="cat-card"><i class="fa-solid fa-circle-notch cat-icon"></i><div class="cat-label">Quran Reader</div></div>', unsafe_allow_html=True)
with row2[1]:
    st.markdown('<div class="cat-card"><i class="fa-solid fa-bookmark cat-icon"></i><div class="cat-label">Saved Knowlege</div></div>', unsafe_allow_html=True)
with row2[2]:
    st.markdown('<div class="cat-card"><i class="fa-solid fa-circle-nodes cat-icon"></i><div class="cat-label">Verse of the day</div></div>', unsafe_allow_html=True)

# Verse of the day Section
st.markdown('<div class="section-row"><span class="section-title">Verse of the day</span></div>', unsafe_allow_html=True)
st.markdown("""
    <div class="verse-card-main">
        <div class="arabic-badge">﷽</div>
        <i class="fa-solid fa-star star-icon"></i>
        <div class="verse-placeholder">"Indeed, with hardship comes ease." (94:6)</div>
    </div>
""", unsafe_allow_html=True)

# Handle Chat functionality (keeps your AI logic alive)
st.markdown('<div style="padding: 20px;"><hr></div>', unsafe_allow_html=True)
prompt = st.chat_input("Ask any question?")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    res = client.chat.completions.create(
        messages=[{"role":"system","content":"Concise Islamic scholar assistant."}] + st.session_state.messages,
        model="llama-3.3-70b-versatile"
    ).choices[0].message.content
    st.info(res)

render_nav()
