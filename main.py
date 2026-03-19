import os, requests, re, streamlit as st, datetime, io, base64
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

# API key handling
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
# 3. UTILITIES (KEEP YOUR EXISTING CODE)
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
# 4. UI COMPONENTS
# ==========================================
def render_top_app_bar(title="The Digital Maqam"):
"""Render the top app bar with logo and title"""
st.markdown(f"""
<div class="app-header">
    <div style="display: flex; align-items: center; gap: 0.75rem;">
        <div style="width: 2rem; height: 2rem; border-radius: 9999px; background-color: var(--surface-container-high); display: flex; align-items: center; justify-content: center; border: 1px solid rgba(242, 202, 80, 0.2);">
            <span class="material-symbols-outlined" style="color: var(--primary); font-size: 1rem;">spa</span>
        </div>
        <span style="color: var(--primary); font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 700; font-size: 1.25rem; letter-spacing: 0.1em; text-transform: uppercase;">{title}</span>
    </div>
    <div>
        <button style="background: transparent; border: none; color: rgba(203, 234, 215, 0.7); width: 2.5rem; height: 2.5rem; border-radius: 9999px; cursor: pointer; display: flex; align-items: center; justify-content: center;">
            <span class="material-symbols-outlined">settings</span>
        </button>
    </div>
</div>
""", unsafe_allow_html=True)

def render_bottom_nav():
"""Render the bottom navigation bar"""
active = st.session_state.app_mode

home_class = "nav-item active" if active == "Dashboard" else "nav-item" 
quran_class = "nav-item active" if active == "Quran Reader" else "nav-item"
hadith_class = "nav-item active" if active == "Hadith Search" else "nav-item"

st.markdown(f"""
<div class="bottom-nav">
    <a href="#" class="{home_class}" id="nav-home">
        <span class="material-symbols-outlined">{("home") if active != "Dashboard" else "home" + '" style="font-variation-settings: \'FILL\' 1;'}</span>
        <span class="nav-label">Home</span>
    </a>
    <a href="#" class="{quran_class}" id="nav-quran">
        <span class="material-symbols-outlined">{("menu_book") if active != "Quran Reader" else "menu_book" + '" style="font-variation-settings: \'FILL\' 1;'}</span>
        <span class="nav-label">Quran</span>
    </a>
    <a href="#" class="{hadith_class}" id="nav-hadith">
        <span class="material-symbols-outlined">{("auto_stories") if active != "Hadith Search" else "auto_stories" + '" style="font-variation-settings: \'FILL\' 1;'}</span>
        <span class="nav-label">Hadith</span>
    </a>
</div>

<script>
    // Navigation handler
    document.getElementById("nav-home").addEventListener("click", function(e) {
        e.preventDefault();
        window.parent.postMessage({type: "nav_change", value: "Dashboard"}, "*");
    });
    document.getElementById("nav-quran").addEventListener("click", function(e) {
        e.preventDefault();
        window.parent.postMessage({type: "nav_change", value: "Quran Reader"}, "*");
    });
    document.getElementById("nav-hadith").addEventListener("click", function(e) {
        e.preventDefault();
        window.parent.postMessage({type: "nav_change", value: "Hadith Search"}, "*");
    });
</script>
""", unsafe_allow_html=True)

# Handle navigation through JavaScript events
nav_result = streamlit_js_eval(js_expressions=[
    'function listenForNavChange() {',
    '  window.addEventListener("message", function(event) {',
    '    if(event.data.type === "nav_change") return event.data.value;',
    '    return null;',
    '  }, {once: true});',
    '  return null;',
    '}',
    'listenForNavChange();'
], key=f"nav_listener_{datetime.now().timestamp()}", want_output=True)

if nav_result and nav_result in ["Dashboard", "Quran Reader", "Hadith Search"]:
    st.session_state.app_mode = nav_result
    st.rerun()

# ==========================================
# 5. PAGE IMPLEMENTATIONS
# ==========================================
def render_dashboard():
"""Render the home dashboard as in the mockup"""

