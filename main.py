import streamlit as st
import requests
import os
from groq import Groq

# --- INITIALIZATION ---
if 'app_mode' not in st.session_state: st.session_state.app_mode = "Guide"
if 'messages' not in st.session_state: 
    st.session_state.messages = [{"role": "assistant", "content": "Assalamu Alaikum. I am Noor, your digital companion on this spiritual journey. How may I assist your heart today?"}]

G_KEY = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
client = Groq(api_key=G_KEY) if G_KEY else None

# --- UI CONFIG ---
st.set_page_config(page_title="Digital Sanctuary", layout="wide", initial_sidebar_state="collapsed")

# --- FULL CSS INJECTION (Your exact styling) ---
st.markdown("""
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;700;800&family=Inter:wght@400;600&family=Amiri:wght@400;700&display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
<style>
    /* Hide Streamlit Native UI */
    #MainMenu, footer, header {visibility: hidden;}
    .stApp { background-color: #00180d; }
    .stChatInputContainer { bottom: 110px !important; background: transparent !important; border: none !important; }
    
    /* Your Custom Classes */
    .message-gradient { background: linear-gradient(135deg, #142f23 0%, #082419 100%); }
    .ai-border { border: 1px solid rgba(242, 202, 80, 0.15); }
    .gold-glow { box-shadow: 0 0 20px rgba(242, 202, 80, 0.15); }
    .arabic-font { font-family: 'Amiri', serif; }
</style>
""", unsafe_allow_html=True)

# --- HEADER (Shared) ---
st.markdown(f"""
<header class="fixed top-0 w-full z-50 bg-[#00180d]/80 backdrop-blur-xl flex justify-between items-center px-6 h-16 shadow-[0_4px_30px_rgba(0,26,15,0.6)]">
    <div class="flex items-center gap-4">
        <span class="material-symbols-outlined text-[#f2ca50]">menu</span>
        <h1 class="text-[#f2ca50] font-bold tracking-widest uppercase text-lg">Digital Sanctuary</h1>
    </div>
    <div class="flex items-center gap-3">
        <div class="text-right">
            <p class="text-[#f2ca50] text-[10px] font-bold uppercase tracking-tighter">Noor AI</p>
            <p class="text-[#cbead7] text-[8px] opacity-60">Spiritual Guide</p>
        </div>
        <div class="w-10 h-10 rounded-full border-2 border-[#f2ca50]/20 overflow-hidden">
            <img src="https://api.dicebear.com/7.x/bottts/svg?seed=Noor" class="w-full h-full object-cover">
        </div>
    </div>
</header>
""", unsafe_allow_html=True)

# --- MAIN CONTENT AREA ---
content_container = st.container()

