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

# API key handling
G_KEY = st.secrets["GROQ_API_KEY"] if "GROQ_API_KEY" in st.secrets else os.environ.get("GROQ_API_KEY")
client = Groq(api_key=G_KEY)

# ==========================================
# 2. PAGE CONFIGURATION & CSS
# ==========================================
st.set_page_config(page_title="DeenAI", page_icon="🕌", layout="centered", initial_sidebar_state="collapsed")

# Main CSS for styling
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Inter:wght@400;500;600&family=Amiri:wght@400;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

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

body {
    font-family: 'Inter', sans-serif;
    background-color: var(--surface);
    color: var(--on-surface);
}

/* Hide Streamlit elements */
#MainMenu, header, footer {visibility: hidden;}
.stDeployButton {display:none;}

.stApp {
    background: linear-gradient(135deg, #001a0f 0%, #002b24 100%); 
}

/* App Header */
.app-header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    height: 4rem;
    background-color: rgba(0, 24, 13, 0.8);
    backdrop-filter: blur(12px);
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0 1.5rem;
    z-index: 1000;
}

/* Bottom Navigation */
.bottom-nav {
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    height: 5rem;
    background-color: rgba(0, 24, 13, 0.8);
    backdrop-filter: blur(12px);
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
    text-decoration: none;
    padding: 0.5rem;
    cursor: pointer;
}

.nav-item.active {
    color: #f2ca50;
    background-color: #142f23;
    border-radius: 9999px;
    padding: 0.25rem 1rem;
    box-shadow: 0 0 15px rgba(242, 202, 80, 0.2);
}

.nav-label {
    font-family: 'Inter', sans-serif;
    font-size: 0.625rem;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-top: 0.25rem;
}

/* Content area */
.main-content {
    padding-top: 5rem;
    padding-bottom: 7rem;
    max-width: 48rem;
    margin: 0 auto;
}

/* Cards */
.card {
    background-color: rgba(0,77,64,0.3);
    padding: 1.5rem; 
    border-radius: 1rem;
    border: 1px solid rgba(212, 175, 55, 0.2);
    margin-bottom: 1.5rem;
}

/* Arabic text */
.arabic-txt {
    font-family: 'Amiri', serif;
    font-size: 2rem;
    line-height: 1.8;
    text-align: right;
    direction: rtl;
}

/* Material icons */
.material-symbols-outlined {
    font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 24;
}

/* Prayer time cards */
.prayer-time-box {
    text-align: center;
    padding: 1rem;
    border: 1px solid rgba(212, 175, 55, 0.2);
    border-radius: 0.75rem;
    background-color: rgba(0, 0, 0, 0.3);
    margin-bottom: 0.5rem;
}