# Welcome header
st.markdown("""
<div style="margin-bottom: 2.5rem;">
    <p style="color: var(--secondary); font-family: var(--font-label); text-transform: uppercase; letter-spacing: 0.2em; font-size: 0.75rem; margin-bottom: 0.25rem;">Assalamu Alaikum</p>
    <h1 style="font-size: 2.25rem; font-weight: 800; letter-spacing: -0.025em; margin-top: 0;">Digital Sanctuary</h1>
</div>
""", unsafe_allow_html=True)

# Daily verse of the day
day_of_year = datetime.now().timetuple().tm_yday
rotation_keys = ["2:153", "3:139", "94:5", "2:186", "8:30", "29:69", "39:53", "48:4", "55:13", "65:3", "2:255"]
todays_key = rotation_keys[day_of_year % len(rotation_keys)]
s_id, a_id = todays_key.split(':')

dv_list = get_data(s_id, a_id)
if dv_list and dv_list[0]:
    dv = dv_list[0]
    text_ar = dv.get('text_uthmani', 'Arabic text unavailable')
    trans_text = re.sub('<[^<]+?>', '', dv.get('translations', [{}])[0].get('text', ''))
    
    st.markdown(f"""
    <div class="card verse-card">
        <div style="position: absolute; top: 0; right: 0; padding: 1rem; opacity: 0.1;">
            <span class="material-symbols-outlined" style="font-size: 4rem;">auto_stories</span>
        </div>
        
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem;">
            <span style="background: rgba(242, 202, 80, 0.1); color: var(--primary); padding: 0.25rem 0.75rem; border-radius: 9999px; font-size: 0.625rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; border: 1px solid rgba(242, 202, 80, 0.2);">
                Verse of the Day
            </span>
            <span style="color: var(--on-surface-variant); font-size: 0.75rem;">
                Surah {todays_key}
            </span>
        </div>
        
        <p class="arabic-txt">{text_ar}</p>
        
        <p style="color: var(--on-surface-variant); font-style: italic; font-size: 0.875rem; line-height: 1.6; margin-top: 1.5rem;">
            "{trans_text}"
        </p>
        
        <div style="display: flex; gap: 1rem; margin-top: 1.5rem;">
            <button style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.75rem; font-weight: 700; color: var(--primary); background: transparent; border: none; cursor: pointer;">
                <span class="material-symbols-outlined" style="font-size: 1rem;">share</span>
                SHARE
            </button>
            <button style="display: flex; align-items: center; gap: 0.5rem; font-size: 0.75rem; font-weight: 700; color: var(--primary); background: transparent; border: none; cursor: pointer;">
                <span class="material-symbols-outlined" style="font-size: 1rem;">bookmark</span>
                SAVE
            </button>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Prayer Times section
st.markdown("""
<div style="margin-top: 2.5rem; margin-bottom: 1rem;">
    <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 1rem;">
        <h2 style="font-size: 0.875rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; margin: 0;">Prayer Times</h2>
        <span style="font-size: 0.625rem; color: var(--on-surface-variant);">""" + st.session_state.user_city + """ • """ + datetime.now().strftime('%I:%M %p') + """</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Prayer times cards
pt = get_prayer_times(st.session_state.user_city)
if pt:
    col1, col2, col3, col4, col5 = st.columns([1,1,1,1,1])
    
    current_hour = datetime.now().hour
    prayers = [
        {"name": "Fajr", "time": pt["Fajr"], "icon": "light_mode", "col": col1, 
         "active": 4 <= current_hour < 7},
        {"name": "Dhuhr", "time": pt["Dhuhr"], "icon": "wb_sunny", "col": col2, 
         "active": 12 <= current_hour < 15},
        {"name": "Asr", "time": pt["Asr"], "icon": "wb_twilight", "col": col3,
         "active": 15 <= current_hour < 18},
        {"name": "Maghrib", "time": pt["Maghrib"], "icon": "nights_stay", "col": col4,
         "active": 18 <= current_hour < 20},
        {"name": "Isha", "time": pt["Isha"], "icon": "bedtime", "col": col5,
         "active": 20 <= current_hour or current_hour < 4}
    ]
    
    for prayer in prayers:
        with prayer["col"]:
            card_class = "prayer-time-card active" if prayer.get("active") else "prayer-time-card"
            icon_fill = 'font-variation-settings: \'FILL\' 1;' if prayer.get("active") else ''
            text_color = '#3c2f00' if prayer.get("active") else 'var(--on-surface-variant)'
            
            st.markdown(f"""
            <div class="{card_class}">
                <span class="material-symbols-outlined" style="{icon_fill}">{prayer['icon']}</span>
                <div style="font-size: 0.625rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 0.5rem; color: {text_color};">{prayer['name']}</div>
                <div style="font-size: 1.125rem; font-weight: 700; margin-top: 0.25rem; color: {text_color};">{prayer['time']}</div>
            </div>
            """, unsafe_allow_html=True)

# Daily Tasbih card
st.markdown("""
<div style="margin-top: 2.5rem; display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
    <!-- Daily Tasbih card -->
    <div style="background: var(--surface-container-high); padding: 1.5rem; border-radius: 0.75rem; border: 1px solid rgba(77, 70, 53, 0.1); height: 10rem; display: flex; flex-direction: column; justify-content: space-between; transition: all 0.3s ease;">
        <div style="width: 100%; display: flex; justify-content: space-between; align-items: start;">
            <span class="material-symbols-outlined" style="color: var(--primary); font-size: 1.875rem;">history_edu</span>
            <span style="color: var(--primary); font-size: 0.625rem; font-weight: 700;">33%</span>
        </div>
        <div>
            <h3 style="color: var(--on-surface); font-size: 0.875rem; font-weight: 700;">Daily Tasbih</h3>
            <div style="width: 100%; height: 0.25rem; background: var(--surface-container-highest); border-radius: 9999px; margin-top: 0.5rem;">
                <div style="width: 33%; height: 100%; background: var(--primary); border-radius: 9999px; box-shadow: 0 0 8px rgba(242, 202, 80, 0.5);"></div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Chat input (floating)
st.markdown("""
<div class="chat-input">
    <div style="background: rgba(4, 32, 21, 0.8); backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); border: 1px solid rgba(242, 202, 80, 0.2); border-radius: 9999px; padding: 0.5rem; display: flex; align-items: center; box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);">
        <div style="width: 2.5rem; height: 2.5rem; display: flex; align-items: center; justify-content: center; background: rgba(242, 202, 80, 0.1); color: var(--primary); border-radius: 9999px; margin-left: 0.5rem;">
            <span class="material-symbols-outlined">psychology_alt</span>
        </div>
        <input type="text" id="ai-chat-input" placeholder="Ask DeenAI..." style="flex: 1; background: transparent; border: none; color: var(--on-surface); padding: 0.75rem; font-size: 0.875rem; outline: none;" />
        <button id="mic-button" style="width: 3rem; height: 3rem; display: flex; align-items: center; justify-content: center; background: linear-gradient(135deg, #f2ca50 0%, #d4af37 100%); color: var(--on-primary); border-radius: 9999px; border: none; cursor: pointer; margin-right: 0.25rem; transition: transform 0.2s;">
            <span class="material-symbols-outlined" style="font-variation-settings: 'FILL' 1;">mic</span>
        </button>
    </div>
</div>

<script>
    // Submit on Enter key
    document.getElementById('ai-chat-input').addEventListener('keyup', function(event) {
        if (event.key === 'Enter') {
            const value = this.value;
            this.value = '';
            window.parent.postMessage({type: 'chat_input', value: value}, '*');
        }
    });
    
    // Handle mic button click
    document.getElementById('mic-button').addEventListener('click', function() {
        // Activate Streamlit's hidden mic recorder
        document.getElementById('streamlit-mic-button').click();
    });
</script>
""", unsafe_allow_html=True)

# Hidden elements to handle input
with st.container():
    st.markdown('<div id="streamlit-mic-button" style="display: none;">', unsafe_allow_html=True)
    audio_bytes = mic_recorder(start_prompt="", stop_prompt="", key='mic', just_once=True)
    st.markdown('</div>', unsafe_allow_html=True)

# Chat input through Streamlit (hidden)
prompt = st.chat_input("", key="hidden_chat")

# Handle input from JavaScript
js_input = streamlit_js_eval(js_expressions=[
    'function listenForChatInput() {',
    '  window.addEventListener("message", function(event) {',
    '    if(event.data.type === "chat_input") return event.data.value;',
    '    return null;',
    '  }, {once: true});',
    '  return null;',
    '}',
    'listenForChatInput();'
], key=f"chat_input_listener_{datetime.now().timestamp()}", want_output=True)

user_input = prompt or js_input

if audio_bytes:
    with open("temp.wav", "wb") as f: f.write(audio_bytes['bytes'])
    with open("temp.wav", "rb") as af:
        user_input = client.audio.transcriptions.create(model="whisper-large-v3", file=af).text

# Handle and display chat
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Display chat messages
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(f"""
            <div style="display: flex; flex-direction: column; align-items: flex-end; margin-bottom: 1.5rem; max-width: 85%; margin-left: auto;">
                <div class="user-msg">
                    <p style="margin: 0; color: var(--on-surface); font-size: 0.875rem; line-height: 1.6;">
                        {msg["content"]}
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="display: flex; flex-direction: column; align-items: flex-start; margin-bottom: 1.5rem; max-width: 85%;">
                <div style="display: flex; align-items: center; gap: 0.5rem; margin-left: 0.5rem; margin-bottom: 0.25rem;">
                    <span style="width: 0.5rem; height: 0.5rem; background-color: var(--primary); border-radius: 9999px;"></span>
                    <span style="font-size: 0.625rem; font-weight: 700; color: var(--primary); letter-spacing: 0.1em; text-transform: uppercase;">DeenAI</span>
                </div>
                <div class="ai-msg">
                    <p style="margin: 0; color: var(--on-surface); font-size: 0.875rem; line-height: 1.6;">
                        {msg["content"]}
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Generate AI response
    with st.chat_message("assistant"):
        sys_p = "You are DeenAI, a devout Muslim companion. Answer strictly from Quran and Sahih Hadith. Cite [Surah:Ayah] and Hadith numbers."
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"system","content": sys_p}] + st.session_state.messages).choices[0].message.content
        st.markdown(res)
        audio_out = speak_gtts(res)
        if audio_out: st.audio(audio_out, autoplay=True)
        st.session_state.messages.append({"role": "assistant", "content": res})

