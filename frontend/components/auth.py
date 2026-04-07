"""Authentication components (login and register forms)."""
import streamlit as st
import re
from components.api import login, register
from components.utils import set_user, get_state_manager, validate_mobile_number
from components.config import BLOOD_GROUPS
from components.google_signin import render_google_signin_button
import os
from dotenv import load_dotenv

def render_login_page():
    """Render login form."""
    st.title("🔑 Login")
    
    col, _ = st.columns([1.2, 1])
    with col:

        # Google Sign In Button
        render_google_signin_button()            
        st.divider()
        

def render_register_page():
    """Render registration form."""
    st.title("📝 Create Account")

    col, _ = st.columns([1.2, 1])
    with col:
        with st.form("reg_form", border=True):
            full_name = st.text_input("Full Name", value=get_state_manager().get('full_name'), disabled=True)
            email = st.text_input("Email", value=get_state_manager().get('user_email'), disabled=True)
            phone = st.text_input("Phone (optional)")
            dob = st.date_input("Date of Birth", value=None)
            blood_group = st.selectbox("Blood Group", BLOOD_GROUPS)

            submit = st.form_submit_button("Register", use_container_width=True)

        if submit:
            # Validate phone number if provided
            if phone:
                is_valid = validate_mobile_number(phone)
                if not is_valid:
                    st.error(f"❌ Invalid phone number")
                    st.stop()
                st.info(f"✅ Valid phone number")
                
            response = register(
                user_id = get_state_manager().get('user_id'),  # Pass user_id for Google Sign In users
                full_name=full_name,
                email=email,
                phone=phone or None,
                date_of_birth=str(dob) if dob else None,
                blood_group=blood_group if blood_group else None,
            )
            if response and response.status_code == 201:
                st.success("✅ Account created! Please reload the page.")

            elif response:
                st.error(f"❌ {response.json().get('detail', 'Registration failed')}")
