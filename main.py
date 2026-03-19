import os, requests, re, streamlit as st, datetime, io, base64
from groq import Groq
from gtts import gTTS 
from streamlit_mic_recorder import mic_recorder

# --- 1. INITIALIZATION ---
if 'app_mode' not in st.session_state: st.session_state.app_mode = "Home"
if 'messages' not in st.session_state: st.session_state.messages = []

G_KEY = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
client = Groq(api_key=G_KEY) if G_KEY else None

# --- 2. THEME & CSS (Your Exact Colors) ---
st.set_page_config(page_title="The Digital Maqam", layout="wide", initial_sidebar_state="collapsed")

def local_css():
    st.markdown("""
    <script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;700;800&family=Inter:wght@400;600&family=Amiri:wght@400;700&display=swap" rel="stylesheet"/>
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
    <style>
        /* Base Overrides */
        .stApp { background-color: #00180d; color: #cbead7; }
        [data-testid="stHeader"], [data-testid="stToolbar"] { display: none; }
        .main .block-container { padding: 0; max-width: 100%; }
        
        /* Custom Styles from your HTML */
        .gold-gradient { background: linear-gradient(135deg, #f2ca50 0%, #d4af37 100%); }
        .arabic-font { font-family: 'Amiri', serif; }
        .glass-card { background: rgba(31, 58, 45, 0.6); backdrop-filter: blur(20px); border: 1px solid rgba(242, 202, 80, 0.1); }
        
        /* Hide Scrollbar */
        .no-scrollbar::-webkit-scrollbar { display: none; }
        
        /* Fixed Footer Fix */
        .nav-active { color: #f2ca50 !important; background: #142f23; border-radius: 999px; padding: 4px 16px; box-shadow: 0 0 15px rgba(242,202,80,0.2); }
    </style>
    """, unsafe_allow_html=True)

local_css()

# --- 3. UI COMPONENTS ---

def render_top_bar():
    st.markdown(f"""
    <header class="fixed top-0 w-full z-[100] bg-[#00180d]/60 backdrop-blur-xl flex justify-between items-center px-6 h-16">
        <div class="flex items-center gap-3">
            <div class="w-8 h-8 rounded-full bg-[#d4af37] flex items-center justify-center text-[#3c2f00]">
                <span class="material-symbols-outlined text-sm">spa</span>
            </div>
            <h1 class="text-xl font-bold tracking-[0.1em] text-[#f2ca50] uppercase font-['Plus_Jakarta_Sans']">The Digital Maqam</h1>
        </div>
        <div class="flex items-center gap-4">
            <span class="material-symbols-outlined text-[#cbead7]/70">settings</span>
        </div>
    </header>
    """, unsafe_allow_html=True)

def render_bottom_nav():
    # Since HTML buttons can't trigger Python, we use a Columns-based layout that mimics your nav
    st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)
    cols = st.columns(4)
    with cols[0]: 
        if st.button("🏠 Home", use_container_width=True): st.session_state.app_mode = "Home"; st.rerun()
    with cols[1]: 
        if st.button("📖 Quran", use_container_width=True): st.session_state.app_mode = "Quran"; st.rerun()
    with cols[2]: 
        if st.button("📜 Hadith", use_container_width=True): st.session_state.app_mode = "Hadith"; st.rerun()
    with cols[3]: 
        if st.button("🧭 Qibla", use_container_width=True): st.session_state.app_mode = "Qibla"; st.rerun()

# --- 4. PAGE ROUTING ---

render_top_bar()

if st.session_state.app_mode == "Home":
    st.markdown("""
    <main class="pt-24 px-6 max-w-2xl mx-auto space-y-10">
        <section>
            <p class="text-[#dac58d] tracking-widest uppercase text-xs mb-1">Assalamu Alaikum</p>
            <h2 class="text-4xl font-extrabold tracking-tight text-[#cbead7]">Digital Sanctuary</h2>
        </section>
        
        <section class="relative bg-[#042015] border border-[#f2ca50]/20 rounded-lg p-8 overflow-hidden">
            <div class="space-y-6">
                <div class="flex justify-between items-center">
                    <span class="bg-[#f2ca50]/10 text-[#f2ca50] px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider">Verse of the Day</span>
                    <span class="text-[#d0c5af] text-xs">Surah Al-Baqarah 2:255</span>
                </div>
                <p class="arabic-font text-right text-3xl leading-[1.8] text-[#f2ca50]" dir="rtl">
                    اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ
                </p>
                <p class="text-[#d0c5af] italic text-sm leading-relaxed">
                    "Allah! There is no god but He, the Living, the Self-subsisting..."
                </p>
            </div>
        </section>

        <h3 class="text-sm font-bold text-[#cbead7] tracking-wider uppercase">Prayer Times</h3>
        <div class="grid grid-cols-3 gap-3">
            <div class="gold-gradient text-[#3c2f00] p-4 rounded-lg text-center shadow-lg">
                <p class="text-[10px] font-bold uppercase">Dhuhr</p>
                <p class="text-lg font-extrabold">12:58</p>
            </div>
            <div class="bg-[#142f23] p-4 rounded-lg text-center border border-[#4d4635]">
                <p class="text-[10px] font-bold uppercase">Asr</p>
                <p class="text-lg font-extrabold">15:22</p>
            </div>
            <div class="bg-[#142f23] p-4 rounded-lg text-center border border-[#4d4635]">
                <p class="text-[10px] font-bold uppercase">Maghrib</p>
                <p class="text-lg font-extrabold">18:05</p>
            </div>
        </div>
    </main>
    """, unsafe_allow_html=True)
    
    # AI CHAT BOX (Integrated with your Groq logic)
    st.markdown("<br>", unsafe_allow_html=True)
    prompt = st.chat_input("Ask Noor Spiritual Guide...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        if client:
            res = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": "You are Noor, a spiritual guide."}] + st.session_state.messages
            ).choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": res})
        st.rerun()

    for m in reversed(st.session_state.messages):
        bg = "#1f3a2d" if m["role"] == "assistant" else "#042015"
        st.markdown(f"""<div style="background:{bg}; padding:15px; border-radius:15px; margin-bottom:10px; border: 1px solid rgba(242,202,80,0.1)">{m['content']}</div>""", unsafe_allow_html=True)

elif st.session_state.app_mode == "Hadith":
    st.markdown("""
    <main class="pt-24 px-6 max-w-5xl mx-auto">
        <header class="mb-12">
            <h1 class="text-4xl font-extrabold text-[#f2ca50] mb-4">Hadith Library</h1>
            <p class="text-[#d0c5af] max-w-xl leading-relaxed">Explore the preserved wisdom of the Prophet Muhammad (PBUH).</p>
        </header>
    </main>
    """, unsafe_allow_html=True)
    
    search_query = st.text_input("Search Hadith...", placeholder="Search Hadith, narrators, or topics...")
    if search_query:
        # Search logic from your original file
        st.info(f"Searching for {search_query}...")

render_bottom_nav()
