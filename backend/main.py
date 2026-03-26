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
from typing import Annotated, Optional
from fastapi import Body, FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.database import get_db, engine, Base
from backend.models import (User, Doctor, Patient, Appointment,
                             ChatMessage, Feedback)
from backend.auth import (hash_password, verify_password, create_access_token,
                           get_current_user, require_role)
from backend.schemas import (RegisterRequest, TokenResponse, ChatRequest,
                              ChatResponse, AppointmentOut, CancelRequest,
                              FeedbackRequest, FeedbackOut, DoctorOut, User as UserSchema, isRegisteredRequest, isRegisteredResponse)
from backend import llm_service

app = FastAPI(title="MedApp API", version="1.0.0")

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

# @app.post("/auth/login", response_model=TokenResponse)
# async def login(
#     form: OAuth2PasswordRequestForm = Depends(),
#     db: AsyncSession = Depends(get_db),
# ):
#     from backend.auth import verify_password
    
#     result = await db.execute(select(User).where(User.email == form.username))
#     user = result.scalar_one_or_none()
    
#     # If user doesn't exist, create a default user (skip password validation for auto-create)
#     if not user:
#         user = User(
#             email=form.username,
#             password_hash="",  # Skip password hashing for test user
#             full_name=form.username.split("@")[0],
#             role=form.role if hasattr(form, "role") else "patient",  # Default to patient role
#             is_active=True,
#         )
#         db.add(user)
#         await db.flush()
        
#         # Create patient profile for the default user
#         db.add(Patient(user_id=user.id))
#         await db.commit()
#     else:
#         # For existing users with non-empty password, verify it
#         if user.password_hash and not verify_password(form.password, user.password_hash):
#             raise HTTPException(status_code=401, detail="Invalid credentials")

#     token = create_access_token({"sub": user.id, "role": user.role})
#     return TokenResponse(access_token=token, role=user.role,
#                          full_name=user.full_name, user_id=user.id)


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

    from types import SimpleNamespace
    patient = SimpleNamespace(id=user.id)    
    if not patient:
        raise HTTPException(400, "Patient profile not found")
    
    
    role = db.execute(select(User.role).where(User.email == user.email))
    role = role.scalar_one_or_none()
    role =  role[0]["role"] if role else "patient" 
    response = llm_service.chat_with_deep_agent(body.message, user_email=user.email, role=role)
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