def render_quran_reader():
"""Render the Quran reader page as in the mockup"""

# Hero section
st.markdown("""
<section style="position: relative; overflow: hidden; border-radius: 0.75rem; padding: 2rem; background: linear-gradient(to bottom right, var(--surface-container-high), var(--surface-container-low)); border-left: 4px solid var(--primary); margin-bottom: 3rem;">
    <div style="position: relative; z-index: 10; display: flex; flex-direction: column; justify-content: space-between; align-items: flex-end; gap: 1.5rem;">
        <div>
            <span style="font-family: 'Inter', sans-serif; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.2em; color: rgba(242, 202, 80, 0.8); display: block; margin-bottom: 0.5rem;">Now Reading</span>
            <h2 style="font-family: 'Plus Jakarta Sans', sans-serif; font-size: 2.25rem; font-weight: 800; color: var(--on-surface); letter-spacing: -0.025em;">Surah Al-Fatihah</h2>
            <p style="font-family: 'Inter', sans-serif; color: var(--on-surface-variant); margin-top: 0.5rem; max-width: 20rem;">
                "The Opening" — Revealed in Makkah, consisting of 7 Ayahs.
            </p>
        </div>
        <div style="text-align: right;">
            <span style="font-family: 'Amiri', serif; font-size: 2.5rem; color: var(--primary); display: block; line-height: 1.5;" dir="rtl">
                سُورَةُ ٱلْفَاتِحَةِ
            </span>
        </div>
    </div>
    <div style="position: absolute; right: -3rem; bottom: -3rem; width: 16rem; height: 16rem; opacity: 0.1; pointer-events: none;">
        <span class="material-symbols-outlined" style="font-size: 16rem; color: var(--primary);">menu_book</span>
    </div>
</section>
""", unsafe_allow_html=True)

