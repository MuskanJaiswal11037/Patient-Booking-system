"""Google OAuth Sign In component - Frontend only implementation."""
from urllib.parse import urlencode

import streamlit as st

def render_google_signin_button():
    """
    Render Google Sign In using Streamlit's experimental user authentication.
    
    Examples
    --------
    >>> render_google_signin_button()
    """
    st.markdown("### Sign in with Google")
   
    if st.button("🔐 Sign in with Google"):
        st.login()
        st.rerun()

