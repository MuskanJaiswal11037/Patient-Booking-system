"""API client module for backend communication."""
from typing import Any, Dict, List, Optional

import streamlit as st
import httpx
import json
from components.config import BACKEND_URL
from components.utils import get_state_manager, get_token
import pandas as pd

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


def get_user_role(email: str) -> Optional[str]:
    """
    Get the role of a user by their email address.
    
    Args:
        email: User's email address
    
    Returns:
        str: user role (e.g., 'patient', 'doctor', 'nurse', 'admin')
        None: if request fails or user not found
    """
    if not email:
        print("Email is required to get user role")
        return None
    
    response = api_request(
        "POST", 
        "/auth/user-role-by-email", 
        json={"email": get_state_manager().get("user_email")}
    )
    if response is None:
        return None
    if response.status_code != 200:
        print(f"Failed to get user role: {response.status_code}")
        return None
    try:
        data = response.json()
        return data.get("role")
    except Exception as e:
        print(f"Error parsing user role response: {str(e)}")
        return None


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

def get_waiting_list() -> Optional[List[Any]]:
    # Avoid trailing-slash redirects/mismatch across deployments.
    response = api_request("GET", "/waiting_list")
    if response is None:
        return None
    if response.status_code != 200:
        try:
            detail = response.json().get("message", response.text)
        except Exception:
            detail = response.text
        st.error(f"waiting_list failed: {detail}")
        return None
    data = response.json()
    if not data.get("success", True):
        st.error(data.get("message", "Unable to load waiting list"))
        return None
    return data.get("availability", [])

def get_appointment_details(
    doctor_email: Optional[str] = None,
    status: Optional[str] = None,
) -> Optional[List[Any]]:
    """
    Queue management: list appointments (POST /appointment_details).

    Parameters
    ----------
    doctor_email : str, optional
        Filter by doctor's user email. None or empty = all doctors.
    status : str, optional
        Filter by queue status (scheduled, in-progress, ...). None or 'All' = any.
    """
    payload = {}
    payload["doctor_email"] = doctor_email
    
    payload["status"] = status
    print(payload)
    response = api_request("POST", "/appointment_details", json=payload)
    if response is None:
        return None
    if response.status_code != 200:
        try:
            detail = response.json().get("message", response.text)
        except Exception:
            detail = response.text
        st.error(f"appointment_details failed: {response.json().get('message', response.text)}")
        return None
    data = response.json()
    if not data.get("success"):
        st.error(response.json().get("message", response.text))
        return None
    avail = data.get("availability")
    return avail


def get_emergency_appointments() -> Optional[List[Any]]:
    response = api_request("GET", "/emergency_appointments")
    if response is None:
        return None
    if response.status_code != 200:
        try:
            detail = response.json().get("message", response.text)
        except Exception:
            detail = response.text
        st.error(f"emergency_appointments failed: {detail}")
        return None
    data = response.json()
    if not data.get("success", True):
        st.error(data.get("message", "Unable to load emergency cases"))
        return None
    return data.get("availability") or []


def get_queue_doctors() -> Optional[List[Dict[str, Any]]]:
    response = api_request("GET", "/queue/doctors")
    if response is None:
        return None
    if response.status_code != 200:
        try:
            detail = response.json().get("message", response.text)
        except Exception:
            detail = response.text
        st.error(f"queue/doctors failed: {detail}")
        return None
    data = response.json()
    if not data.get("success", True):
        st.error(data.get("message", "Unable to load doctors"))
        return None
    return data.get("doctors") or []


def create_emergency_appointment_quick(
    patient_email: str,
    reason: str,
    patient_name: str,
    doctor_email: Optional[str] = None
) -> bool:
    """Emergency only: appointment_at is database NOW()."""
    payload: Dict[str, Any] = {
        "patient_email": patient_email.strip(),
        "reason": reason.strip(),
    }
    if doctor_email and str(doctor_email).strip():
        payload["doctor_email"] = str(doctor_email).strip()

    if patient_name and str(patient_name).strip():
        payload["patient_name"] = str(patient_name).strip()

    response = api_request(
        "POST", "/create_emergency_appointment_quick", json=payload
    )
    if response is None:
        return False
    if response.status_code != 200:
        try:
            j = response.json()
            detail = j.get("detail")
            if not isinstance(detail, str):
                detail = j.get("message", response.text)
        except Exception:
            detail = response.text
        st.error(f"create_emergency_appointment_quick failed: {detail}")
        return False
    data = response.json()
    if not data.get("success"):
        st.error(data.get("message", "Create failed"))
        return False
    return True


def update_queue_appointment_status(appointment_id: str, status: str) -> bool:
    """Queue management: update status (POST /update_appointment_status)."""
    response = api_request(
        "POST",
        "/update_appointment_status",
        json={"appointment_id": str(appointment_id), "status": status},
    )
    if response is None:
        return False
    if response.status_code != 200:
        try:
            detail = response.json().get("message", response.text)
        except Exception:
            detail = response.text
        st.error(f"update_appointment_status failed: {detail}")
        return False
    data = response.json()
    if not data.get("success"):
        st.error(data.get("message", "Update failed"))
        return False
    return True


# ─── Speech-to-Text & Text-to-Speech ────────────────────────────

def transcribe_audio(audio_bytes: bytes, filename: str = "audio.wav") -> Optional[str]:
    """
    Convert audio bytes to text using OpenAI Whisper.
    
    Parameters
    ----------
    audio_bytes : bytes
        Raw audio file bytes
    filename : str
        Filename with extension (used for format detection)
    
    Returns
    -------
    str or None
        Transcribed text or None on error
    """

    
    try:
        files = {"audio": (filename, audio_bytes, "audio/wav")}
        response = httpx.request(
            "POST",
            f"{BACKEND_URL}/transcribe",
            files=files,
            timeout=30,
        )
        
        if response.status_code == 200:
            data = response.json()
            return data.get("text", "").strip()
        else:
            st.error(f"❌ Transcription failed: {response.json().get('detail', response.text)}")
            return None
    except Exception as e:
        st.error(f"❌ Transcription error: {str(e)}")
        return None


def text_to_speech(text: str, voice: str = "alloy") -> Optional[bytes]:
    """
    Convert text to speech audio using OpenAI TTS.
    
    Parameters
    ----------
    text : str
        Text to convert to speech
    voice : str
        Voice name: 'alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'
    
    Returns
    -------
    bytes or None
        Audio MP3 bytes or None on error
    """
    
    try:
        response = httpx.request(
            "POST",
            f"{BACKEND_URL}/tts",
            json={"text": text, "voice": voice},
            timeout=30,
        )
        
        if response.status_code == 200:
            return response.content
        else:
            st.error(f"❌ Text-to-speech failed: {response.json().get('detail', response.text)}")
            return None
    except Exception as e:
        st.error(f"❌ Text-to-speech error: {str(e)}")
        return None


