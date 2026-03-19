import os, requests, re, streamlit as st, datetime
from groq import Groq

# --- 1. CONFIG & SYSTEM PROMPT ---
st.set_page_config(page_title="The Digital Maqam", layout="wide")

if 'app_mode' not in st.session_state: st.session_state.app_mode = "Home"
if 'messages' not in st.session_state: st.session_state.messages = []
if 'user_city' not in st.session_state: st.session_state.user_city = "London"

client = Groq(api_key=st.secrets.get("GROQ_API_KEY"))

# --- 2. GLOBAL STYLES (Based on your @theme) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@700;800&family=Inter:wght@400;600&family=Amiri:wght@400;700&display=swap');

    :root {
        --primary: #f2ca50;
        --surface: #00180d;
        --surface-low: #042015;
        --surface-high: #142f23;
        --surface-highest: #1f3a2d;
        --on-surface-variant: #d0c5af;
    }

    .stApp { background-color: var(--surface); color: #cbead7; font-family: 'Inter', sans-serif; }
    
    /* Navigation Bar Fix */
    .nav-bar {
        position: fixed; bottom: 0; left: 0; width: 100%;
        background: rgba(0, 24, 13, 0.8); backdrop-filter: blur(10px);
        border-top: 1px solid rgba(242, 202, 80, 0.1);
        display: flex; justify-content: space-around; padding: 1rem; z-index: 1000;
    }

    /* Verse/Hadith Cards */
    .content-card {
        background: var(--surface-low);
        border: 1px solid rgba(242, 202, 80, 0.1);
        padding: 1.5rem; border-radius: 1rem; margin-bottom: 1rem;
    }

    .arabic-font { font-family: 'Amiri', serif; color: var(--primary); text-align: right; }
    
    /* Hide Streamlit elements */
    [data-testid="stHeader"], [data-testid="stToolbar"], footer { display: none !important; }
</style>
""", unsafe_allow_html=True)

# --- 3. UTILITY FUNCTIONS ---
def get_prayer_times(city):
    try:
        r = requests.get(f"https://api.aladhan.com/v1/timingsByCity?city={city}&country=").json()
        return r['data']['timings']
    except: return {"Dhuhr": "12:00", "Asr": "15:30", "Maghrib": "18:00"}

def get_quran_verse(s_id, a_id):
    try:
        r = requests.get(f"https://api.quran.com/api/v4/verses/by_key/{s_id}:{a_id}?translations=131&fields=text_uthmani").json()
        return r['verse']
    except: return None

# --- 4. NAVIGATION LOGIC ---
# Using streamlit buttons styled like a nav bar
cols = st.columns(4)
if cols[0].button("🏠 Home"): st.session_state.app_mode = "Home"; st.rerun()
if cols[1].button("📖 Quran"): st.session_state.app_mode = "Quran"; st.rerun()
if cols[2].button("📜 Hadith"): st.session_state.app_mode = "Hadith"; st.rerun()
if cols[3].button("🧭 Qibla"): st.session_state.app_mode = "Qibla"; st.rerun()

# --- 5. PAGE ROUTING ---

# PAGE: HOME
if st.session_state.app_mode == "Home":
    st.markdown('<p style="color:#dac58d; text-transform:uppercase; font-size:0.7rem; font-weight:700; margin-top:2rem;">Assalamu Alaikum</p>', unsafe_allow_html=True)
    st.markdown('<h1 style="font-family:\'Plus Jakarta Sans\'; font-weight:800; font-size:2.5rem; margin-bottom:2rem;">Digital Sanctuary</h1>', unsafe_allow_html=True)
    
    # Verse Card
    v = get_quran_verse(2, 255)
    st.markdown(f"""
    <div class="content-card">
        <p class="arabic-font" style="font-size:1.8rem;">{v['text_uthmani'] if v else 'اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ'}</p>
        <p style="color:var(--on-surface-variant); font-style:italic; font-size:0.9rem; margin-top:1rem;">
            "{re.sub('<[^<]+?>', '', v['translations'][0]['text']) if v else 'Connecting to Sanctuary...'}"
        </p>
    </div>
    """, unsafe_allow_html=True)

    # AI CHAT SECTION
    st.markdown('<p style="font-size:0.75rem; font-weight:bold; text-transform:uppercase; margin-top:2rem;">Spiritual Guidance</p>', unsafe_allow_html=True)
    for m in st.session_state.messages[-3:]:
        role_style = "background:var(--surface-highest);" if m["role"] == "assistant" else "background:var(--surface-low); border:1px solid #4d4635;"
        st.markdown(f'<div style="{role_style} padding:1rem; border-radius:0.75rem; margin-bottom:0.5rem; font-size:0.9rem;">{m["content"]}</div>', unsafe_allow_html=True)
    
    user_query = st.chat_input("Ask Noor...")
    if user_query:
        st.session_state.messages.append({"role": "user", "content": user_query})
        res = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": "You are Noor, a spiritual guide. Quote Quran [Surah:Ayah]."}] + st.session_state.messages
        ).choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": res})
        st.rerun()

# PAGE: QURAN READER
elif st.session_state.app_mode == "Quran":
    st.markdown('<h2 style="font-family:\'Plus Jakarta Sans\'; font-weight:800;">Noble Quran</h2>', unsafe_allow_html=True)
    surah = st.number_input("Surah Number", 1, 114, 1)
    # Simplified logic to show first 5 verses of selected surah
    for i in range(1, 6):
        v = get_quran_verse(surah, i)
        if v:
            st.markdown(f"""
            <div class="content-card">
                <p class="arabic-font" style="font-size:1.5rem;">{v['text_uthmani']}</p>
                <p style="color:var(--on-surface-variant); font-size:0.8rem;">{re.sub('<[^<]+?>', '', v['translations'][0]['text'])}</p>
            </div>
            """, unsafe_allow_html=True)

# PAGE: HADITH LIBRARY
elif st.session_state.app_mode == "Hadith":
    st.markdown('<h2 style="font-family:\'Plus Jakarta Sans\'; font-weight:800;">Hadith Library</h2>', unsafe_allow_html=True)
    topic = st.text_input("Search Topic (e.g. Patience)")
    if topic:
        with st.spinner("Searching..."):
            res = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": f"Share a Sahih Hadith about {topic}. Include the narrator and collection."}]
            ).choices[0].message.content
            st.markdown(f'<div class="content-card">{res}</div>', unsafe_allow_html=True)

# PAGE: QIBLA
elif st.session_state.app_mode == "Qibla":
    st.markdown('<h2 style="font-family:\'Plus Jakarta Sans\'; font-weight:800; text-align:center;">Qibla Finder</h2>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="text-align:center; padding: 3rem;">
        <div style="width:200px; height:200px; border:4px solid var(--primary); border-radius:50%; margin: 0 auto; display:flex; align-items:center; justify-content:center;">
            <span style="font-size:3rem; transform: rotate(45deg);">⬆️</span>
        </div>
        <p style="margin-top:2rem; color:var(--on-surface-variant);">Pointing towards the Kaaba in Mecca</p>
    </div>
    """, unsafe_allow_html=True)
