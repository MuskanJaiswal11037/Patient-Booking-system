# frontend/streamlit_app.py
"""
Main Streamlit app - Orchestrates all components.
Modular architecture with separate components for:
  - Authentication (login/register)
  - Navigation (sidebar)
  - API communication
  - Page components (chat, appointments, feedback, schedule)
"""
import os

import streamlit as st
from dotenv import load_dotenv
# Import components
from components.config import PAGE_TITLE, PAGE_ICON, LAYOUT, INITIAL_SIDEBAR_STATE
from components.utils import get_state_manager, init_session_state, init_user, is_logged_in
from components.sidebar import render_sidebar
from components.page_factory import render_page

# ── Global Theme (dark) ─────────────────────────────────────────
# This CSS is injected once for the whole app.
_GLOBAL_DARK_CSS = r"""
<style>
body, .stApp {
    background-color: #0f1115 !important;
    color: #e6e6e6 !important;
}

.stMainBlockContainer, .main .block-container {
    background-color: #0f1115 !important;
}

/* Sidebar */
.stSidebar {
    background-color: #0b0d12 !important;
    border-right: 1px solid rgba(255,255,255,0.10) !important;
}
.stSidebar > div {
    background-color: #0b0d12 !important;
}
.stSidebar [data-testid="stSidebarContent"] {
    background-color: #0b0d12 !important;
}
.stSidebar * {
    color: #e6e6e6 !important;
}
.stSidebar hr {
    border-top: 1px solid rgba(255,255,255,0.14) !important;
}
.stSidebar .stButton > button {
    background-color: rgba(102, 126, 234, 0.18) !important;
    color: #e6e6e6 !important;
    border: 1px solid rgba(102, 126, 234, 0.45) !important;
}
.stSidebar .stButton > button:hover {
    background-color: rgba(102, 126, 234, 0.28) !important;
}

/* Chat */
.stChatMessage {
    background-color: #171a22 !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    border-radius: 10px !important;
    padding: 0.75rem 1rem !important;
}
.stChatMessage[data-testid="stChatMessage"],
div[data-testid="stChatMessage"] {
    background-color: #171a22 !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    border-radius: 10px !important;
}
.stChatMessage .stMarkdown, 
.stChatMessage .stText, 
.stChatMessage p {
    color: #e6e6e6 !important;
}
.stChatInput, .stChatInput > div, .stChatInput textarea, .stChatInput input {
    background-color: #0c0e13 !important;
    color: #e6e6e6 !important;
    border-color: rgba(255,255,255,0.12) !important;
}
.stChatInput {
    background-color:#0c0e13 !important;
    padding: 0 !important;
    margin: 0 !important;
}
.stChatInput > div {
    background-color: #0c0e13 !important;
    padding: 0 !important;
    margin: 0 !important;
}
.stChatInput [role="textbox"], .stChatInput [contenteditable="true"] {
    background-color: #0c0e13 !important;
}
.stChatInput [data-testid="stChatInputTextarea"],
textarea[data-testid="stChatInputTextarea"] {
    background-color: #0c0e13 !important;
    color: #e6e6e6 !important;
}
.stChatInput textarea {
    border: 1px solid rgba(255,255,255,0.12) !important;
    margin: 0 !important;
}

/* Navbar-ish text (sidebar titles) */
.stSidebar h1, .stSidebar h2, .stSidebar h3, .stSidebar .stTitle {
    color: #e6e6e6 !important;
}

/* Cards / containers */
.stMetric {
    color: #ffffff !important;
    border-color: rgba(255,255,255,0.12) !important;
}
.queue-card {
    background: #171a22 !important;
    border-left: 4px solid #667eea !important;
}

/* Text blocks */
.stMarkdown, .stText, .stTitle, .stSubheader, .stHeader, .stCaption, .stLabel {
    color: #e6e6e6 !important;
}

/* Buttons */
.stButton > button {
    background-color: #1f77b4 !important;
    color: white !important;
    border: 1px solid #1f77b4 !important;
    border-radius: 5px !important;
    padding: 0.5rem 1rem !important;
    font-weight: 600 !important;
}
.stButton > button:hover {
    background-color: #1557a0 !important;
    border-color: #1557a0 !important;
}
/* Form Submit Buttons */
.stFormSubmitButton > button {
    background-color: #28a745 !important;
    color: white !important;
    border: 1px solid #28a745 !important;
    border-radius: 5px !important;
    padding: 0.5rem 1rem !important;
    font-weight: 600 !important;
}
.stFormSubmitButton > button:hover {
    background-color: #218838 !important;
    border-color: #218838 !important;
}

/* Inputs */
input, textarea, select {
    background-color: #0c0e13 !important;
    color: #e6e6e6 !important;
}

/* Streamlit form elements */
.stTextInput input, .stTextArea textarea, .stSelectbox [role="combobox"] {
    background-color: #0c0e13 !important;
    color: #e6e6e6 !important;
}

/* Expander */
.stExpander > section {
    background-color: #171a22 !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
}

/* Specific Streamlit container (fix remaining light areas) */
div.st-emotion-cache-128upt6.eht7o1d3 {
    background-color: #0f1115 !important;
}

/* App Header */
.stAppHeader {
    background-color: #0f1115 !important;
}

/* Dividers */
hr {
    border-top: 1px solid rgba(255,255,255,0.14) !important;
}
</style>
"""

# ── Page Configuration ───────────────────────────────────────────
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT,
    initial_sidebar_state=INITIAL_SIDEBAR_STATE,
)

# Apply global theme
st.markdown(_GLOBAL_DARK_CSS, unsafe_allow_html=True)

# ── Initialize Session State ────────────────────────────────────
init_session_state()

# ── User Authentication Check ─────────────────────────────────
init_user()

# ── Render Sidebar & Get Current Page ───────────────────────────
render_sidebar()

# ═══════════════════════════════════════════════════════════════
#  MAIN PAGE ROUTING USING FACTORY PATTERN
# ═══════════════════════════════════════════════════════════════

# Get the current page from session state (set by sidebar navigation)
page = get_state_manager().get('current_page')

# Try to render the selected page
if page:
    page_rendered = render_page(page)
    
    # If page wasn't rendered (access denied or not found)
    if not page_rendered:
        if is_logged_in():
            st.error(f"❌ Access denied to page: {page}")
        else:
            st.info("👈 Please login or register to get started.")
else:
    # No page selected (not logged in)
    st.info("👈 If loggged in then please navigate to book via chat or view queue real-time status; otherwise register/login to get started.")
    
    