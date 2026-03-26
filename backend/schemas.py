# backend/schemas.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date, time
from uuid import UUID


class User(BaseModel):
    id: str
    email: Optional[str]
    full_name: str
    role: str
    

# ── Auth ────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    user_id:   str
    email:     EmailStr
    # password:  str = Field(min_length=6, max_length=72)
    full_name: str
    phone:     Optional[str] = None
    # doctor extras
    specialty:     Optional[str] = None
    qualification: Optional[str] = None
    # patient extras
    date_of_birth: Optional[date] = None
    blood_group:   Optional[str]  = None

class LoginRequest(BaseModel):
    email:    EmailStr
    password: str = Field(min_length=6, max_length=72)

class isRegisteredRequest(BaseModel):
    email: str

class isRegisteredResponse(BaseModel):
    exists: bool

class TokenResponse(BaseModel):
    access_token: str
    token_type:   str = "bearer"
    role:         str
    full_name:    str
    user_email:   str

# ── Doctors ─────────────────────────────────────────────────────
class DoctorOut(BaseModel):
    id:               str
    full_name:        str
    specialty:        str
    qualification:    Optional[str]
    consultation_fee: Optional[float]

    class Config:
        from_attributes = True

class AvailabilitySlot(BaseModel):
    day_of_week:           int
    start_time:            time
    end_time:              time
    slot_duration_minutes: int = 30

# ── Appointments ────────────────────────────────────────────────
class AppointmentOut(BaseModel):
    id:              str
    doctor_name:     str
    patient_name:    str
    appointment_at:  datetime
    status:          str
    reason:          Optional[str]
    cancel_reason:   Optional[str]

    class Config:
        from_attributes = True

class CancelRequest(BaseModel):
    appointment_id: str
    cancel_reason:  Optional[str] = "Cancelled by patient"

# ── Chat ────────────────────────────────────────────────────────
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply:          str
    action_taken:   Optional[str] = None   # "booked" | "cancelled" | "suggested_slots" | None
    appointment:    Optional[AppointmentOut] = None
    suggested_slots: Optional[List[datetime]] = None

# ── Feedback ────────────────────────────────────────────────────
class FeedbackRequest(BaseModel):
    appointment_id: str
    raw_feedback:   str

class FeedbackOut(BaseModel):
    ai_rating:  int
    ai_summary: str
