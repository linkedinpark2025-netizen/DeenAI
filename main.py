import os
import requests
import re
import streamlit as st
import datetime
import io
from groq import Groq
from gtts import gTTS 
from streamlit_mic_recorder import mic_recorder
from datetime import datetime
from streamlit_js_eval import streamlit_js_eval

# Initialize session state
if 'messages' not in st.session_state:
st.session_state.messages = []
if 'v_list' not in st.session_state:
st.session_state.v_list = None
if 'user_city' not in st.session_state:
st.session_state.user_city = "London"
if 'trans_lang' not in st.session_state:
st.session_state.trans_lang = "131"
if 'app_mode' not in st.session_state:
st.session_state.app_mode = "Dashboard"
