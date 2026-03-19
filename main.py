import os, requests, re, streamlit as st, datetime, io
from groq import Groq

# 1. INITIALIZATION (Always first)
if 'user_city' not in st.session_state: st.session_state.user_city = "London"
if 'app_mode' not in st.session_state: st.session_state.app_mode = "Home"

# 2. DEFINE FUNCTIONS (This fixes the NameError)
def get_prayer_times(city_name):
    try:
        url = f"https://api.aladhan.com/v1/timingsByCity?city={city_name}&country="
        r = requests.get(url, timeout=10).json()
        return r['data']['timings'] if r['code'] == 200 else None
    except: 
        return None

def get_data(s_id, a_id=None):
    # ... (your existing get_data code here)
    return [] 

# 3. UI LOGIC (Only call functions down here)
if st.session_state.app_mode == "Home":
    # Now that the function is defined above, this line will work:
    pt = get_prayer_times(st.session_state.user_city) or {"Dhuhr": "--:--", "Asr": "--:--", "Maghrib": "--:--"}
    
    # ... (Rest of your HTML rendering code)
    st.markdown(f"""
        <div class="grid grid-cols-3 gap-3">
            <div class="gold-gradient text-[#3c2f00] p-4 rounded-lg text-center">
                <p class="text-[10px] font-bold">Dhuhr</p>
                <p class="text-lg font-extrabold">{pt['Dhuhr']}</p>
            </div>
            </div>
    """, unsafe_allow_html=True)
