# backend/schemas.py
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any, Dict, Union, Literal
from datetime import datetime, date, time


class User(BaseModel):
    # Keep this permissive because frontend identity providers may send non-UUID IDs.
    id: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    

# ── Auth ────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
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


class RegisterDoctorRequest(BaseModel):
    email:             EmailStr
    full_name:         str
    phone:             Optional[str] = None
    specialty:         Optional[str] = None
    qualification:     Optional[str] = None
    consultation_fee:  Optional[float] = None
    role:              str = "doctor"


class RegisterNurseRequest(BaseModel):
    email:      EmailStr
    full_name:  str
    phone:      Optional[str] = None
    department: Optional[str] = None
    role:       str = "nurse"


class AppointmentRequest(BaseModel):
    doctor_email: Optional[str] = None
    status: Optional[str] = None


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


class UserRoleResponse(BaseModel):
    role: str
    email: str
    full_name: str


class UserRoleRequest(BaseModel):
    email: str

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
    slot_duration_minutes: int = 15

# ── Appointments ────────────────────────────────────────────────
class AppointmentOut(BaseModel):
    id:              str
    doctor_name:     str
    patient_name:    str
    appointment_at:  datetime
    status:          str
    reason:          Optional[str]
    cancel_reason:   Optional[str]
    drive_link:      Optional[str] = None

    class Config:
        from_attributes = True

class UpdateAppointmentStatusRequest(BaseModel):
    appointment_id: str
    status: str


class AssignEmergencyDoctorRequest(BaseModel):
    """Assign a doctor to an emergency appointment (criticality level matches queue config)."""
    appointment_id: str
    doctor_email: EmailStr


class CreateEmergencyQuickRequest(BaseModel):
    """Emergency-only: time is server NOW(). Patient must exist. Doctor optional: by email and/or id."""
    patient_email: EmailStr
    reason: str = Field(..., min_length=1, max_length=2000)
    patient_name :str
    doctor_email: Optional[EmailStr] = None
    


class QueueManagementResponse(BaseModel):
    """Response for /appointment_details and /update_appointment_status."""
    success: bool
    message: str
    availability: Optional[Union[List[Dict[str, Any]], Dict[str, Any]]] = None


class QueueDoctorsResponse(BaseModel):
    success: bool
    message: str
    doctors: List[Dict[str, Any]] = Field(default_factory=list)


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
