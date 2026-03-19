# --- 1. GET DYNAMIC DATA ---
# Prayer times for your city
pt = get_prayer_times(st.session_state.user_city) or {"Dhuhr": "--:--", "Asr": "--:--", "Maghrib": "--:--"}

# Verse of the Day logic
day_of_year = datetime.now().timetuple().tm_yday
rotation_keys = ["2:153", "3:139", "94:5", "2:186", "8:30", "29:69", "39:53", "48:4", "55:13", "65:3"]
todays_key = rotation_keys[day_of_year % len(rotation_keys)]
s_id, a_id = todays_key.split(':')
dv_list = get_data(s_id, a_id)

if dv_list and dv_list[0]:
    dv = dv_list[0]
    text_ar = dv.get('text_uthmani', 'Arabic text unavailable')
    trans_text = re.sub('<[^<]+?>', '', dv.get('translations', [{}])[0].get('text', ''))
else:
    text_ar, trans_text = "Loading...", "Connecting to Sanctuary..."

# --- 2. RENDER UI ---
st.markdown(f"""
<main class="pt-24 px-6 max-w-2xl mx-auto space-y-10">
    <section>
        <p class="text-[#dac58d] tracking-widest uppercase text-xs mb-1">Assalamu Alaikum</p>
        <h2 class="text-4xl font-extrabold tracking-tight text-[#cbead7]">Digital Sanctuary</h2>
    </section>
    
    <section class="relative bg-[#042015] border border-[#f2ca50]/20 rounded-lg p-8 overflow-hidden">
        <div class="space-y-6">
            <div class="flex justify-between items-center">
                <span class="bg-[#f2ca50]/10 text-[#f2ca50] px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider">Verse of the Day</span>
                <span class="text-[#d0c5af] text-xs">Surah {todays_key}</span>
            </div>
            <p class="arabic-font text-right text-3xl leading-[1.8] text-[#f2ca50]" dir="rtl">
                {text_ar}
            </p>
            <p class="text-[#d0c5af] italic text-sm leading-relaxed">
                "{trans_text}"
            </p>
        </div>
    </section>

    <div class="flex justify-between items-end">
        <h3 class="text-sm font-bold text-[#cbead7] tracking-wider uppercase">Prayer Times</h3>
        <span class="text-[10px] text-[#d0c5af] uppercase">{st.session_state.user_city} • {datetime.now().strftime('%H:%M')}</span>
    </div>
    
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