# Bismillah
st.markdown("""
<div style="text-align: center; padding: 2rem 0;">
    <p style="font-family: 'Amiri', serif; font-size: 2.25rem; color: var(--on-surface); line-height: 2;" dir="rtl">
        بِسْمِ ٱللَّهِ ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ
    </p>
    <p style="font-family: 'Inter', sans-serif; font-size: 0.875rem; color: var(--on-surface-variant); margin-top: 1rem; font-style: italic; letter-spacing: 0.05em;">
        In the name of Allah, the Entirely Merciful, the Especially Merciful.
    </p>
</div>
""", unsafe_allow_html=True)

# Surah selector (hidden)
s_choice = st.number_input("Surah", 1, 114, 1, label_visibility="collapsed")
v_list = get_data(s_choice)

# Display verses
for i, v in enumerate(v_list):
    verse_key = v.get('verse_key', '')
    text_ar = v.get('text_uthmani', '')
    trans_text = ""
    for trans in v.get('translations', []):
        trans_text += re.sub('<[^<]+?>', '', trans.get('text', ''))
    
    ayah_num = verse_key.split(':')[1]
    
    st.markdown(f"""
    <div class="ayah-card">
        <div style="display: flex; align-items: start; gap: 2rem; margin-bottom: 1.5rem;">
            <div style="display: flex; align-items: center; justify-content: center; width: 2.5rem; height: 2.5rem; border-radius: 9999px; border: 1px solid rgba(242, 202, 80, 0.3); background: var(--surface); color: var(--primary); font-weight: 700; font-size: 0.875rem; flex-shrink: 0; text-align: center; line-height: 2.5rem;">
                {ayah_num}
            </div>
            <p style="font-family: 'Amiri', serif; font-size: 1.875rem; color: var(--on-surface); line-height: 1.8; text-align: right; width: 100%;" dir="rtl">
                {text_ar}
            </p>
        </div>
        <div style="padding-left: 3.5rem;">
            <p style="font-family: 'Inter', sans-serif; color: var(--on-surface); line-height: 1.6;">
                {trans_text}
            </p>
            <div style="display: flex; gap: 1rem; margin-top: 1rem; opacity: 0.6; transition: opacity 0.3s;">
                <button class="ayah-action" style="color: var(--primary); font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; display: flex; align-items: center; gap: 0.5rem; background: transparent; border: none; cursor: pointer;">
                    <span class="material-symbols-outlined" style="font-size: 0.875rem;">play_arrow</span> 
                    Play
                </button>
                <button class="ayah-action" style="color: var(--on-surface-variant); font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; display: flex; align-items: center; gap: 0.5rem; background: transparent; border: none; cursor: pointer;">
                    <span class="material-symbols-outlined" style="font-size: 0.875rem;">bookmark</span> 
                    Save
                </button>
            </div>
        </div>
        <audio controls style="margin-top: 1rem; width: 100%; height: 30px; opacity: 0.7;">
            <source src="{get_audio_url(verse_key)}" type="audio/mp3">
        </audio>
    </div>
    """, unsafe_allow_html=True)

