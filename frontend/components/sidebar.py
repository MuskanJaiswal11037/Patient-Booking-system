"""Sidebar navigation component."""
import streamlit as st
from components.utils import is_logged_in, logout, reset_chat_history, get_state_manager
from components.config import ROLE_NAVIGATION
from components.api import is_registered


def render_sidebar():
    """Render sidebar with navigation and user info."""
    with st.sidebar:
        st.markdown("## 🏥 MedApp - Test Mode")
        
        page = get_state_manager().get('current_page')
        if is_logged_in():
            if not is_registered():
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📝 Register", use_container_width=True):
                        page = "📝 Register"
                with col2:
                    if st.button("🚪 Logout", use_container_width=True):
                        logout()
                        st.rerun()
            else:
                # User info section
                state = get_state_manager()
                st.success(f"👤 **{state.get('full_name')}**")        
                # Action buttons
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 Reset Chat", use_container_width=True):
                        reset_chat_history()
                        st.rerun()
                with col2:
                    if st.button("🚪 Logout", use_container_width=True):
                        logout()
                        st.rerun()
                
                st.divider()
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💬 Book via Chat", use_container_width=True):
                        page = "💬 Book via Chat"
                with col2:
                    if st.button("Live Queue Status 📊", use_container_width=True):
                        page = "Live Queue Status 📊"

        else:
                # Not logged in - show login/register options
                st.markdown("### 🔐 Authentication")
                [col1] = st.columns(1)
                with col1:
                    if st.button("🔑 Login", use_container_width=True):
                        page = "🔑 Login"
                
                if not page:    
                    st.info("👈 Please login or register to get started")
        get_state_manager().set('current_page', page)  # Store current page in state for access in sidebar