.active-prayer {
    background: linear-gradient(135deg, #f2ca50 0%, #d4af37 100%);
    color: #3c2f00;
}

/* Verse cards */
.verse-card {
    background-color: rgba(0, 0, 0, 0.3);
    padding: 1.5rem;
    border-radius: 1rem;
    margin-bottom: 1rem;
    border-left: 4px solid #d4af37;
}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. UTILITY FUNCTIONS
# ==========================================
def get_prayer_times(city_name):
try:
    url = f"https://api.aladhan.com/v1/timingsByCity?city={city_name}&country="
    r = requests.get(url, timeout=10).json()
    return r['data']['timings'] if r['code'] == 200 else None
except Exception as e:
    return None

def speak_gtts(text):
try:
    clean_text = re.sub(r'[*_#]', '', text)
    tts = gTTS(text=clean_text[:1000], lang='en')
    fp = io.BytesIO()
    tts.write_to_fp(fp)
    return fp.getvalue()
except Exception as e:
    return None

def get_data(s_id, a_id=None):
try:
    u = f"https://api.quran.com/api/v4/verses/by_key/{s_id}:{a_id}" if a_id else f"https://api.quran.com/api/v4/verses/by_chapter/{s_id}"
    p = {"translations": st.session_state.trans_lang, "fields": "text_uthmani", "per_page": 20}
    r = requests.get(u, params=p).json()
    return [r.get('verse')] if a_id else r.get('verses', [])
except Exception as e:
    return []

def get_audio_url(verse_key):
try:
    s, ay = verse_key.split(':')
    return f"https://everyayah.com/data/Alafasy_128kbps/{s.zfill(3)}{ay.zfill(3)}.mp3"
except Exception as e:
    return None

# ==========================================
# 4. UI COMPONENTS
# ==========================================
def render_top_bar(title="DeenAI"):
st.markdown(f"""
<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.5rem;">
    <div style="display:flex; align-items:center; gap:0.5rem;">
        <div style="width:2rem; height:2rem; border-radius:9999px; background-color:#142f23; display:flex; align-items:center; justify-content:center; border:1px solid rgba(242,202,80,0.2);">
            <span class="material-symbols-outlined" style="color:#d4af37; font-size:1rem;">spa</span>
        </div>
        <h1 style="color:#d4af37; font-family:'Plus Jakarta Sans',sans-serif; font-weight:700; font-size:1.5rem; margin:0;">{title}</h1>
    </div>
</div>
""", unsafe_allow_html=True)

def render_bottom_nav():
st.markdown("""
<div style="height:5rem;"></div>  <!-- Spacer for bottom nav -->

<div class="bottom-nav">
    <a href="#home" onclick="changeTab('Dashboard')" class="nav-item {}" id="nav-home">
        <span class="material-symbols-outlined">home</span>
        <span class="nav-label">Home</span>
    </a>
    <a href="#quran" onclick="changeTab('Quran Reader')" class="nav-item {}" id="nav-quran">
        <span class="material-symbols-outlined">menu_book</span>
        <span class="nav-label">Quran</span>
    </a>
    <a href="#hadith" onclick="changeTab('Hadith Search')" class="nav-item {}" id="nav-hadith">
        <span class="material-symbols-outlined">auto_stories</span>
        <span class="nav-label">Hadith</span>
    </a>
</div>

<script>
    function changeTab(tab) {
        window.parent.postMessage({type: "nav_change", value: tab}, "*");
    }
</script>
""".format(
    "active" if st.session_state.app_mode == "Dashboard" else "",
    "active" if st.session_state.app_mode == "Quran Reader" else "",
    "active" if st.session_state.app_mode == "Hadith Search" else ""
), unsafe_allow_html=True)

# ==========================================
# 5. PAGE IMPLEMENTATIONS
# ==========================================

# --- DASHBOARD / HOME ---
def show_dashboard():
render_top_bar("The Digital Maqam")

# Welcome section
st.markdown("""
<div style="margin-bottom: 2rem;">
    <p style="color:#dac58d; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.2em; margin-bottom:0.25rem;">Assalamu Alaikum</p>
    <h2 style="font-family:'Plus Jakarta Sans', sans-serif; font-size:2rem; font-weight:800; margin-top:0;">Digital Sanctuary</h2>
</div>
""", unsafe_allow_html=True)

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
    <div class="card">
        <div style="display:flex; justify-content:space-between; margin-bottom:1rem;">
            <span style="background:rgba(242,202,80,0.1); color:#d4af37; padding:0.25rem 0.75rem; border-radius:9999px; font-size:0.625rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; border:1px solid rgba(242,202,80,0.2);">
                Verse of the Day
            </span>
            <span style="color:var(--on-surface-variant); font-size:0.75rem;">
                Surah {todays_key}
            </span>
        </div>
        <p class="arabic-txt" style="color:#ffffff; margin-bottom:1rem;">{text_ar}</p>
        <p style="color:#d4af37; font-style:italic; font-size:0.875rem; line-height:1.6; margin-top:1rem; border-top:1px solid rgba(212,175,55,0.1); padding-top:0.5rem;">
            "{trans_text}"
        </p>
    </div>
    """, unsafe_allow_html=True)

# Prayer Times
st.markdown("""
<h3 style="font-family:'Plus Jakarta Sans', sans-serif; font-size:1rem; margin-top:2rem; margin-bottom:1rem; text-transform:uppercase; letter-spacing:0.05em;">Prayer Times</h3>
""", unsafe_allow_html=True)

pt = get_prayer_times(st.session_state.user_city)
if pt:
    col1, col2, col3, col4, col5 = st.columns(5)
    
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
            active_class = "prayer-time-box active-prayer" if prayer.get("active") else "prayer-time-box"
            text_color = '#3c2f00' if prayer.get("active") else 'var(--on-surface)'
            
            st.markdown(f"""
            <div class="{active_class}">
                <span class="material-symbols-outlined">{prayer['icon']}</span>
                <div style="font-size:0.625rem; font-weight:700; text-transform:uppercase; letter-spacing:0.05em; margin-top:0.5rem; color:{text_color};">{prayer['name']}</div>
                <div style="font-size:1.125rem; font-weight:700; margin-top:0.25rem; color:{text_color};">{prayer['time']}</div>
            </div>
            """, unsafe_allow_html=True)

# AI Chat
st.markdown("<h3 style='margin-top:2rem; margin-bottom:1rem;'>Chat with DeenAI</h3>", unsafe_allow_html=True)

for m in st.session_state.messages:
    with st.chat_message(m["role"]): 
        st.markdown(m["content"])

prompt = st.chat_input("Ask DeenAI...")
audio_bytes = mic_recorder(start_prompt="🎤 Speak", stop_prompt="🛑 Stop", key='mic', just_once=True)

if prompt or audio_bytes:
    u_input = prompt
    if audio_bytes:
        with open("temp.wav", "wb") as f: f.write(audio_bytes['bytes'])
        with open("temp.wav", "rb") as af:
            u_input = client.audio.transcriptions.create(model="whisper-large-v3", file=af).text
    
    st.session_state.messages.append({"role": "user", "content": u_input})
    with st.chat_message("user"): st.markdown(u_input)

    with st.chat_message("assistant"):
        sys_p = "You are DeenAI, a devout Muslim companion. Answer strictly from Quran and Sahih Hadith. Cite [Surah:Ayah] and Hadith numbers."
        res = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role":"system","content": sys_p}] + st.session_state.messages).choices[0].message.content
        st.markdown(res)
        audio_out = speak_gtts(res)
        if audio_out: st.audio(audio_out, autoplay=True)
        st.session_state.messages.append({"role": "assistant", "content": res})

render_bottom_nav()

# --- QURAN READER ---
def show_quran_reader():
render_top_bar("Quran Reader")

st.markdown("""
<div style="background:linear-gradient(to bottom right, #142f23, #042015); border-left:4px solid #d4af37; padding:1.5rem; border-radius:0.75rem; margin-bottom:2rem;">
    <h2 style="font-family:'Plus Jakarta Sans',sans-serif; font-size:1.75rem; font-weight:700; margin-bottom:0.5rem;">Surah Al-Fatihah</h2>
    <p style="color:#d0c5af; margin-bottom:1rem;">"The Opening" — Revealed in Makkah, consisting of 7 Ayahs</p>
    <p class="arabic-txt" style="color:#d4af37; font-size:1.5rem; margin-top:1rem;">سُورَةُ ٱلْفَاتِحَةِ</p>
</div>
""", unsafe_allow_html=True)

# Bismillah
st.markdown("""
<div style="text-align:center; margin-bottom:2rem;">
    <p class="arabic-txt" style="color:#ffffff; font-size:1.75rem;">بِسْمِ ٱللَّهِ ٱلرَّحْمَـٰنِ ٱلرَّحِيمِ</p>
    <p style="color:#d0c5af; font-style:italic; margin-top:0.5rem;">In the name of Allah, the Entirely Merciful, the Especially Merciful.</p>
</div>
""", unsafe_allow_html=True)

# Surah selector (simplified)
s_choice = st.number_input("Surah", 1, 114, 1, label_visibility="collapsed")
v_list = get_data(s_choice)

# Display verses
for v in v_list:
    verse_key = v.get('verse_key', '')
    text_ar = v.get('text_uthmani', '')
    trans_text = re.sub('<[^<]+?>', '', v.get('translations', [{}])[0].get('text', ''))
    
    st.markdown(f"""
    <div class="verse-card">
        <p class="arabic-txt" style="color:#ffffff; margin-bottom:1rem;">{text_ar}</p>
        <p style="color:#d0c5af; margin-bottom:1rem;">{trans_text}</p>
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span style="color:#d4af37; font-size:0.75rem;">{verse_key}</span>
            <button style="background:transparent; border:none; color:#d4af37; cursor:pointer; display:flex; align-items:center; gap:0.5rem;">
                <span class="material-symbols-outlined" style="font-size:1rem;">play_arrow</span>
                <span style="font-size:0.75rem; text-transform:uppercase;">Play</span>
            </button>
        </div>
        <audio controls style="width:100%; margin-top:1rem; height:30px; opacity:0.7;">
            <source src="{get_audio_url(verse_key)}" type="audio/mp3">
        </audio>
    </div>
    """, unsafe_allow_html=True)

render_bottom_nav()

# --- HADITH SEARCH ---
def show_hadith_search():
render_top_bar("Hadith Library")

st.markdown("""
<h2 style="font-family:'Plus Jakarta Sans',sans-serif; font-size:2rem; font-weight:700; margin-bottom:1rem; color:#d4af37;">Hadith Library</h2>
<p style="color:#d0c5af; margin-bottom:2rem;">Explore the preserved wisdom of the Prophet Muhammad (PBUH) through the most authentic collections.</p>
""", unsafe_allow_html=True)

# Search box
topic = st.text_input("Search by topic", placeholder="e.g. Prayer, Fasting, Patience...")

if topic:
    with st.spinner("Searching Sahihayn..."):
        res = client.chat.completions.create(
            messages=[
                {"role":"system","content":"Answer only using Sahih Bukhari and Sahih Muslim. Provide Hadith numbers."},
                {"role":"user","content":topic}
            ],
            model="llama-3.3-70b-versatile"
        ).choices[0].message.content
        
        st.markdown(f"""
        <div class="card">
            <h3 style="margin-bottom:1rem; font-family:'Plus Jakarta Sans',sans-serif;">Results for "{topic}"</h3>
            <div style="padding:1rem; background:rgba(20,47,35,0.6); border-radius:0.75rem; line-height:1.6;">
                {res}
            </div>
        </div>
        """, unsafe_allow_html=True)
else:
    # Display collections if no search
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        <div style="background:#082419; padding:1.5rem; border-radius:0.75rem; margin-bottom:1rem; position:relative; overflow:hidden;">
            <div style="position:absolute; top:1rem; right:1rem; opacity:0.1; font-family:'Amiri',serif; font-size:3rem; direction:rtl;">البخاري</div>
            <span style="background:rgba(242,202,80,0.1); color:#d4af37; padding:0.25rem 0.75rem; border-radius:9999px; font-size:0.625rem; text-transform:uppercase; letter-spacing:0.1em; display:inline-block; margin-bottom:1rem;">Most Authentic</span>
            <h3 style="margin-bottom:0.5rem; font-family:'Plus Jakarta Sans',sans-serif;">Sahih al-Bukhari</h3>
            <p style="color:#d0c5af; font-size:0.875rem; margin-bottom:1rem;">The most authentic book after the Holy Quran with 7,563 hadiths.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div style="background:#082419; padding:1.5rem; border-radius:0.75rem; margin-bottom:1rem; height:100%;">
            <h3 style="margin-bottom:0.5rem; font-family:'Plus Jakarta Sans',sans-serif;">Sahih Muslim</h3>
            <p style="color:#d0c5af; font-size:0.875rem; margin-bottom:1rem;">The second most authentic book with 3,033 hadiths.</p>
        </div>
        """, unsafe_allow_html=True)
        
    # Hadith of the Day
    st.markdown("""
    <div style="margin-top:2rem; padding:1.5rem; background:#082419; border-radius:0.75rem; border-left:4px solid #d4af37;">
        <span style="font-size:0.75rem; text-transform:uppercase; letter-spacing:0.1em; color:#d4af37; margin-bottom:1rem; display:block;">Hadith of the Day</span>
        <p class="arabic-txt" style="color:#ffffff; margin-bottom:0.5rem;">"إِنَّمَا الأَعْمَالُ بِالنِّيَّاتِ"</p>
        <p style="color:#d0c5af; font-style:italic; margin-top:1rem; margin-bottom:1rem; font-size:1.125rem;">"Actions are but by intentions and every man shall have only that which he intended."</p>
        <div style="color:#d4af37; font-size:0.75rem; text-align:right;">Sahih al-Bukhari 1</div>
    </div>
    """, unsafe_allow_html=True)

render_bottom_nav()

# ==========================================
# 6. NAVIGATION HANDLER
# ==========================================
# Listen for navigation events from JavaScript
nav_change = streamlit_js_eval(js_expressions=[
'function listenForNavChange() {',
'  window.addEventListener("message", function(event) {',
'    if(event.data && event.data.type === "nav_change") return event.data.value;',
'    return null;',
'  });',
'  return null;',
'}',
'listenForNavChange();'
], key=f"nav_listener_{datetime.now().timestamp()}", want_output=True)

if nav_change in ["Dashboard", "Quran Reader", "Hadith Search"]:
st.session_state.app_mode = nav_change
st.rerun()

# Display the current page
if st.session_state.app_mode == "Dashboard":
show_dashboard()
elif st.session_state.app_mode == "Quran Reader":
show_quran_reader()
elif st.session_state.app_mode == "Hadith Search":
show_hadith_search()