def render_hadith_search():
"""Render the Hadith search page as in the mockup"""

# Header section
st.markdown("""
<header style="margin-bottom: 3rem;">
    <h1 style="font-size: 2.5rem; font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 800; color: var(--primary); margin-bottom: 1rem; letter-spacing: -0.025em;">Hadith Library</h1>
    <p style="color: var(--on-surface-variant); max-width: 36rem; margin-bottom: 2rem; line-height: 1.6;">
        Explore the preserved wisdom of the Prophet Muhammad (PBUH) through the most authentic collections of Hadith.
    </p>
    
    <div style="position: relative; margin-bottom: 2.5rem;">
        <div style="position: absolute; inset-y: 0; left: 1.25rem; display: flex; align-items: center; pointer-events: none;">
            <span class="material-symbols-outlined" style="color: rgba(242, 202, 80, 0.6);">search</span>
        </div>
        <input type="text" id="hadith-search" placeholder="Search Hadith, narrators, or topics..." style="width: 100%; background: var(--surface-container-low); border: none; border-radius: 1rem; padding: 1.25rem 1.5rem 1.25rem 3.5rem; font-size: 1rem; color: var(--on-surface); outline: none; transition: all 0.3s;" />
    </div>
</header>

<div style="display: flex; gap: 0.75rem; overflow-x: auto; margin-bottom: 2.5rem; padding-bottom: 0.5rem;">
    <button style="padding: 0.625rem 1.5rem; border-radius: 9999px; background: linear-gradient(135deg, #f2ca50 0%, #d4af37 100%); color: var(--on-primary); font-weight: 600; font-size: 0.875rem; white-space: nowrap; border: none; cursor: pointer;">
        All Collections
    </button>
    <button style="padding: 0.625rem 1.5rem; border-radius: 9999px; background: var(--surface-container-high); color: var(--on-surface-variant); font-weight: 500; font-size: 0.875rem; white-space: nowrap; border: none; cursor: pointer;">
        Sahih Sittah
    </button>
    <button style="padding: 0.625rem 1.5rem; border-radius: 9999px; background: var(--surface-container-high); color: var(--on-surface-variant); font-weight: 500; font-size: 0.875rem; white-space: nowrap; border: none; cursor: pointer;">
        Arba'in
    </button>
    <button style="padding: 0.625rem 1.5rem; border-radius: 9999px; background: var(--surface-container-high); color: var(--on-surface-variant); font-weight: 500; font-size: 0.875rem; white-space: nowrap; border: none; cursor: pointer;">
        Daily Wisdom
    </button>
</div>

<script>
    // Connect the search input to Streamlit
    document.getElementById('hadith-search').addEventListener('keyup', function(event) {
        if (event.key === 'Enter') {
            window.parent.postMessage({type: 'hadith_search', value: this.value}, '*');
        }
    });
</script>
""", unsafe_allow_html=True)

