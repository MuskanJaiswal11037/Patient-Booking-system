# frontend/streamlit_app.py
"""
Main Streamlit app - Orchestrates all components.
Modular architecture with separate components for:
  - Authentication (login/register)
  - Navigation (sidebar)
  - API communication
  - Page components (chat, appointments, feedback, schedule)
"""
import streamlit as st

# Import components
from components.config import PAGE_TITLE, PAGE_ICON, LAYOUT, INITIAL_SIDEBAR_STATE
from components.utils import get_state_manager, init_session_state, init_user, is_logged_in
from components.sidebar import render_sidebar
from components.page_factory import render_page

# ── Page Configuration ───────────────────────────────────────────
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT,
    initial_sidebar_state=INITIAL_SIDEBAR_STATE,
)

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
    st.info("👈 Please login or register to get started.")