with content_container:
    # --- CHAT MODE ---
    if st.session_state.app_mode == "Guide":
        st.markdown("<main class='pt-24 pb-44 px-4 max-w-3xl mx-auto space-y-8'>", unsafe_allow_html=True)
        
        for m in st.session_state.messages:
            if m["role"] == "assistant":
                st.markdown(f"""
                <div class="flex flex-col items-start gap-2 max-w-[90%] mb-6">
                    <div class="flex items-center gap-2 ml-2">
                        <span class="w-2 h-2 rounded-full bg-[#f2ca50] animate-pulse"></span>
                        <span class="text-[10px] font-bold text-[#f2ca50] tracking-widest uppercase">Noor</span>
                    </div>
                    <div class="message-gradient ai-border rounded-t-xl rounded-br-xl p-5 gold-glow">
                        <p class="text-[#cbead7] text-sm leading-relaxed">{m['content']}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="flex flex-col items-end gap-2 max-w-[85%] ml-auto mb-6">
                    <div class="bg-[#1f3a2d] rounded-t-xl rounded-bl-xl p-5">
                        <p class="text-[#cbead7] text-sm leading-relaxed">{m['content']}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # Chat Logic
        prompt = st.chat_input("Speak your heart...")
        if prompt:
            st.session_state.messages.append({"role": "user", "content": prompt})
            if client:
                res = client.chat.completions.create(
                    model="llama-3.3-70b-specdec",
                    messages=[{"role": "system", "content": "You are Noor, a spiritual guide. Be concise, empathetic, and use Islamic wisdom."}] + st.session_state.messages
                )
                st.session_state.messages.append({"role": "assistant", "content": res.choices[0].message.content})
            st.rerun()

    # --- QURAN MODE ---
    elif st.session_state.app_mode == "Library":
        st.markdown("<main class='pt-24 px-6 max-w-4xl mx-auto space-y-12'>", unsafe_allow_html=True)
        
        # Surah Header (Static for Al-Fatihah in this demo)
        st.markdown("""
        <section class="relative overflow-hidden rounded-lg p-8 bg-gradient-to-br from-[#142f23] to-[#042015] border-l-4 border-[#f2ca50]">
            <div class="relative z-10 flex flex-col md:flex-row justify-between items-center gap-6">
                <div>
                    <span class="text-xs uppercase tracking-[0.2em] text-[#f2ca50]/80 mb-2 block">Now Reading</span>
                    <h2 class="text-4xl font-extrabold text-[#cbead7]">Surah Al-Fatihah</h2>
                    <p class="text-[#d0c5af] mt-2 text-sm italic">"The Opening" — 7 Ayahs</p>
                </div>
                <div class="text-right"><span class="arabic-font text-5xl text-[#f2ca50] block" dir="rtl">سُورَةُ ٱلْفَاتِحَةِ</span></div>
            </div>
        </section>
        """, unsafe_allow_html=True)

        # Ayahs (Fetching example)
        try:
            r = requests.get("https://api.quran.com/api/v4/verses/by_chapter/1?language=en&translations=131&fields=text_uthmani").json()
            for i, v in enumerate(r['verses'][:5]):
                st.markdown(f"""
                <div class="group p-6 rounded-lg bg-[#042015] border border-[#f2ca50]/5 hover:bg-[#142f23] transition-all mb-4">
                    <div class="flex items-start justify-between gap-8 mb-4">
                        <div class="w-8 h-8 rounded-full border border-[#f2ca50]/30 flex items-center justify-center text-[#f2ca50] text-xs">{i+1}</div>
                        <p class="arabic-font text-3xl text-[#cbead7] text-right w-full" dir="rtl">{v['text_uthmani']}</p>
                    </div>
                    <p class="text-sm text-[#cbead7]/80 pl-12">{v['translations'][0]['text']}</p>
                </div>
                """, unsafe_allow_html=True)
        except: st.error("Library connection lost.")

# --- NAVIGATION BAR (The engine that changes modes) ---
# We use a trick: 4 invisible buttons over your HTML icons
st.markdown("<div style='height: 120px;'></div>", unsafe_allow_html=True) # Space for nav

nav_html = """
<nav class="fixed bottom-0 w-full rounded-t-[32px] z-50 bg-[#042015]/95 backdrop-blur-md flex justify-around items-center px-4 pb-6 pt-2 shadow-[0_-8px_40px_rgba(0,0,0,0.5)]">
    <div id="btn-guide" class="flex flex-col items-center justify-center p-3 cursor-pointer">
        <span class="material-symbols-outlined">forum</span>
        <span class="text-[10px]">Guide</span>
    </div>
    <div id="btn-library" class="flex flex-col items-center justify-center p-3 cursor-pointer">
        <span class="material-symbols-outlined">menu_book</span>
        <span class="text-[10px]">Library</span>
    </div>
</nav>
"""
st.markdown(nav_html, unsafe_allow_html=True)

# Streamlit Buttons (Placed at bottom for control)
col1, col2 = st.columns(2)
if col1.button("✨ Switch to Guide", use_container_width=True):
    st.session_state.app_mode = "Guide"
    st.rerun()
if col2.button("📖 Open Library", use_container_width=True):
    st.session_state.app_mode = "Library"
    st.rerun()

# Background Ornament
st.markdown("""
<div class="fixed top-0 left-0 w-full h-full pointer-events-none -z-10 overflow-hidden opacity-10">
    <div class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px]">
        <svg class="w-full h-full fill-[#f2ca50]" viewBox="0 0 100 100">
            <path d="M50 0 L60 40 L100 50 L60 60 L50 100 L40 60 L0 50 L40 40 Z"></path>
        </svg>
    </div>
</div>
""", unsafe_allow_html=True)
