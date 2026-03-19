import os, requests, re, streamlit as st, datetime, io
from groq import Groq

# ==========================================
# 1. INITIALIZATION & SESSION STATE
# ==========================================
if 'app_mode' not in st.session_state: st.session_state.app_mode = "Home"
if 'messages' not in st.session_state: st.session_state.messages = []
if 'user_city' not in st.session_state: st.session_state.user_city = "London"
if 'trans_lang' not in st.session_state: st.session_state.trans_lang = "131"
if 'tasbih_count' not in st.session_state: st.session_state.tasbih_count = 0

G_KEY = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
client = Groq(api_key=G_KEY) if G_KEY else None

# ==========================================
# 2. UTILITY FUNCTIONS
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
# 3. UI CONFIG & CSS
# ==========================================
st.set_page_config(page_title="The Digital Maqam", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<script src="https://cdn.tailwindcss.com?plugins=forms,container-queries"></script>
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;700;800&family=Inter:wght@400;600&family=Amiri:wght@400;700&display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
<style>
    [data-testid="stHeader"], [data-testid="stToolbar"], footer { display: none !important; }
    .stApp { background-color: #00180d; color: #cbead7; }
    .main .block-container { padding: 0; max-width: 100%; }
    .gold-gradient { background: linear-gradient(135deg, #f2ca50 0%, #d4af37 100%); }
    .arabic-font { font-family: 'Amiri', serif; text-align: right; }
    .no-scrollbar::-webkit-scrollbar { display: none; }
    /* Fix for button styling in Streamlit to match your UI */
    div.stButton > button {
        background-color: #142f23; color: #f2ca50; border: 1px solid rgba(242, 202, 80, 0.2);
        border-radius: 12px; transition: all 0.3s ease;
    }
    div.stButton > button:hover { border-color: #f2ca50; background-color: #1f3a2d; }
</style>
""", unsafe_allow_html=True)

# Shared Header
st.markdown(f"""
<header class="fixed top-0 w-full z-50 bg-[#00180d]/60 backdrop-blur-xl flex justify-between items-center px-6 h-16">
    <div class="flex items-center gap-3">
        <div class="w-8 h-8 rounded-full bg-[#d4af37] flex items-center justify-center text-[#3c2f00]"><span class="material-symbols-outlined text-sm">spa</span></div>
        <h1 class="text-xl font-bold tracking-[0.1em] text-[#f2ca50] uppercase font-['Plus_Jakarta_Sans']">The Digital Maqam</h1>
    </div>
</header>
""", unsafe_allow_html=True)

# ==========================================
# 4. ROUTING
# ==========================================

# --- HOME PAGE ---
if st.session_state.app_mode == "Home":
    pt = get_prayer_times(st.session_state.user_city) or {"Dhuhr": "--:--", "Asr": "--:--", "Maghrib": "--:--"}
    
    st.markdown(f"""
    <main class="pt-24 pb-10 px-6 max-w-2xl mx-auto space-y-10">
        <section>
            <p class="text-[#dac58d] tracking-widest uppercase text-xs mb-1">Assalamu Alaikum</p>
            <h2 class="text-4xl font-extrabold tracking-tight text-[#cbead7]">Digital Sanctuary</h2>
        </section>

        <div class="flex gap-3 overflow-x-auto pb-2 no-scrollbar">
            <div class="flex-shrink-0 gold-gradient text-[#3c2f00] px-6 py-4 rounded-lg flex flex-col items-center min-w-[100px]">
                <span class="text-[10px] font-bold uppercase">Dhuhr</span>
                <span class="text-lg font-extrabold">{pt.get('Dhuhr')}</span>
            </div>
            <div class="flex-shrink-0 bg-[#142f23] border border-[#4d4635] text-[#cbead7] px-6 py-4 rounded-lg flex flex-col items-center min-w-[100px]">
                <span class="text-[10px] font-bold uppercase">Asr</span>
                <span class="text-lg font-extrabold">{pt.get('Asr')}</span>
            </div>
            <div class="flex-shrink-0 bg-[#142f23] border border-[#4d4635] text-[#cbead7] px-6 py-4 rounded-lg flex flex-col items-center min-w-[100px]">
                <span class="text-[10px] font-bold uppercase">Maghrib</span>
                <span class="text-lg font-extrabold">{pt.get('Maghrib')}</span>
            </div>
        </div>

        <section class="grid grid-cols-2 gap-4">
            <div class="bg-[#142f23] p-6 rounded-lg border border-[#f2ca50]/10 flex flex-col justify-between h-40">
                <span class="material-symbols-outlined text-[#f2ca50] text-3xl">explore</span>
                <div>
                    <h4 class="text-[#cbead7] font-bold text-sm">Qibla</h4>
                    <p class="text-[#d0c5af] text-[10px]">Tap to find Mecca</p>
                </div>
            </div>
            <div class="bg-[#142f23] p-6 rounded-lg border border-[#f2ca50]/10 flex flex-col justify-between h-40">
                <div class="w-full flex justify-between items-start">
                    <span class="material-symbols-outlined text-[#f2ca50] text-3xl">history_edu</span>
                    <span class="text-[#f2ca50] text-[10px] font-bold">{st.session_state.tasbih_count}/33</span>
                </div>
                <div>
                    <h4 class="text-[#cbead7] font-bold text-sm">Daily Tasbih</h4>
                </div>
            </div>
        </section>
    </main>
    """, unsafe_allow_html=True)
    
    if st.button("📿 Click to Pray (Tasbih)", use_container_width=True):
        st.session_state.tasbih_count = (st.session_state.tasbih_count + 1) % 34
        st.rerun()

    # Chat logic
    prompt = st.chat_input("Ask Noor Spiritual Guide...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        if client:
            res = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": "You are Noor, a spiritual guide. Be poetic, kind, and use Quranic wisdom."}] + st.session_state.messages
            ).choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": res})
        st.rerun()

    for m in st.session_state.messages[-2:]:
        role = "Noor" if m["role"] == "assistant" else "You"
        st.info(f"**{role}:** {m['content']}")

# --- QURAN PAGE ---
elif st.session_state.app_mode == "Quran":
    st.markdown('<main class="pt-24 px-6 max-w-2xl mx-auto">', unsafe_allow_html=True)
    surah_num = st.number_input("Enter Surah Number", 1, 114, 1)
    verses = get_data(surah_num)
    for v in verses[:10]:
        st.markdown(f"""
        <div class="bg-[#042015] p-5 rounded-lg border-l-2 border-[#f2ca50] mb-4">
            <p class="arabic-font text-2xl text-[#f2ca50] mb-2">{v['text_uthmani']}</p>
            <p class="text-xs text-[#d0c5af]">{re.sub('<[^<]+?>', '', v['translations'][0]['text'])}</p>
        </div>
        """, unsafe_allow_html=True)
    st.markdown('</main>', unsafe_allow_html=True)

# --- HADITH PAGE ---
elif st.session_state.app_mode == "Hadith":
    st.markdown('<main class="pt-24 px-6 max-w-2xl mx-auto">', unsafe_allow_html=True)
    st.title("Hadith Library")
    h_query = st.text_input("Search Topics (e.g., Kindness, Patience)")
    if h_query and client:
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": f"Share a Sahih Hadith about {h_query}"}]
        ).choices[0].message.content
        st.write(res)
    st.markdown('</main>', unsafe_allow_html=True)

# ==========================================
# 5. FIXED BOTTOM NAV
# ==========================================
st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)
nav_cols = st.columns(4)
if nav_cols[0].button("🏠 Home"): st.session_state.app_mode = "Home"; st.rerun()
if nav_cols[1].button("📖 Quran"): st.session_state.app_mode = "Quran"; st.rerun()
if nav_cols[2].button("📜 Hadith"): st.session_state.app_mode = "Hadith"; st.rerun()
if nav_cols[3].button("🧭 Qibla"): st.session_state.app_mode = "Qibla"; st.rerun()
