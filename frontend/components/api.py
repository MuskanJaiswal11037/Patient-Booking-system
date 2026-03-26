"""API client module for backend communication."""
import streamlit as st
import httpx
from components.config import BACKEND_URL
from components.utils import get_state_manager, get_token


def api_request(method: str, path: str, **kwargs):
    """
    Make HTTP request to backend.
    
    Parameters
    ----------
    method : str
        HTTP method (GET, POST, etc.)
    path : str
        API endpoint path
    **kwargs
        Additional arguments for httpx.request
    
    Returns
    -------
    httpx.Response or None
        Response object or None if connection fails
    """
    headers = kwargs.pop("headers", {})
    token = get_token()
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        response = httpx.request(
            method,
            f"{BACKEND_URL}{path}",
            timeout=600,
            headers=headers,
            **kwargs
        )
        return response
    except httpx.ConnectError:
        st.error("❌ Cannot connect to backend. Is the FastAPI server running?")
        return None
    except Exception as e:
        st.error(f"❌ API Error: {str(e)}")
        return None


# Convenience functions for common endpoints

def login(email: str, password: str):
    """Login with email and password."""
    return api_request(
        "POST",
        "/auth/login",
        data={"username": email, "password": password}
    )


def register(user_id: str, full_name: str, email: str, phone: str = None,
             date_of_birth: str = None, blood_group: str = None):
    """Register new user."""
    payload = {
        "user_id": user_id,
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "date_of_birth": date_of_birth,
        "blood_group": blood_group,
    }
    return api_request("POST", "/auth/register", json=payload)


def is_registered():
    """Check if a user is registered."""
    response =  api_request(
        "POST",
        "/auth/check-or-insert-user",
        json={
            "email": get_state_manager().get("user_email")
        }
    )
    print("is_registered response:", response.text)
    if response.status_code == 200:
        data = response.json()
        return data.get("exists", False)
    return False


def send_chat_message(message: str):
    """Send chat message."""
    return api_request(
        "POST", 
        "/chat", 
        json={
            "body": {"message": message},
            "user": {
                "id": get_state_manager().get("user_id"),
                "email": get_state_manager().get("user_email"),
                "full_name": get_state_manager().get("full_name"),
                "role": get_state_manager().get("role"),
            }
        }
    )


