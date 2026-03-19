import os, requests, re, streamlit as st, datetime, io
from groq import Groq
from gtts import gTTS 
from streamlit_mic_recorder import mic_recorder

# ==========================================
# 1. INITIALIZATION & SESSION STATE
# ==========================================
if 'app_mode' not in st.session_state: st.session_state.app_mode = "Home"
if 'messages' not in st.session_state: st.session_state.messages = []
if 'user_city' not in st.session_state: st.session_state.user_city = "London"
if 'trans_lang' not in st.session_state: st.session_state.trans_lang = "131"

G_KEY = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
client = Groq(api_key=G_KEY) if G_KEY else None

# ==========================================
# 2. UTILITY FUNCTIONS (Must be above UI)
# ==========================================

def get_prayer_times(city_name):
    try:
        url = f"https://api.aladhan.com/v1/timingsByCity?city={city_name}&country="
        r = requests.get(url, timeout=10).json()
        return r['data']['timings'] if r['code'] == 200 else None
    except: return None

def get_data(s_id, a_id=None):
    u = f"https://api.quran.com/api/v4/verses/by_key/{s_id}:{a_id}" if a_id else f"https://api.quran.com/api/v4/verses/by_chapter/{s_id}"
    p = {"translations": st.session_state.trans_lang, "fields": "text_uthmani", "per_page": 20}
    try:
        r = requests.get(u, params=p).json()
        return [r.get('verse')] if a_id else r.get('verses', [])
    except: return []

