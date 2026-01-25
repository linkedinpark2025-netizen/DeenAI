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

st.markdown("""
    <link rel="stylesheet"
          href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        /* Main App Container */
        .stApp {
            background-color: #F7F7FB;
            color: #333333;
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text",
                         "SF Pro Display", "Roboto", sans-serif;
        }
        [data-testid="stHeader"], [data-testid="stSidebar"] {
            display: none;
        }
        .block-container {
            padding-top: 0rem;
            padding-bottom: 6rem;
            padding-left: 0;
            padding-right: 0;
            max-width: 480px;      /* mimic mobile width */
        }

        /* Top Header Panel */
        .top-header {
            background-color: #1B3243;   /* deep blue/teal like screenshot */
            padding: 32px 24px 70px 24px;
            border-bottom-left-radius: 28px;
            border-bottom-right-radius: 28px;
            color: #FFFFFF;
            position: relative;
        }
        .header-content {
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .logo-section {
            display: flex;
            align-items: center;
            gap: 14px;
        }
        .logo-circle {
            width: 52px;
            height: 52px;
            background: #0E202C;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #F9C663;
            font-size: 20px;
        }
        .welcome-text b {
            font-size: 22px;
            display: block;
            margin-bottom: 2px;
        }
        .welcome-text span {
            font-size: 14px;
            opacity: 0.9;
        }

        /* Search Bar */
        .search-container {
            position: absolute;
            left: 50%;
            bottom: -26px;
            transform: translateX(-50%);
            width: calc(100% - 48px);
            background: #FFFFFF;
            padding: 12px 18px;
            border-radius: 22px;
            box-shadow: 0 6px 16px rgba(0,0,0,0.10);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .search-placeholder {
            color: #B0B5C0;
            font-size: 14px;
        }
        .search-icon {
            color: #7E57C2;
            font-size: 18px;
        }

        /* Section Titles */
        .section-row {
            display: flex;
            justify-content: space-between;
            padding: 40px 24px 12px 24px;
        }
        .section-title {
            color: #2E3135;
            font-weight: 600;
            font-size: 18px;
        }
        .show-all {
            color: #7E828E;
            font-size: 14px;
        }

        /* Category Grid */
        .category-grid-wrapper {
            padding: 0 24px;
        }
        .cat-card {
            background: #FFFFFF;
            padding: 22px 10px 18px 10px;
            border-radius: 20px;
            text-align: center;
            box-shadow: 0 1px 6px rgba(0,0,0,0.04);
        }
        .cat-icon {
            font-size: 26px;
            color: #1B3243;
            margin-bottom: 10px;
            display: block;
        }
        .cat-label {
            font-size: 13px;
            color: #3A3D43;
            font-weight: 500;
        }

        /* Verse Section Title */
        .verse-section-row {
            padding: 26px 24px 12px 24px;
        }

        /* Verse of the Day Card */
        .verse-card-main {
            background: #FFFFFF;
            margin: 0 24px;
            padding: 22px 20px;
            border-radius: 22px;
            box-shadow: 0 1px 6px rgba(0,0,0,0.04);
            display: flex;
            align-items: center;
            gap: 16px;
        }
        .arabic-badge {
            background: #F5E1D5;
            color: #7B4A2A;
            padding: 18px;
            border-radius: 999px;
            font-size: 18px;
            min-width: 64px;
            text-align: center;
        }
        .star-icon {
            color: #FFC107;
            font-size: 20px;
        }
        .verse-text-wrapper {
            flex: 1;
        }
        .verse-line {
            font-size: 20px;
            color: #2E3135;
            line-height: 1.3;
        }

        /* Bottom Nav Bar */
        .bottom-nav {
            position: fixed;
            bottom: 0;
            left: 50%;
            transform: translateX(-50%);
            max-width: 480px;
            width: 100%;
            background: #1B3243;
            display: flex;
            justify-content: space-around;
            padding: 10px 0 12px 0;
            border-top-left-radius: 22px;
            border-top-right-radius: 22px;
            z-index: 999;
        }
        .nav-item {
            text-align: center;
            color: #FFFFFF;
            opacity: 0.7;
            font-size: 11px;
        }
        .nav-item.active {
            opacity: 1;
            font-weight: 600;
        }
        .nav-item i {
            font-size: 22px;
            display: block;
            margin-bottom: 4px;
        }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. COMPONENTS
# ==========================================

def render_header():
    st.markdown("""
    <div class="top-header">
        <div class="header-content">
            <div class="logo-section">
                <div class="logo-circle">
                    <i class="fa-solid fa-mosque"></i>
                </div>
                <div class="welcome-text">
                    <b>Welcome</b>
                    <span>to DEEN AI</span>
                </div>
            </div>
            <div class="logo-circle" style="width:44px; height:44px; background:#0E202C; opacity:0.9;">
                <i class="fa-solid fa-star-and-crescent"></i>
            </div>
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
        <div class="nav-item active">
            <i class="fa-solid fa-house"></i>
            Home
        </div>
        <div class="nav-item">
            <i class="fa-solid fa-stethoscope"></i>
            Talk to AI
        </div>
        <div class="nav-item">
            <i class="fa-solid fa-calendar-days"></i>
            Prayer times
        </div>
        <div class="nav-item">
            <i class="fa-solid fa-circle-user"></i>
            Support
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================
# 4. MAIN LAYOUT
# ==========================================

render_header()

# Categories Section title row
st.markdown("""
    <div class="section-row">
        <span class="section-title">Categories</span>
        <span class="show-all">Show All</span>
    </div>
""", unsafe_allow_html=True)

# Category grid (2 x 3)
st.markdown('<div class="category-grid-wrapper">', unsafe_allow_html=True)
row1 = st.columns(3)
with row1[0]:
    st.markdown(
        '<div class="cat-card">'
        '<i class="fa-solid fa-user-group cat-icon"></i>'
        '<div class="cat-label">Talk to AI</div>'
        '</div>', unsafe_allow_html=True)
with row1[1]:
    st.markdown(
        '<div class="cat-card">'
        '<i class="fa-solid fa-clock cat-icon"></i>'
        '<div class="cat-label">Prayer time</div>'
        '</div>', unsafe_allow_html=True)
with row1[2]:
    st.markdown(
        '<div class="cat-card">'
        '<i class="fa-solid fa-file-lines cat-icon"></i>'
        '<div class="cat-label">Hadith Search</div>'
        '</div>', unsafe_allow_html=True)

st.markdown('<div style="margin-top:14px;"></div>', unsafe_allow_html=True)

row2 = st.columns(3)
with row2[0]:
    st.markdown(
        '<div class="cat-card">'
        '<i class="fa-solid fa-circle-notch cat-icon"></i>'
        '<div class="cat-label">Quran Reader</div>'
        '</div>', unsafe_allow_html=True)
with row2[1]:
    st.markdown(
        '<div class="cat-card">'
        '<i class="fa-solid fa-bookmark cat-icon"></i>'
        '<div class="cat-label">Saved Knowlege</div>'
        '</div>', unsafe_allow_html=True)
with row2[2]:
    st.markdown(
        '<div class="cat-card">'
        '<i class="fa-solid fa-hexagon-nodes-bolt cat-icon"></i>'
        '<div class="cat-label">Verse of the day</div>'
        '</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Verse of the day section
st.markdown(
    '<div class="verse-section-row">'
    '<span class="section-title">Verse of the day</span>'
    '</div>', unsafe_allow_html=True)

# Verse card – no Loren Ipsum text, just placeholders you can fill
st.markdown("""
    <div class="verse-card-main">
        <div class="arabic-badge">﷽</div>
        <i class="fa-solid fa-star star-icon"></i>
        <div class="verse-text-wrapper">
            <div class="verse-line">Verse line one</div>
            <div class="verse-line">Verse line two</div>
            <div class="verse-line">Verse line three</div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Optional: chat functionality section under the card
st.markdown('<div style="padding: 24px 24px 80px 24px;"><hr></div>',
            unsafe_allow_html=True)

prompt = st.chat_input("Ask any question?")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    res = client.chat.completions.create(
        messages=[{"role": "system",
                   "content": "Concise Islamic scholar assistant."}]
                 + st.session_state.messages,
        model="llama-3.3-70b-versatile"
    ).choices[0].message.content
    st.info(res)

render_nav()

