import os, requests, re, streamlit as st, datetime, io
from groq import Groq

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
# 2. UTILITY FUNCTIONS (Defined before use)
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
# 3. PAGE CONFIG & STYLES
# ==========================================
st.set_page_config(page_title="The Digital Maqam", layout="wide")

st.markdown("""
<script src="https://cdn.tailwindcss.com"></script>
<link href="https://fonts.googleapis.com/css2?family=Amiri&display=swap" rel="stylesheet"/>
<style>
    [data-testid="stHeader"], [data-testid="stToolbar"], footer { display: none !important; }
    .stApp { background-color: #00180d; color: #cbead7; }
    .gold-gradient { background: linear-gradient(135deg, #f2ca50 0%, #d4af37 100%); }
    .arabic-font { font-family: 'Amiri', serif; }
    .no-scrollbar::-webkit-scrollbar { display: none; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. MAIN UI LOGIC
# ==========================================
if st.session_state.app_mode == "Home":
    # Data Fetching
    pt = get_prayer_times(st.session_state.user_city) or {"Dhuhr": "--:--", "Asr": "--:--", "Maghrib": "--:--"}
    
    # Verse of the Day Logic
    day_of_year = datetime.date.today().timetuple().tm_yday
    rotation_keys = ["2:255", "2:153", "3:139", "94:5", "2:186"]
    todays_key = rotation_keys[day_of_year % len(rotation_keys)]
    s_id, a_id = todays_key.split(':')
    dv_list = get_data(s_id, a_id)
    
    text_ar = dv_list[0].get('text_uthmani', '') if dv_list else "Loading..."
    trans_text = re.sub('<[^<]+?>', '', dv_list[0].get('translations', [{}])[0].get('text', '')) if dv_list else "Connecting..."

    # Render Dashboard
    st.markdown(f"""
    <main class="pt-10 px-6 max-w-2xl mx-auto space-y-8">
        <section class="relative bg-[#042015] border border-[#f2ca50]/20 rounded-lg p-8 overflow-hidden">
            <div class="space-y-6">
                <div class="flex justify-between items-center">
                    <span class="bg-[#f2ca50]/10 text-[#f2ca50] px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider">Verse of the Day</span>
                    <span class="text-[#d0c5af] text-xs">Surah {todays_key}</span>
                </div>
                <p class="arabic-font text-right text-3xl leading-[1.8] text-[#f2ca50]" dir="rtl">{text_ar}</p>
                <p class="text-[#d0c5af] italic text-sm leading-relaxed">"{trans_text}"</p>
            </div>
        </section>

        <h3 class="text-sm font-bold text-[#cbead7] tracking-wider uppercase">Prayer Times</h3>
        <div class="grid grid-cols-3 gap-3">
            <div class="gold-gradient text-[#3c2f00] p-4 rounded-lg text-center shadow-lg">
                <p class="text-[10px] font-bold uppercase">Dhuhr</p>
                <p class="text-lg font-extrabold">{pt['Dhuhr']}</p>
            </div>
            <div class="bg-[#142f23] p-4 rounded-lg text-center border border-[#4d4635]">
                <p class="text-[10px] font-bold uppercase">Asr</p>
                <p class="text-lg font-extrabold">{pt['Asr']}</p>
            </div>
            <div class="bg-[#142f23] p-4 rounded-lg text-center border border-[#4d4635]">
                <p class="text-[10px] font-bold uppercase">Maghrib</p>
                <p class="text-lg font-extrabold">{pt['Maghrib']}</p>
            </div>
        </div>
    </main>
    """, unsafe_allow_html=True)

# Navigation (Simple)
st.sidebar.title("Navigation")
if st.sidebar.button("Home"): st.session_state.app_mode = "Home"; st.rerun()