# Hadith collection grid
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("""
    <div class="hadith-card" style="padding: 2rem; position: relative; overflow: hidden; box-shadow: 0 4px 40px rgba(0, 26, 15, 0.4); margin-bottom: 1.5rem;">
        <div style="position: absolute; top: 0; right: 0; padding: 2rem; opacity: 0.1;">
            <span style="font-family: 'Amiri', serif; font-size: 5rem;">البخاري</span>
        </div>
        <div style="position: relative; z-index: 10;">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 1rem;">
                <span style="padding: 0.25rem 0.75rem; background: rgba(242, 202, 80, 0.1); color: var(--primary); font-size: 0.625rem; text-transform: uppercase; font-weight: 700; letter-spacing: 0.2em; border-radius: 9999px;">
                    Most Authentic
                </span>
                <span style="color: var(--on-surface-variant); font-size: 0.75rem;">
                    7,563 Hadiths
                </span>
            </div>
            <h2 style="font-size: 1.875rem; font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 700; color: var(--on-surface); margin-bottom: 0.5rem;">
                Sahih al-Bukhari
            </h2>
            <p style="color: var(--on-surface-variant); margin-bottom: 2rem; max-width: 30rem; font-size: 0.875rem; line-height: 1.6;">
                Considered the most authentic book after the Holy Quran, compiled by Imam Muhammad al-Bukhari.
            </p>
            <button style="display: flex; align-items: center; gap: 0.5rem; color: var(--primary); font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; font-size: 0.75rem; background: transparent; border: none; cursor: pointer;">
                Open Collection
                <span class="material-symbols-outlined" style="font-size: 1.125rem; transition: transform 0.3s;">arrow_forward</span>
            </button>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="hadith-card" style="padding: 2rem; display: flex; flex-direction: column; justify-content: space-between; height: 100%;">
        <div>
            <div style="width: 3rem; height: 3rem; border-radius: 1rem; background: rgba(242, 202, 80, 0.2); display: flex; align-items: center; justify-content: center; color: var(--primary); margin-bottom: 1.5rem;">
                <span class="material-symbols-outlined">menu_book</span>
            </div>
            <h3 style="font-size: 1.25rem; font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 700; color: var(--on-surface); margin-bottom: 0.5rem;">
                Sahih Muslim
            </h3>
            <p style="color: var(--on-surface-variant); font-size: 0.75rem;">
                The second of the Sahihayn, focusing on legal rulings and ethics.
            </p>
        </div>
        <div style="margin-top: 2rem; display: flex; justify-content: space-between; align-items: center;">
            <span style="font-size: 0.625rem; color: rgba(208, 197, 175, 0.6);">
                3,033 Hadiths
            </span>
            <span class="material-symbols-outlined" style="color: var(--primary);">arrow_forward_ios</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Second row of hadith collections
col3, col4, col5 = st.columns(3)

with col3:
    st.markdown("""
    <div class="hadith-card" style="padding: 1.5rem; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);">
        <h3 style="font-size: 1.125rem; font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 700; color: var(--on-surface); margin-bottom: 0.25rem;">
            Sunan an-Nasa'i
        </h3>
        <p style="color: var(--on-surface-variant); font-size: 0.75rem; margin-bottom: 1rem;">
            Focuses on religious rites and rituals.
        </p>
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <span style="font-size: 0.625rem; color: rgba(242, 202, 80, 0.8); font-weight: 700; text-transform: uppercase; letter-spacing: 0.2em;">
                Al-Mujtaba
            </span>
            <button style="width: 2rem; height: 2rem; border-radius: 9999px; background: var(--surface-container-high); display: flex; align-items: center; justify-content: center; color: var(--primary); border: none; cursor: pointer;">
                <span class="material-symbols-outlined" style="font-size: 0.875rem;">bookmark</span>
            </button>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="hadith-card" style="padding: 1.5rem; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);">
        <h3 style="font-size: 1.125rem; font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 700; color: var(--on-surface); margin-bottom: 0.25rem;">
            Sunan Abu Dawud
        </h3>
        <p style="color: var(--on-surface-variant); font-size: 0.75rem; margin-bottom: 1rem;">
            Essential collection for legal scholarship.
        </p>
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <span style="font-size: 0.625rem; color: rgba(242, 202, 80, 0.8); font-weight: 700; text-transform: uppercase; letter-spacing: 0.2em;">
                Fiqh Focus
            </span>
            <button style="width: 2rem; height: 2rem; border-radius: 9999px; background: var(--surface-container-high); display: flex; align-items: center; justify-content: center; color: var(--primary); border: none; cursor: pointer;">
                <span class="material-symbols-outlined" style="font-size: 0.875rem;">bookmark</span>
            </button>
        </div>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown("""
    <div class="hadith-card" style="padding: 1.5rem; box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);">
        <h3 style="font-size: 1.125rem; font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 700; color: var(--on-surface); margin-bottom: 0.25rem;">
            Jami' at-Tirmidhi
        </h3>
        <p style="color: var(--on-surface-variant); font-size: 0.75rem; margin-bottom: 1rem;">
            Notable for its legal discussion and narrators.
        </p>
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <span style="font-size: 0.625rem; color: rgba(242, 202, 80, 0.8); font-weight: 700; text-transform: uppercase; letter-spacing: 0.2em;">
                The Collector
            </span>
            <button style="width: 2rem; height: 2rem; border-radius: 9999px; background: var(--surface-container-high); display: flex; align-items: center; justify-content: center; color: var(--primary); border: none; cursor: pointer;">
                <span class="material-symbols-outlined" style="font-size: 0.875rem;">bookmark</span>
            </button>
        </div>
    </div>
    """, unsafe_allow_html=True)

# 40 Hadith Nawawi Glass Card
st.markdown("""
<div class="glass-card" style="padding: 2rem; margin-top: 1.5rem; margin-bottom: 3rem; display: flex; flex-direction: column; align-items: center; text-align: center; gap: 2rem;">
    <div style="position: relative; width: 6rem; height: 6rem; border-radius: 9999px; background: rgba(242, 202, 80, 0.2); display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
        <span class="material-symbols-outlined" style="font-size: 2.5rem; color: var(--primary); position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-variation-settings: 'FILL' 1;">star</span>
        <div style="position: absolute; inset: -0.5rem; background: rgba(242, 202, 80, 0.1); filter: blur(1rem); border-radius: 9999px; z-index: -1;"></div>
    </div>
    <div>
        <h3 style="font-size: 1.5rem; font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 700; color: var(--primary); margin-bottom: 0.5rem;">
            40 Hadith Nawawi
        </h3>
        <p style="color: var(--on-surface-variant); line-height: 1.6; font-size: 0.875rem;">
            A concise collection of the most fundamental principles of Islam, perfect for daily meditation and study.
        </p>
    </div>
    <button style="background: linear-gradient(135deg, #f2ca50 0%, #d4af37 100%); color: var(--on-primary); padding: 0.75rem 2rem; border-radius: 9999px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.2em; font-size: 0.75rem; white-space: nowrap; box-shadow: 0 0.5rem 1.5rem rgba(0, 0, 0, 0.2); border: none; cursor: pointer;">
        Start Reading
    </button>
</div>
""", unsafe_allow_html=True)

# Hadith of the Day section
st.markdown("""
<section style="margin-top: 4rem; margin-bottom: 6rem; padding: 2.5rem; background: var(--surface-container-low); border-radius: 0.75rem; border-left: 4px solid var(--primary);">
    <span style="font-size: 0.625rem; font-weight: 700; color: var(--primary); text-transform: uppercase; letter-spacing: 0.2em; margin-bottom: 1.5rem; display: block;">
        Hadith of the Day
    </span>
    <p style="font-family: 'Amiri', serif; text-align: right; font-size: 1.875rem; line-height: 1.8; color: var(--on-surface); margin-bottom: 1.5rem;" dir="rtl">
        "إِنَّمَا الأَعْمَالُ بِالنِّيَّاتِ"
    </p>
    <p style="font-family: 'Inter', sans-serif; font-style: italic; color: var(--on-surface-variant); font-size: 1.125rem; line-height: 1.6; margin-bottom: 1rem;">
        "Actions are but by intentions and every man shall have only that which he intended."
    </p>
    <div style="display: flex; align-items: center; justify-content: space-between; border-top: 1px solid rgba(77, 70, 53, 0.1); padding-top: 1.5rem;">
        <span style="font-size: 0.75rem; color: rgba(242, 202, 80, 0.7);">
            Sahih al-Bukhari 1
        </span>
        <div style="display: flex; gap: 1rem;">
            <button style="color: var(--on-surface-variant); background: transparent; border: none; cursor: pointer;">
                <span class="material-symbols-outlined">share</span>
            </button>
            <button style="color: var(--on-surface-variant); background: transparent; border: none; cursor: pointer;">
                <span class="material-symbols-outlined">content_copy</span>
            </button>
        </div>
    </div>
</section>
""", unsafe_allow_html=True)

# Hidden search functionality
hadith_search_js = streamlit_js_eval(js_expressions=[
    'function listenForHadithSearch() {',
    '  window.addEventListener("message", function(event) {',
    '    if(event.data.type === "hadith_search") return event.data.value;',
    '    return null;',
    '  }, {once: true});',
    '  return null;',
    '}',
    'listenForHadithSearch();'
], key=f"hadith_search_listener_{datetime.now().timestamp()}", want_output=True)

# Regular Streamlit search (hidden)
topic = st.text_input("Search Hadith by Topic", label_visibility="collapsed", key="hadith_search")

search_query = topic or hadith_search_js

if search_query:
    with st.spinner("Searching Sahihayn..."):
        res = client.chat.completions.create(
            messages=[{"role":"system","content":"Answer only using Sahih Bukhari and Sahih Muslim. Provide Hadith numbers."},{"role":"user","content":search_query}],
            model="llama-3.3-70b-versatile").choices[0].message.content
        
        st.markdown(f"""
        <div style="background: var(--surface-container); border: 1px solid rgba(242, 202, 80, 0.1); border-radius: 0.75rem; padding: 1.5rem; margin-top: 1rem; line-height: 1.6; color: var(--on-surface);">
            {res}
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# 6. APP LAYOUT & NAVIGATION
# ==========================================

# Top app bar with title based on current page
if st.session_state.app_mode == "Dashboard":
render_top_app_bar("The Digital Maqam")
elif st.session_state.app_mode == "Quran Reader":
render_top_app_bar("Al-Fatihah")
else:
render_top_app_bar("Hadith Library")

# Wrap content in main container with padding
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# Render the appropriate page based on app mode
if st.session_state.app_mode == "Dashboard":
render_dashboard()
elif st.session_state.app_mode == "Quran Reader":
render_quran_reader()
elif st.session_state.app_mode == "Hadith Search":
render_hadith_search()

st.markdown('</div>', unsafe_allow_html=True)

# Render the bottom navigation bar
render_bottom_nav()

# Add service worker for PWA capability
st.markdown("""
<script>
if ('serviceWorker' in navigator) {
window.addEventListener('load', function() {
    navigator.serviceWorker.register('service-worker.js')
    .then(function(registration) {
        console.log('DeenAI ServiceWorker registration successful');
    })
    .catch(function(err) {
        console.log('DeenAI ServiceWorker registration failed: ', err);
    });
});
}
</script>
""", unsafe_allow_html=True)
