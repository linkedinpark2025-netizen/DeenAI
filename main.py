import streamlit as st

st.title("DeenAI")

# Simple tabs
tab1, tab2, tab3 = st.tabs(["Home", "Quran", "Hadith"])

if tab1:
st.write("Dashboard content")

if tab2:
st.write("Quran reader")

if tab3:
st.write("Hadith search")
