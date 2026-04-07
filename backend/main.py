# backend/main.py
"""
FastAPI entrypoint.
Routes:
  POST  /auth/register
  POST  /auth/login
  GET   /doctors
  GET   /appointments            (patient's own)
  POST  /chat                    (LLM booking chat)
  POST  /appointments/cancel
  POST  /feedback
  GET   /doctor/appointments     (doctor's schedule)
"""
from datetime import datetime
from openai import OpenAI
from typing import Annotated, Optional
from fastapi import Body, FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import Session
import numpy as np
from backend.utils import queue_management_data
from backend.database import get_db, engine, Base
from backend.models import (User, Doctor, Patient, Appointment,
                             ChatMessage, Feedback, Nurse)
from backend.auth import (hash_password, verify_password, create_access_token,
                           get_current_user, require_role)
from backend.schemas import (RegisterRequest, TokenResponse, ChatRequest,
                              ChatResponse, CancelRequest,
                              FeedbackRequest, FeedbackOut, DoctorOut, User as UserSchema, isRegisteredRequest, isRegisteredResponse, AppointmentRequest, UpdateAppointmentStatusRequest, QueueManagementResponse, QueueDoctorsResponse, CreateEmergencyQuickRequest, AssignEmergencyDoctorRequest, UserRoleResponse, UserRoleRequest, RegisterDoctorRequest, RegisterNurseRequest)
from backend import llm_service
from backend.config import settings
import logging
import io
from fastapi import UploadFile, File
from fastapi.responses import StreamingResponse
from openai import OpenAI
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from backend.utils.google_form_handler import sync_google_form_submissions

logger = logging.getLogger(__name__)

app = FastAPI(title="MedApp API", version="1.0.0")

# ══════════════════════════════════════════════════════════════════
#  BACKGROUND SCHEDULER - Google Form Sync
# ══════════════════════════════════════════════════════════════════
scheduler = BackgroundScheduler(daemon=True)

def scheduled_google_form_sync():
    """Background job to sync Google Form submissions every 5 minutes."""
    try:
        result = sync_google_form_submissions()
        logger.info(f"✅ Scheduled sync completed: {result}")
    except Exception as e:
        logger.error(f"❌ Error in scheduled sync: {e}")

@app.on_event("startup")
async def startup_event():
    """Start background scheduler on app startup."""
    if not scheduler.running:
        # Add job: sync every 5 minutes (300 seconds)
        scheduler.add_job(
            scheduled_google_form_sync,
            trigger=IntervalTrigger(seconds=300),  # 5 minutes
            id='sync_google_forms',
            name='Sync Google Form Submissions',
            replace_existing=True
        )
        scheduler.start()
        logger.info("🚀 Background scheduler started - Google Form sync: every 5 minutes")

