"""Authentication components (login and register forms)."""
import streamlit as st
import re
from components.api import login, register
from components.utils import set_user, get_state_manager
from components.config import BLOOD_GROUPS
from components.google_signin import render_google_signin_button


def validate_mobile_number(phone: str) -> tuple[bool, str]:
    """
    Validate mobile number with flexible formatting support.
    
    Supports:
    - Indian format: 10 digits (e.g., 9876543210)
    - International format: +91-9876543210, +1-2025551234
    - Formats with spaces/dashes: 98 7654 3210, 987-654-3210
    - Optional country code: +91, +1, +44, etc.
    
    Args:
        phone: Phone number string to validate
    
    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    if not phone or not isinstance(phone, str):
        return False, "Phone number is required"
    
    # Remove whitespace and common separators
    cleaned_phone = re.sub(r'[\s\-\(\).]', '', phone)
    
    # Pattern explanation:
    # ^\+?[\d]{1,3}?[\d]{9,15}$ - Optional +, country code (1-3 digits), followed by 9-15 digits
    phone_pattern = r'^\+?[\d]{1,3}?[\d]{9,15}$'
    
    if not re.match(phone_pattern, cleaned_phone):
        return False, "Invalid mobile number format. Use 10+ digits, optionally with country code (e.g., +91-9876543210)"
    
    
    return True, "Valid mobile number"


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
                is_valid, validation_message = validate_mobile_number(phone)
                if not is_valid:
                    st.error(f"❌ {validation_message}")
                    st.stop()
                st.info(f"✅ {validation_message}")
                
            response = register(
                user_id = get_state_manager().get('user_id'),  # Pass user_id for Google Sign In users
                full_name=full_name,
                email=email,
                phone=phone or None,
                date_of_birth=str(dob) if dob else None,
                blood_group=blood_group if blood_group else None,
            )
            if response and response.status_code == 201:                    st.success("✅ Account created! Please reload the page.")

            elif response:
                st.error(f"❌ {response.json().get('detail', 'Registration failed')}")
