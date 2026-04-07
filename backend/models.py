# backend/models.py
import uuid
from datetime import datetime
from groq import BaseModel
from sqlalchemy import (Column, String, Boolean, DateTime, ForeignKey,
                        Integer, Text, Numeric, Date, Time, CheckConstraint, UniqueConstraint)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, synonym
from backend.database import Base

def new_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    email         = Column(String(255), primary_key=True, nullable=False)
    id            = synonym("email")
    # Keep `user.id` available in code as an alias to `email`.
    
    full_name     = Column(String(255), nullable=False)
    role          = Column(String(20), nullable=False)
    phone         = Column(String(20))
    is_active     = Column(Boolean, default=True)
    created_at    = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at    = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    doctor_profile  = relationship("Doctor",  back_populates="user", uselist=False)
    patient_profile = relationship("Patient", back_populates="user", uselist=False)


class Doctor(Base):
    __tablename__ = "doctors"
    id               = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    user_email       = Column(String(255), ForeignKey("users.email", ondelete="CASCADE"), unique=True)
    specialty        = Column(String(100), nullable=False)
    qualification    = Column(String(255))
    consultation_fee = Column(Numeric(10,2), default=0)
    created_at       = Column(DateTime(timezone=True), default=datetime.utcnow)
    user         = relationship("User", back_populates="doctor_profile")
    availability = relationship("DoctorAvailability", back_populates="doctor", cascade="all, delete")
    appointments = relationship("Appointment", back_populates="doctor")


class Patient(Base):
    __tablename__ = "patients"
    id            = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    user_email    = Column(String(255), ForeignKey("users.email", ondelete="CASCADE"), unique=True)
    date_of_birth = Column(Date)
    blood_group   = Column(String(5))
    allergies     = Column(Text)
    created_at    = Column(DateTime(timezone=True), default=datetime.utcnow)

    user         = relationship("User", back_populates="patient_profile")
    appointments = relationship("Appointment", back_populates="patient")
    # chat_history = relationship("ChatMessage", back_populates="patient", cascade="all, delete")


class Nurse(Base):
    __tablename__ = "nurses"
    id         = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    user_email = Column(String(255), ForeignKey("users.email", ondelete="CASCADE"), unique=True)
    department = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    user = relationship("User")


class DoctorAvailability(Base):
    __tablename__ = "doctor_availability"
    __table_args__ = (UniqueConstraint("doctor_id", "day_of_week", "start_time"),)

    id                    = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    doctor_id             = Column(UUID(as_uuid=False), ForeignKey("doctors.id", ondelete="CASCADE"))
    day_of_week           = Column(Integer, nullable=False)   # 0=Mon … 6=Sun
    start_time            = Column(Time, nullable=False)
    end_time              = Column(Time, nullable=False)
    slot_duration_minutes = Column(Integer, default=15)

    doctor = relationship("Doctor", back_populates="availability")


class Appointment(Base):
    __tablename__ = "appointments"

    id               = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    patient_id       = Column(UUID(as_uuid=False), ForeignKey("patients.id", ondelete="CASCADE"))
    doctor_id        = Column(UUID(as_uuid=False), ForeignKey("doctors.id", ondelete="CASCADE"))
    appointment_at   = Column(DateTime(timezone=True), nullable=False)
    duration_minutes = Column(Integer, default=15)
    status           = Column(String(20), default="scheduled")
    reason           = Column(Text)
    notes            = Column(Text)
    cancelled_by     = Column(String(255), ForeignKey("users.email"), nullable=True)
    cancelled_at     = Column(DateTime(timezone=True), nullable=True)
    cancel_reason    = Column(Text)
    drive_link       = Column(String(500), nullable=True)
    created_at       = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at       = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    is_confirmed     = Column(Boolean, default=False)
    patient  = relationship("Patient",  back_populates="appointments")
    doctor   = relationship("Doctor",   back_populates="appointments")
    feedback = relationship("Feedback", back_populates="appointment", uselist=False)


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id         = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    user_id    = Column(String(255), ForeignKey("users.id", ondelete="CASCADE"))
    role       = Column(String(20), nullable=False)   # 'user' | 'assistant'
    content    = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

    # user = relationship("User", back_populates="chat_history")


class Feedback(Base):
    __tablename__ = "feedback"
    id             = Column(UUID(as_uuid=False), primary_key=True, default=new_uuid)
    appointment_id = Column(UUID(as_uuid=False), ForeignKey("appointments.id", ondelete="CASCADE"), unique=True)
    patient_id     = Column(UUID(as_uuid=False), ForeignKey("patients.id"))
    doctor_id      = Column(UUID(as_uuid=False), ForeignKey("doctors.id"))
    raw_feedback   = Column(Text, nullable=False)
    ai_rating      = Column(Integer)
    ai_summary     = Column(Text)
    created_at     = Column(DateTime(timezone=True), default=datetime.utcnow)

    appointment = relationship("Appointment", back_populates="feedback")
