"""Utility functions for session state and helpers."""
import streamlit as st
from typing import Any, Optional
from components.config import STATE_KEYS
import copy
import re

class StateManager:
    """
    Centralized state management for Streamlit applications.
    
    A simple, type-safe interface for managing Streamlit session state
    with just two core methods: set and get.
    
    Examples
    --------
    >>> state = StateManager()
    >>> state.set("token", "abc123")
    >>> state.get("token")
    'abc123'
    >>> state.get("missing_key", default="default_value")
    'default_value'
    """
    
    @staticmethod
    def set(key: str, value: Any) -> None:
        """
        Set a state value.
        
        Parameters
        ----------
        key : str
            State key to set
        value : Any
            Value to set
        
        Examples
        --------
        >>> state.set("count", 5)
        >>> state.set("user_data", {"name": "John"})
        """
        st.session_state[key] = value
    
    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """
        Get a state value with optional default.
        
        Parameters
        ----------
        key : str
            State key
        default : Any, optional
            Default value if key doesn't exist
        
        Returns
        -------
        Any
            State value or default
        
        Examples
        --------
        >>> state.get("token")
        >>> state.get("role", default="guest")
        """
        return st.session_state.get(key, default)


# ── Global Instance ──────────────────────────────────────────────

_state_manager: Optional[StateManager] = None


def get_state_manager() -> StateManager:
    """
    Get global state manager instance.
    
    Returns
    -------
    StateManager
        Global state manager
    
    Examples
    --------
    >>> state = get_state_manager()
    >>> state.set("key", "value")
    """
    return StateManager


# ── Initialization ───────────────────────────────────────────────

def init_session_state():
    """Initialize session state with default values."""
    for key, value in STATE_KEYS.items():
        if key not in st.session_state:
            st.session_state[key] = copy.deepcopy(value)

def init_user() -> None:
    """
    Initialize user authentication data from Streamlit's experimental user.
    
    Automatically populates user data (name, email, role, user_id) if user
    is logged in via Streamlit's authentication system.
    
    This function is called on app startup to sync authentication state.
    
    Examples
    --------
    >>> init_user()
    """
    state = get_state_manager()
    
    # Check if user is authenticated via Streamlit
    if st.experimental_user.is_logged_in:
        # Extract user info from Streamlit experimental user
        full_name = st.experimental_user.name
        user_email = st.experimental_user.email
        user_id = st.experimental_user.sub
        
        # Set user data in state
        state.set("full_name", full_name)
        state.set("user_email", user_email)
        state.set("user_id", user_id)
        state.set("role", "patient")  # Set default role for authenticated users


# ── Authentication Utilities ──────────────────────────────────────

def is_logged_in() -> bool:
    """
    Check if user is currently logged in.
    
    Returns
    -------
    bool
        True if user has valid authentication token, False otherwise
    
    Examples
    --------
    >>> if is_logged_in():
    ...     show_dashboard()
    >>> else:
    ...     show_login_page()
    """
    return st.experimental_user.is_logged_in


def logout() -> None:
    """
    Logout user by clearing all authentication and session data.
    
    Clears token, role, user ID, full name, and chat history.
    After calling this, should call st.rerun() to refresh the app.
    
    Examples
    --------
    >>> logout()
    >>> st.rerun()
    """
    st.logout()
    state = get_state_manager()
    state.set("token", None)
    state.set("role", None)
    state.set("user_id", None)
    state.set("full_name", None)
    state.set("chat_history", [])


def get_token() -> Optional[str]:
    """
    Get the current authentication token.
    
    Returns
    -------
    Optional[str]
        Authentication token if user is logged in, None otherwise
    
    Examples
    --------
    >>> token = get_token()
    >>> if token:
    ...     use_token_for_api_calls(token)
    """
    state = get_state_manager()
    return state.get("token")


def set_user(token: str, role: str, full_name: str, user_id: str) -> None:
    """
    Set user authentication data.
    
    Parameters
    ----------
    token : str
        Authentication token
    role : str
        User role (patient, doctor, nurse)
    full_name : str
        User's full name
    user_id : str
        User's unique ID
    
    Examples
    --------
    >>> set_user("jwt_token", "patient", "John Doe", "user_123")
    """
    state = get_state_manager()
    state.set("token", token)
    state.set("role", role)
    state.set("full_name", full_name)
    state.set("user_id", user_id)


# ── Chat History Utilities ────────────────────────────────────────

def reset_chat_history() -> None:
    """
    Clear all chat history from session state.
    
    Examples
    --------
    >>> reset_chat_history()
    """
    state = get_state_manager()
    state.set("chat_history", [])


def get_chat_history() -> list:
    """
    Get complete chat history from session state.
    
    Returns
    -------
    list
        List of messages with role and content
    
    Examples
    --------
    >>> history = get_chat_history()
    >>> for message in history:
    ...     print(f"{message['role']}: {message['content']}")
    """
    state = get_state_manager()
    return state.get("chat_history", [])


def add_chat_message(role: str, content: str) -> None:
    """
    Add a message to chat history.
    
    Parameters
    ----------
    role : str
        Message role (user, assistant)
    content : str
        Message content
    
    Examples
    --------
    >>> add_chat_message("user", "Hello")
    >>> add_chat_message("assistant", "Hi there!")
    """
    state = get_state_manager()
    history = state.get("chat_history", [])
    history.append({"role": role, "content": content})
    state.set("chat_history", history)

def validate_mobile_number(phone: str) -> bool:
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
        return True
    
    # Remove whitespace and common separators
    cleaned_phone = re.sub(r'[\s\-\(\).]', '', phone)
    
    # Pattern explanation:
    # ^\+?[\d]{1,3}?[\d]{9,15}$ - Optional +, country code (1-3 digits), followed by 10 digits
    phone_pattern = r'^\+?([\d]{1,3})?[\d]{10}$'
    
    if not re.match(phone_pattern, cleaned_phone):
        return False

    return True

def validate_email_id(email_id: str):
    email_id = email_id.strip()
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email_id):
        return False
    return True

if __name__ == "__main__":
    email = "abcde"
    print(validate_email_id(email))
