"""Configuration module for Streamlit app."""
import os
import streamlit as st

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
PAGE_TITLE = "MedApp"
PAGE_ICON = "🏥"
LAYOUT = "wide"
INITIAL_SIDEBAR_STATE = "expanded"

# State keys
STATE_KEYS = {
    "token": None,
    "role": None,
    "full_name": None,
    "user_id": None,
    "chat_history": [],
}

# Role-specific navigation
ROLE_NAVIGATION = {
    "patient": ["💬 Book via Chat"],
    "doctor": ["📅 My Schedule"],
    "nurse": ["📅 Appointments"],
}

# Status color mapping
STATUS_COLORS = {
    "scheduled": "🟢",
    "completed": "🔵",
    "cancelled": "🔴",
}

# Blood groups
BLOOD_GROUPS = ["", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