# ==========================================
# 3. PREMIUM CSS INJECTION
# ==========================================
st.set_page_config(page_title="The Digital Maqam", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;700;800&family=Inter:wght@400;600&family=Amiri:wght@400;700&display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
<style>
    /* Hide Streamlit Elements */
    [data-testid="stHeader"], [data-testid="stToolbar"], footer { display: none !important; }
    .stApp { background-color: #00180d; color: #cbead7; }
    .main .block-container { padding: 0; max-width: 100%; }
    
    /* Custom Components */
    .gold-gradient { background: linear-gradient(135deg, #f2ca50 0%, #d4af37 100%); }
    .arabic-font { font-family: 'Amiri', serif; }
    .glass-card { background: rgba(31, 58, 45, 0.6); backdrop-filter: blur(20px); border: 1px solid rgba(242, 202, 80, 0.1); }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. SHARED UI (TopBar)
# ==========================================
st.markdown(f"""
<header class="fixed top-0 w-full z-50 bg-[#00180d]/60 backdrop-blur-xl flex justify-between items-center px-6 h-16">
    <div class="flex items-center gap-3">
        <div class="w-8 h-8 rounded-full bg-[#d4af37] flex items-center justify-center text-[#3c2f00]">
            <span class="material-symbols-outlined text-sm">spa</span>
        </div>
        <h1 class="text-xl font-bold tracking-[0.1em] text-[#f2ca50] uppercase font-['Plus_Jakarta_Sans']">The Digital Maqam</h1>
    </div>
</header>
""", unsafe_allow_html=True)

# ==========================================
# 5. PAGE CONTENT
# ==========================================

if st.session_state.app_mode == "Home":
    # --- Data Fetching ---
    pt = get_prayer_times(st.session_state.user_city) or {"Dhuhr": "--:--", "Asr": "--:--", "Maghrib": "--:--", "Isha": "--:--", "Fajr": "--:--"}
    
    day_of_year = datetime.date.today().timetuple().tm_yday
    rotation_keys = ["2:255", "2:153", "3:139", "94:5", "2:186"]
    todays_key = rotation_keys[day_of_year % len(rotation_keys)]
    s_id, a_id = todays_key.split(':')
    dv_list = get_data(s_id, a_id)
    
    text_ar = dv_list[0].get('text_uthmani', '') if dv_list else "Loading..."
    trans_text = re.sub('<[^<]+?>', '', dv_list[0].get('translations', [{}])[0].get('text', '')) if dv_list else "Connecting..."

    # --- Render HTML ---
    st.markdown(f"""
    <main class="pt-24 pb-32 px-6 max-w-2xl mx-auto space-y-10">
        <section>
            <p class="text-[#dac58d] tracking-widest uppercase text-xs mb-1">Assalamu Alaikum</p>
            <h2 class="text-4xl font-extrabold tracking-tight text-[#cbead7]">Digital Sanctuary</h2>
        </section>

        <section class="relative bg-[#042015] border border-[#f2ca50]/20 rounded-lg p-8 overflow-hidden shadow-2xl">
            <div class="space-y-6">
                <div class="flex justify-between items-center">
                    <span class="bg-[#f2ca50]/10 text-[#f2ca50] px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider">Verse of the Day</span>
                    <span class="text-[#d0c5af] text-xs">Surah {todays_key}</span>
                </div>
                <p class="arabic-font text-right text-3xl leading-[1.8] text-[#f2ca50]" dir="rtl">{text_ar}</p>
                <p class="text-[#d0c5af] italic text-sm leading-relaxed">"{trans_text}"</p>
            </div>
        </section>

        <section class="space-y-4">
            <div class="flex justify-between items-end">
                <h3 class="text-sm font-bold text-[#cbead7] tracking-wider uppercase">Prayer Times</h3>
                <span class="text-[10px] text-[#d0c5af] uppercase">{st.session_state.user_city}</span>
            </div>
            <div class="flex gap-3 overflow-x-auto pb-2 no-scrollbar">
                <div class="flex-shrink-0 gold-gradient text-[#3c2f00] px-6 py-4 rounded-lg flex flex-col items-center min-w-[100px]">
                    <span class="text-[10px] font-bold uppercase">Dhuhr</span>
                    <span class="text-lg font-extrabold">{pt['Dhuhr']}</span>
                </div>
                <div class="flex-shrink-0 bg-[#142f23] border border-[#4d4635] text-[#cbead7] px-6 py-4 rounded-lg flex flex-col items-center min-w-[100px]">
                    <span class="text-[10px] font-bold uppercase">Asr</span>
                    <span class="text-lg font-extrabold">{pt['Asr']}</span>
                </div>
                <div class="flex-shrink-0 bg-[#142f23] border border-[#4d4635] text-[#cbead7] px-6 py-4 rounded-lg flex flex-col items-center min-w-[100px]">
                    <span class="text-[10px] font-bold uppercase">Maghrib</span>
                    <span class="text-lg font-extrabold">{pt['Maghrib']}</span>
                </div>
            </div>
        </section>

        <div class="space-y-4 pt-4">
            <h3 class="text-sm font-bold text-[#cbead7] tracking-wider uppercase">Spiritual Guidance</h3>
        </div>
    </main>
    """, unsafe_allow_html=True)

    # --- AI Chat Logic ---
    for m in st.session_state.messages[-3:]: # Show last 3 messages
        role_color = "#1f3a2d" if m["role"] == "assistant" else "#042015"
        st.markdown(f"""<div style="background:{role_color}; padding:20px; border-radius:15px; border: 1px solid rgba(242,202,80,0.1); margin: 0 24px 10px 24px;">{m['content']}</div>""", unsafe_allow_html=True)

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

# ==========================================
# 6. BOTTOM NAVIGATION (The Switcher)
# ==========================================
st.markdown("<div style='height: 80px;'></div>", unsafe_allow_html=True)
nav_cols = st.columns(4)
if nav_cols[0].button("🏠 Home", use_container_width=True): 
    st.session_state.app_mode = "Home"; st.rerun()
if nav_cols[1].button("📖 Quran", use_container_width=True): 
    st.session_state.app_mode = "Quran"; st.rerun()
if nav_cols[2].button("📜 Hadith", use_container_width=True): 
    st.session_state.app_mode = "Hadith"; st.rerun()
if nav_cols[3].button("🧭 Qibla", use_container_width=True): 
    st.session_state.app_mode = "Qibla"; st.rerun()
