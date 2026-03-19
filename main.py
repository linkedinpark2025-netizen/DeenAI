import os, requests, re, streamlit as st, io
from groq import Groq
from gtts import gTTS 
from streamlit_mic_recorder import mic_recorder
from datetime import datetime
from streamlit_js_eval import streamlit_js_eval

# ==========================================
# 1. INITIALIZATION & SESSION STATE
# ==========================================
if 'messages' not in st.session_state: 
    st.session_state.messages = [{"role": "assistant", "content": "Assalamu Alaikum. I am Noor, your digital companion. How may I assist your heart today?"}]
if 'user_city' not in st.session_state: st.session_state.user_city = "London"
if 'app_mode' not in st.session_state: st.session_state.app_mode = "Home"
if 'current_surah' not in st.session_state: st.session_state.current_surah = 1

G_KEY = st.secrets["GROQ_API_KEY"] if "GROQ_API_KEY" in st.secrets else os.environ.get("GROQ_API_KEY")
client = Groq(api_key=G_KEY)

# ==========================================
# 2. PREMIUM DESIGN SYSTEM (Tailwind & CSS)
# ==========================================
st.set_page_config(page_title="The Digital Maqam", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;700;800&family=Inter:wght@400;600&family=Amiri:wght@400;700&display=swap" rel="stylesheet"/>
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
    <style>
        .stApp { background-color: #00180d; color: #cbead7; }
        .gold-gradient { background: linear-gradient(135deg, #f2ca50 0%, #d4af37 100%); }
        .message-gradient { background: linear-gradient(135deg, #142f23 0%, #082419 100%); border: 1px solid rgba(242, 202, 80, 0.15); }
        .nav-active { color: #f2ca50 !important; background: #142f23; border-radius: 9999px; box-shadow: 0 0 15px rgba(242,202,80,0.2); }
        .no-scrollbar::-webkit-scrollbar { display: none; }
        #MainMenu, footer, header {visibility: hidden;}
        .stButton>button { border-radius: 9999px; background: transparent; border: 1px solid #f2ca50; color: #f2ca50; transition: 0.3s; }
        .stButton>button:hover { background: #f2ca50; color: #00180d; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. CORE LOGIC & API FUNCTIONS
# ==========================================

def get_prayer_times(city):
    try:
        r = requests.get(f"https://api.aladhan.com/v1/timingsByCity?city={city}&country=").json()
        return r['data']['timings'] if r['code'] == 200 else None
    except: return None

def get_surah(s_id):
    try:
        r = requests.get(f"https://api.quran.com/api/v4/verses/by_chapter/{s_id}?language=en&words=true&translations=131&fields=text_uthmani&per_page=10").json()
        return r.get('verses', [])
    except: return []

def noor_chat(prompt):
    st.session_state.messages.append({"role": "user", "content": prompt})
    sys_msg = "You are Noor, a compassionate AI spiritual guide. Provide gentle Islamic guidance using Quran and Hadith. Keep responses concise and use a mix of English and Arabic for greetings/key terms."
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-specdec",
            messages=[{"role": "system", "content": sys_msg}] + st.session_state.messages
        )
        msg = response.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": msg})
        return msg
    except: return "I apologize, my connection to the wisdom clouds is faint. Please try again."

# ==========================================
# 4. TOP BAR & LOCATION
# ==========================================
st.markdown("""
    <header class="fixed top-0 w-full z-50 bg-[#00180d]/80 backdrop-blur-xl flex justify-between items-center px-6 h-16 shadow-lg">
        <h1 class="text-[#f2ca50] font-bold tracking-widest uppercase text-lg">Digital Sanctuary</h1>
        <div class="w-10 h-10 rounded-full border-2 border-[#f2ca50]/20 overflow-hidden">
            <img src="https://api.dicebear.com/7.x/bottts/svg?seed=Noor" class="w-full h-full object-cover">
        </div>
    </header>
""", unsafe_allow_html=True)

# ==========================================
# 5. APP VIEWS
# ==========================================

# --- HOME VIEW ---
if st.session_state.app_mode == "Home":
    st.markdown("<div class='pt-24 px-6'><p class='text-[#dac58d] text-xs uppercase tracking-widest'>Assalamu Alaikum</p><h2 class='text-4xl font-extrabold'>Welcome Back</h2></div>", unsafe_allow_html=True)
    pt = get_prayer_times(st.session_state.user_city)
    if pt:
        st.markdown("<div class='px-6 mt-8 flex gap-3 overflow-x-auto no-scrollbar'>", unsafe_allow_html=True)
        st.write("Current Prayer Times for " + st.session_state.user_city)
        cols = st.columns(len(['Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']))
        for i, (k,v) in enumerate([(k,v) for k,v in pt.items() if k in ['Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']]):
            cols[i].markdown(f"<div class='bg-[#142f23] p-4 rounded-xl text-center border border-[#f2ca50]/10'><p class='text-[10px] font-bold text-[#f2ca50]'>{k}</p><p class='text-lg font-bold'>{v}</p></div>", unsafe_allow_html=True)

# --- QURAN VIEW ---
elif st.session_state.app_mode == "Quran":
    st.markdown("<div class='pt-24 px-6'>", unsafe_allow_html=True)
    s_id = st.number_input("Select Surah Number", min_value=1, max_value=114, value=st.session_state.current_surah)
    st.session_state.current_surah = s_id
    verses = get_surah(s_id)
    
    st.markdown(f"<div class='bg-gradient-to-br from-[#142f23] to-[#042015] p-8 rounded-2xl border-l-4 border-[#f2ca50] mb-8'> <h2 class='text-3xl font-bold text-[#f2ca50]'>Surah {s_id}</h2> </div>", unsafe_allow_html=True)
    
    for v in verses:
        st.markdown(f"""
            <div class='bg-[#042015] p-6 rounded-xl mb-4 border border-[#f2ca50]/5 hover:bg-[#142f23] transition-all'>
                <p class='font-["Amiri"] text-3xl text-right text-[#f2ca50] leading-relaxed' dir='rtl'>{v['text_uthmani']}</p>
                <p class='text-sm mt-4 text-[#cbead7]/80'>{v['translations'][0]['text']}</p>
            </div>
        """, unsafe_allow_html=True)

# --- AI GUIDE (NOOR) VIEW ---
elif st.session_state.app_mode == "Guide":
    st.markdown("<div class='pt-24 px-6 pb-44 max-w-3xl mx-auto'>", unsafe_allow_html=True)
    for m in st.session_state.messages:
        role_class = "items-end ml-auto" if m["role"] == "user" else "items-start"
        bubble_class = "bg-[#1f3a2d]" if m["role"] == "user" else "message-gradient"
        name = "You" if m["role"] == "user" else "Noor"
        st.markdown(f"""
            <div class="flex flex-col {role_class} gap-2 mb-6 max-w-[85%]">
                <span class="text-[10px] font-bold text-[#f2ca50] tracking-widest uppercase ml-2">{name}</span>
                <div class="{bubble_class} p-5 rounded-2xl shadow-lg">
                    <p class="text-sm leading-relaxed">{m["content"]}</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Input area
    with st.container():
        st.markdown("<div class='fixed bottom-24 left-0 w-full px-6 z-40'><div class='max-w-3xl mx-auto'>", unsafe_allow_html=True)
        user_input = st.chat_input("Speak your heart...")
        if user_input:
            noor_chat(user_input)
            st.rerun()
        st.markdown("</div></div>", unsafe_allow_html=True)

# ==========================================
# 6. BOTTOM NAVIGATION (Universal)
# ==========================================
st.markdown("<div class='pb-32'></div>", unsafe_allow_html=True)
nav_cols = st.columns(3)
if nav_cols[0].button("🏠 Home", use_container_width=True): 
    st.session_state.app_mode = "Home"; st.rerun()
if nav_cols[1].button("📖 Quran", use_container_width=True): 
    st.session_state.app_mode = "Quran"; st.rerun()
if nav_cols[2].button("✨ Guide", use_container_width=True): 
    st.session_state.app_mode = "Guide"; st.rerun()

# Styling for the navigation (visual only)
st.markdown(f"""
    <nav class="fixed bottom-0 w-full rounded-t-[2.5rem] z-50 bg-[#042015]/95 backdrop-blur-md flex justify-around items-center h-24 px-4 pb-6 shadow-2xl">
        <div class="flex flex-col items-center {'nav-active px-6 py-2' if st.session_state.app_mode == 'Home' else 'text-[#d0c5af]'}">
            <span class="material-symbols-outlined">home</span>
            <span class="text-[9px] uppercase font-bold mt-1">Home</span>
        </div>
        <div class="flex flex-col items-center {'nav-active px-6 py-2' if st.session_state.app_mode == 'Quran' else 'text-[#d0c5af]'}">
            <span class="material-symbols-outlined">menu_book</span>
            <span class="text-[9px] uppercase font-bold mt-1">Quran</span>
        </div>
        <div class="flex flex-col items-center {'nav-active px-6 py-2' if st.session_state.app_mode == 'Guide' else 'text-[#d0c5af]'}">
            <span class="material-symbols-outlined">auto_awesome</span>
            <span class="text-[9px] uppercase font-bold mt-1">Guide</span>
        </div>
    </nav>
""", unsafe_allow_html=True)
