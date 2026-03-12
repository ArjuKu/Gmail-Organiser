import streamlit as st
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="Gmail Organiser", page_icon="📧", layout="wide")

# Session state
if 'scan_stats' not in st.session_state:
    st.session_state.scan_stats = {'messages': 0, 'senders': 0}
if 'apply_stats' not in st.session_state:
    st.session_state.apply_stats = {'labeled': 0, 'trashed': 0}
if 'status_message' not in st.session_state:
    st.session_state.status_message = ""
if 'glow_cards' not in st.session_state:
    st.session_state.glow_cards = []

# Dark Mode CSS with visible orange gradient & glow
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Onest:wght@700;900&family=Outfit:wght@400;500;600&display=swap');
    * { font-family: 'Outfit', sans-serif; }
    
    /* Visible orange gradient background with ambient glow */
    .stApp {
        background: linear-gradient(180deg, #1a0a00 0%, #0d0502 40%, #050505 100%);
        min-height: 100vh;
        position: relative;
    }
    
    /* Ambient glow behind main content */
    .stApp::before {
        content: '';
        position: fixed;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle at 50% 0%, rgba(255, 107, 53, 0.08) 0%, transparent 50%);
        pointer-events: none;
        z-index: 0;
    }
    
    [data-testid="stSidebar"] { background-color: #0E0E0E !important; border-right: 1px solid rgba(255,107,53,0.15) !important; position: relative; z-index: 1; }
    .sidebar p, .sidebar li { color: #CCC !important; font-size: 0.9rem; }
    .sidebar b { color: #FFF !important; }
    h1, h2, h3 { font-family: 'Onest', sans-serif !important; }
    
    .main-header { 
        font-family: 'Onest', sans-serif !important; 
        font-size: 5rem !important; 
        font-weight: 900; 
        background: linear-gradient(135deg, #FF6B35, #D62828); 
        -webkit-background-clip: text; 
        -webkit-text-fill-color: transparent; 
        text-align: center; 
        margin: 0.3rem 0; 
        position: relative;
        z-index: 1;
    }
    
    .subtitle { color: #888; text-align: center; margin-bottom: 1.5rem; font-weight: 500; letter-spacing: 0.1em; position: relative; z-index: 1; }
    .stButton>button { border-radius: 50px !important; font-weight: 600 !important; padding: 0.5rem 2rem !important; position: relative; z-index: 1; }
    div[data-testid="stButton"] button[kind="primary"] { background: linear-gradient(135deg, #FF6B35, #D62828) !important; border: none !important; color: white !important; box-shadow: 0 4px 15px rgba(214,40,40,0.2); }
    
    .metric-card { 
        background: rgba(255,107,53,0.08); 
        border: 1px solid rgba(255,107,53,0.3); 
        border-radius: 12px; 
        padding: 1rem; 
        text-align: center; 
        transition: all 0.3s ease;
        position: relative;
        z-index: 1;
    }
    
    .metric-value { font-size: 2.2rem; font-weight: 700; background: linear-gradient(135deg, #FF6B35, #D62828); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .metric-label { color: #888; font-size: 0.75rem; text-transform: uppercase; margin-top: 0.2rem; font-weight: 600; }
    
    /* Glow animation */
    @keyframes glow-pulse {
        0% { box-shadow: 0 0 0 0 rgba(255, 107, 53, 0); border-color: rgba(255, 107, 53, 0.3); }
        50% { box-shadow: 0 0 20px 5px rgba(255, 107, 53, 0.4); border-color: rgba(255, 107, 53, 0.8); }
        100% { box-shadow: 0 0 0 0 rgba(255, 107, 53, 0); border-color: rgba(255, 107, 53, 0.3); }
    }
    .metric-card.glow { animation: glow-pulse 2s ease-in-out; border-color: #FF6B35 !important; }
    
    .status-box { padding: 0.8rem; border-radius: 10px; margin: 1rem 0; position: relative; z-index: 1; }
    .status-success { background: rgba(34,197,94,0.1); border: 1px solid rgba(34,197,94,0.2); color: #4ADE80; }
    .status-error { background: rgba(214,40,40,0.1); border: 1px solid rgba(214,40,40,0.2); color: #F87171; }
    
    /* Checkbox captions */
    .stCheckbox + p, .stCheckbox + div { color: #888 !important; font-size: 0.75rem !important; margin-top: -0.5rem !important; }
    
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">Gmail Organiser</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">AI-Powered Inbox Management</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    with st.expander("Features", expanded=False):
        st.markdown('<div class="sidebar"><ul><li><b>AI Classification</b></li><li>Incremental Scanning</li><li>Lifetime Counter</li></ul></div>', unsafe_allow_html=True)
    with st.expander("Safety", expanded=False):
        st.markdown('<div class="sidebar"><ul><li>Starred Protected</li><li>Primary Safe</li></ul></div>', unsafe_allow_html=True)
    with st.expander("Instructions", expanded=False):
        st.markdown('<div class="sidebar"><ul><li>Click <b>Scan Inbox</b></li><li>Review Sheet</li><li>Click <b>Apply</b></li></ul></div>', unsafe_allow_html=True)
    st.markdown("---")
    force_scan = st.checkbox("Force Full Scan", value=False)
    st.caption("Scan ALL emails, not just new ones")
    
    clean_labels = st.checkbox("Clean AO Labels", value=False)
    st.caption("Delete existing labels before scanning")

# Metrics with glow
def m(v, l, key):
    glow = "glow" if key in st.session_state.glow_cards else ""
    return f'<div class="metric-card {glow}"><div class="metric-value">{v}</div><div class="metric-label">{l}</div></div>'

c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown(m(st.session_state.scan_stats['messages'], "Emails", "emails"), unsafe_allow_html=True)
with c2: st.markdown(m(st.session_state.scan_stats['senders'], "Senders", "senders"), unsafe_allow_html=True)
with c3: st.markdown(m(st.session_state.apply_stats['labeled'], "Labeled", "labeled"), unsafe_allow_html=True)
with c4: st.markdown(m(st.session_state.apply_stats['trashed'], "Trashed", "trashed"), unsafe_allow_html=True)

st.markdown('<div style="margin:1rem 0"></div>', unsafe_allow_html=True)

# Controls
b1, b2 = st.columns(2)
scan_btn = b1.button("Scan Inbox", type="primary", use_container_width=True)
apply_btn = b2.button("Apply Decisions", use_container_width=True)

# Progress
pbar = st.progress(0)
status = st.empty()

if scan_btn:
    st.session_state.status_message = ""
    st.session_state.glow_cards = []
    status.markdown("Scanning inbox...", unsafe_allow_html=True)
    pbar.progress(10)
    
    try:
        from core.scan_senders import run_scan_senders
        result = run_scan_senders(force_full_scan=force_scan, clean_old_labels=clean_labels, progress_callback=lambda p, m: pbar.progress(min(p, 100)))
        pbar.progress(100)
        if result and result.get('success'):
            st.session_state.scan_stats = {'messages': result.get('messages', 0), 'senders': result.get('senders', 0)}
            st.session_state.status_message = f"Complete! Found {result.get('messages')} emails."
            st.session_state.glow_cards = ["emails", "senders"]
            st.rerun()
    except Exception as e:
        st.session_state.status_message = f"Error: {str(e)}"

if apply_btn:
    st.session_state.status_message = ""
    st.session_state.glow_cards = []
    status.markdown("Applying decisions...", unsafe_allow_html=True)
    pbar.progress(10)
    
    try:
        from core.apply_senders import run_apply_senders
        result = run_apply_senders(progress_callback=lambda p, m: pbar.progress(min(p, 100)))
        pbar.progress(100)
        if result:
            st.session_state.apply_stats['labeled'] += result.get('labeled', 0)
            st.session_state.apply_stats['trashed'] += result.get('trashed', 0)
            st.session_state.status_message = f"Applied! {result.get('labeled')} labeled, {result.get('trashed')} trashed."
            st.session_state.glow_cards = ["labeled", "trashed"]
            st.rerun()
    except Exception as e:
        st.session_state.status_message = f"Error: {str(e)}"

if st.session_state.status_message:
    cls = "status-success" if "Complete" in st.session_state.status_message or "Applied" in st.session_state.status_message else "status-error"
    st.markdown(f'<div class="status-box {cls}">{st.session_state.status_message}</div>', unsafe_allow_html=True)
