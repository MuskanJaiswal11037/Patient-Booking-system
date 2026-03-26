"""
Utility modules for Hospital Management System.
"""

from .database_handler import (
    DatabaseHandler,
    DatabaseException,
)

from .prompts import (
    get_system_prompt,
    HOSPITAL_AGENT_SYSTEM_PROMPT,
    PATIENT_FOCUSED_PROMPT,
    DOCTOR_FOCUSED_PROMPT,
)

__all__ = [
    "DatabaseHandler",
    "DatabaseException",
    "get_system_prompt",
    "HOSPITAL_AGENT_SYSTEM_PROMPT",
    "PATIENT_FOCUSED_PROMPT",
    "DOCTOR_FOCUSED_PROMPT",
]

__version__ = "1.0.0"
