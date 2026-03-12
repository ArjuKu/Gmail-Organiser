import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="Gmail Organiser", page_icon="📧", layout="wide")

# Simple dark CSS
st.markdown("""
<style>
    .stApp { background-color: #050505; }
    .main-header { font-family: sans-serif; font-size: 4rem; color: #FF6B35; text-align: center; margin: 1rem 0; font-weight: bold; }
    .subtitle { color: #888; text-align: center; margin-bottom: 2rem; }
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">Gmail Organiser</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">AI-Powered Inbox Management</p>', unsafe_allow_html=True)

st.write("App loaded successfully!")

# Checkbox to test
test_btn = st.button("Test Button")
if test_btn:
    st.write("Button works!")

# Metrics
c1, c2, c3, c4 = st.columns(4)
c1.metric("Emails", "0")
c2.metric("Senders", "0")
c3.metric("Labeled", "0")
c4.metric("Trashed", "0")