@app.on_event("shutdown")
async def shutdown_event():
    """Stop background scheduler on app shutdown."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("🛑 Background scheduler stopped")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── DB init (dev only – use Alembic in prod) ────────────────────
# @app.on_event("startup")
# async def startup():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)


# ══════════════════════════════════════════════════════════════════
#  AUTH
# ══════════════════════════════════════════════════════════════════
@app.post("/auth/register", status_code=201)
async def register(body: RegisterRequest, db: Session = Depends(get_db)):
    # unique email check
    existing = db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(400, "Email already registered")

    user = User(
        email=body.email,
        full_name=body.full_name,
        role="patient",  # Default role for registration
        phone=body.phone,
    )
    db.add(user)
    db.flush()

    db.add(Patient(user_email=body.email, date_of_birth=body.date_of_birth,
                       blood_group=body.blood_group))
    print(f"Registered user {user.email} with ID {user.id}" )
    db.commit()
    return {"message": "Registered successfully", "role": "patient"}


@app.post("/auth/register-doctor", status_code=201)
async def register_doctor(body: RegisterDoctorRequest, db: Session = Depends(get_db)):
    """Register a new doctor."""
    # unique email check
    existing = db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(400, "Email already registered")

    user = User(
        email=body.email,
        full_name=body.full_name,
        role="doctor",
        phone=body.phone,
    )
    db.add(user)
    db.flush()

    doctor = Doctor(
        user_email=body.email,
        specialty=body.specialty or "General",
        qualification=body.qualification,
        consultation_fee=body.consultation_fee or 0.0
    )
    db.add(doctor)
    print(f"Registered doctor {user.email} with ID {user.id}")
    db.commit()
    return {"message": "Doctor registered successfully", "role": "doctor", "email": body.email}


@app.post("/auth/register-nurse", status_code=201)
async def register_nurse(body: RegisterNurseRequest, db: Session = Depends(get_db)):
    """Register a new nurse."""
    # unique email check
    existing = db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(400, "Email already registered")

    user = User(
        email=body.email,
        full_name=body.full_name,
        role="nurse",
        phone=body.phone,
    )
    db.add(user)
    db.flush()

    nurse = Nurse(
        user_email=body.email,
        department=body.department or "General"
    )
    db.add(nurse)
    print(f"Registered nurse {user.email} with ID {user.id}")
    db.commit()
    return {"message": "Nurse registered successfully", "role": "nurse", "email": body.email}



@app.post("/auth/check-or-insert-user", response_model=isRegisteredResponse)
async def check_or_insert_user(
    body: isRegisteredRequest,
    db: Session = Depends(get_db),
):
    """
    Check if a user exists in the database by user_email.
    If not, insert the user with the role of 'patient'.
    """
    result = db.execute(select(User).where(User.email == body.email))
    user = result.scalar_one_or_none()

    if not user:
       return {"exists": False}
    else:
        return {"exists": True}


@app.post("/auth/user-role-by-email", response_model=UserRoleResponse)
async def get_user_role_by_email(body: UserRoleRequest, db: Session = Depends(get_db)):
    """
    Get the role of a user by their email address.
    
    Args:
        body: UserRoleRequest containing email field
    
    Returns:
        UserRoleResponse with role, email, and full_name
    
    Raises:
        404: If user with provided email not found
        400: If email is empty or invalid
    """
    if not body.email or len(body.email.strip()) == 0:
        raise HTTPException(status_code=400, detail="Email is required")
    
    result = db.execute(select(User).where(User.email == body.email.strip()))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail=f"User not found with email: {body.email}")
    
    return UserRoleResponse(
        role=user.role,
        email=user.email,
        full_name=user.full_name
    )


@app.post("/appointment_details", response_model=QueueManagementResponse)
async def appointment_details(body: AppointmentRequest):
    result = queue_management_data.extract_appointments_data(
        doctor_email=body.doctor_email or None, status=body.status or None
    )
    # print(result)
    if result["success"]:
        return QueueManagementResponse(
            success=result["success"],
            message=result["message"],
            availability=result["availability"],
        )
    raise HTTPException(status_code=400, detail=result["message"])

@app.get("/waiting_list", response_model=QueueManagementResponse)
async def waiting_list():
    result = queue_management_data.waiting_list_people()
    if result["success"]:
        return QueueManagementResponse(
            success=result["success"],
            message=result["message"],
            availability=result["availability"],
        )
    raise HTTPException(status_code=400, detail=result["message"])
    

@app.post("/update_appointment_status", response_model=QueueManagementResponse)
async def update_appointment_status(body: UpdateAppointmentStatusRequest):
    result = queue_management_data.update_status(body.appointment_id, body.status)
    if result["success"]:
        return QueueManagementResponse(
            success=result["success"],
            message=result["message"],
            availability=result["availability"],
        )
    raise HTTPException(status_code=400, detail=result["message"])


@app.get("/emergency_appointments", response_model=QueueManagementResponse)
async def emergency_appointments():
    result = queue_management_data.list_emergency_appointments()
    return QueueManagementResponse(
        success=result["success"],
        message=result["message"],
        availability=result["availability"],
    )


@app.get("/queue/doctors", response_model=QueueDoctorsResponse)
async def queue_doctors():
    result = queue_management_data.list_doctors_for_queue()
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result.get("message", "Failed to load doctors"))
    return QueueDoctorsResponse(
        success=True,
        message=result["message"],
        doctors=result["doctors"],
    )


@app.post("/create_emergency_appointment_quick", response_model=QueueManagementResponse)
async def create_emergency_appointment_quick(body: CreateEmergencyQuickRequest):
    result = queue_management_data.create_emergency_appointment_now(
        patient_email=str(body.patient_email),
        reason=body.reason,
        doctor_email=str(body.doctor_email) if body.doctor_email else None,
        patient_name=str(body.patient_name) if body.patient_name else None,
    )
    if result["success"]:
        return QueueManagementResponse(
            success=result["success"],
            message=result["message"],
            availability=result["availability"],
        )
    raise HTTPException(status_code=400, detail=result["message"])



# ══════════════════════════════════════════════════════════════════
#  CHAT  (LLM booking agent)
# ══════════════════════════════════════════════════════════════════
@app.post("/chat", response_model=ChatResponse)
async def chat(
    body: ChatRequest,
    user: UserSchema,
    db: AsyncSession = Depends(get_db),
):
    # Load patient profile
    # result = db.execute(
    #     select(Patient).where(Patient.user_id == user.id)
    # )
    # patient = result.scalar_one_or_none()

    # from types import SimpleNamespace
    # patient = SimpleNamespace(id=user.id)    
    # if not patient:
    #     raise HTTPException(400, "Patient profile not found")
    
    
    user_role = db.execute(select(User.role).where(User.email == user.email)).scalar_one_or_none()
    role = user_role or user.role or "patient"
    response = llm_service.chat_with_deep_agent(
        body.message,
        user_email=user.email or "",
        user_role=role,
    )
    print(response)

    # Persist messages to chat history
    # db.add(ChatMessage(user_id=patient.id, role="user", content=body.message))
    # db.add(ChatMessage(user_id=patient.id, role="assistant", content=response.get("reply", "")))
    # db.commit()

    return ChatResponse(
        reply=response.get("reply", ""),
        action_taken=None,
        appointment=None,
        suggested_slots=None,
    )



def is_silent(audio_bytes, threshold=350):
    audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
    return np.abs(audio_array).mean() < threshold

@app.post("/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...),
):
    """
    Convert speech audio to text using OpenAI Whisper.
    Accepts audio files (wav, webm, mp3, m4a, ogg).
    Returns: {"text": "transcribed text"}
    """
    if not settings.OPENAI_API_KEY:
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY not configured")
 
    try: 
        # Read the uploaded audio bytes
        audio_bytes = await audio.read()
        if len(audio_bytes) < 100:
            raise HTTPException(status_code=400, detail="Audio file is too small or empty")
        
        if is_silent(audio_bytes):
            return {"text": ""}  # skip transcription
 
        # Whisper needs a filename with extension for format detection
        filename = audio.filename or "audio.wav"
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        transcript = client.audio.transcriptions.create(
            model="whisper-1",
            file=(filename, audio_bytes),
            language="en",
        )
        text = transcript.text.strip()
        logger.info(f"Transcribed {len(audio_bytes)} bytes -> '{text[:80]}...'")
        return {"text": text}
 
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Transcription error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Transcription failed: {type(e).__name__}: {e}")
 
 
# ─── Text-to-Speech (OpenAI TTS) ─────────────────────────────
 
@app.post("/tts")
async def text_to_speech(
    body: dict,
):
    """
    Convert text to speech using OpenAI TTS.
    Request body: {"text": "...", "voice": "alloy"} (voice is optional)
    Returns: audio/mpeg stream
    """
    if not settings.OPENAI_API_KEY:
        raise HTTPException(status_code=503, detail="OPENAI_API_KEY not configured")
 
    text = body.get("text", "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="No text provided")
 
    # Truncate very long texts (TTS has limits and it's meant for the chat reply)
    if len(text) > 4096:
        text = text[:4096]
 
    voice = body.get("voice", "alloy")  # alloy, echo, fable, onyx, nova, shimmer
  
    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
 
        response = client.audio.speech.create(
            model="tts-1",
            voice=voice,
            input=text,
            response_format="mp3",
        )
 
        # Stream the audio bytes back
        audio_bytes = response.content
        logger.info(f"TTS generated {len(audio_bytes)} bytes for {len(text)} chars")
        return StreamingResponse(
            io.BytesIO(audio_bytes),
            media_type="audio/mpeg",
            headers={"Content-Disposition": "inline; filename=reply.mp3"},
        )
 
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"TTS error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"TTS failed: {type(e).__name__}: {e}")


# ══════════════════════════════════════════════════════════════════
#  GOOGLE FORM SYNC - Manual Endpoint
# ══════════════════════════════════════════════════════════════════

@app.post("/google-forms/sync")
async def manual_google_form_sync():
    """
    Manually trigger Google Form submission sync.
    This endpoint allows you to manually sync Google Form submissions to the database.
    
    Returns:
        {
            "success": true,
            "message": "Google Form sync completed",
            "total_submissions": 5,
            "successful": 3,
            "skipped_duplicates": 2,
            "failed": 0,
            "errors": []
        }
    """
    return sync_google_form_submissions()


@app.get("/google-forms/status")
async def google_form_sync_status():
    """
    Get the status of the background Google Form sync scheduler.
    
    Returns:
        {
            "running": true,
            "schedule_interval_seconds": 300,
            "schedule_interval_minutes": 5,
            "next_run_time": "2026-04-07 12:05:30"
        }
    """
    if scheduler.running:
        job = scheduler.get_job('sync_google_forms')
        return {
            "running": True,
            "schedule_interval_seconds": 300,
            "schedule_interval_minutes": 5,
            "next_run_time": str(job.next_run_time) if job else "Not scheduled"
        }
    return {
        "running": False,
        "message": "Scheduler is not running"
    }


