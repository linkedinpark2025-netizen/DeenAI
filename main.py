import os, requests, re, streamlit as st, datetime
from groq import Groq

# --- 1. CONFIG & STYLE (Your CSS Theme) ---
st.set_page_config(page_title="The Digital Maqam", layout="wide")

# This block translates your @theme CSS into the Streamlit app
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@700;800&family=Inter:wght@400;600&family=Amiri:wght@400;700&display=swap');

    /* Variables from your @theme */
    :root {
        --primary: #f2ca50;
        --surface: #00180d;
        --surface-container-low: #042015;
        --surface-container-high: #142f23;
        --on-surface-variant: #d0c5af;
        --secondary: #dac58d;
    }

    .stApp { 
        background-color: var(--surface); 
        color: #cbead7; 
        font-family: 'Inter', sans-serif; 
    }

    /* Verse Card - surface-container-low */
    .verse-card {
        background-color: var(--surface-container-low);
        border: 1px solid rgba(242, 202, 80, 0.1);
        padding: 2rem;
        border-radius: 1rem;
        margin-bottom: 2rem;
    }

    .arabic-font { 
        font-family: 'Amiri', serif; 
        color: var(--primary);
        font-size: 2rem;
        line-height: 1.8;
        text-align: right;
    }

    /* Prayer Pills - surface-container-high */
    .prayer-pill {
        background-color: var(--surface-container-high);
        border: 1px solid #4d4635;
        padding: 1rem;
        border-radius: 0.75rem;
        text-align: center;
        min-width: 100px;
    }

    .gold-gradient {
        background: linear-gradient(135deg, #f2ca50 0%, #d4af37 100%);
        color: #3c2f00;
    }

    /* Hide Streamlit clutter */
    [data-testid="stHeader"], footer { display: none !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. LAYOUT CONSTRUCTION (The "App.tsx" structure) ---

# Top Header
st.markdown(f"""
<div style="padding: 1rem 0; margin-bottom: 2rem;">
    <p style="color:var(--secondary); text-transform:uppercase; letter-spacing:0.2em; font-size:0.7rem; font-weight:700;">Assalamu Alaikum</p>
    <h1 style="font-family:'Plus Jakarta Sans'; font-weight:800; font-size:2.5rem; color:#cbead7; letter-spacing:-0.02em;">Digital Sanctuary</h1>
</div>
""", unsafe_allow_html=True)

# Main Verse Card
st.markdown(f"""
<div class="verse-card">
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1.5rem;">
        <span style="background:rgba(242,202,80,0.1); color:var(--primary); padding:4px 12px; border-radius:99px; font-size:0.6rem; font-weight:bold; letter-spacing:0.1em;">VERSE OF THE DAY</span>
        <span style="color:var(--on-surface-variant); font-size:0.7rem;">Surah Al-Baqarah 2:255</span>
    </div>
    <p class="arabic-font" dir="rtl">اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ</p>
    <p style="color:var(--on-surface-variant); font-style:italic; font-size:0.9rem; margin-top:1.5rem; line-height:1.6;">
        "Allah! There is no god but He, the Living, the Self-subsisting..."
    </p>
</div>
""", unsafe_allow_html=True)

# Prayer Times Grid
st.markdown('<p style="font-size:0.75rem; font-weight:bold; color:#cbead7; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:1rem;">Prayer Times</p>', unsafe_allow_html=True)

# Using a Flex Container for the Horizontal Scroll look
st.markdown(f"""
<div style="display: flex; gap: 0.75rem; overflow-x: auto; padding-bottom: 1rem;">
    <div class="prayer-pill gold-gradient">
        <p style="font-size:0.6rem; font-weight:bold; text-transform:uppercase; margin:0;">Dhuhr</p>
        <p style="font-size:1.1rem; font-weight:800; margin:0;">12:58</p>
    </div>
    <div class="prayer-pill">
        <p style="font-size:0.6rem; font-weight:bold; text-transform:uppercase; margin:0; color:var(--on-surface-variant);">Asr</p>
        <p style="font-size:1.1rem; font-weight:800; margin:0;">15:22</p>
    </div>
    <div class="prayer-pill">
        <p style="font-size:0.6rem; font-weight:bold; text-transform:uppercase; margin:0; color:var(--on-surface-variant);">Maghrib</p>
        <p style="font-size:1.1rem; font-weight:800; margin:0;">18:05</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Chat Input Placeholder (Styling the Groq input)
st.markdown('<div style="margin-top:3rem;"></div>', unsafe_allow_html=True)
st.markdown('<p style="font-size:0.75rem; font-weight:bold; color:#cbead7; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:1rem;">Spiritual Guidance</p>', unsafe_allow_html=True)

# Your Groq logic would follow here...
prompt = st.chat_input("Ask Noor...")
