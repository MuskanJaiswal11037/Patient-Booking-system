# 🏥 MedApp — Doctor Patient Appointment System

> **Stack:** Streamlit · FastAPI · PostgreSQL · Claude (Anthropic LLM)

---

## Project Structure

```
medapp/
├── backend/
│   ├── main.py                 # FastAPI app + all routes
│   ├── models.py               # SQLAlchemy ORM models
│   ├── schemas.py              # Pydantic request/response schemas
│   ├── auth.py                 # JWT auth + role guards
│   ├── database.py             # Async SQLAlchemy engine
│   ├── config.py               # Settings from .env
│   ├── llm_service.py          # Claude integration
│   └── appointment_service.py  # Business logic
├── frontend/
│   └── streamlit_app.py        # Streamlit UI
├── db/
│   └── schema.sql              # PostgreSQL DDL + seed data
├── requirements.txt
└── .env.example
```

---

## Database Schema (ERD overview)

```
users ──────────────────────────────────────
  id, email, password_hash, full_name,
  role (patient|doctor|nurse), phone

doctors ─────────────────────────────────────
  id, user_id(FK→users), specialty,
  qualification, bio, consultation_fee

patients ────────────────────────────────────
  id, user_id(FK→users), date_of_birth,
  blood_group, allergies

doctor_availability ─────────────────────────
  id, doctor_id(FK), day_of_week(0-6),
  start_time, end_time, slot_duration_minutes

appointments ────────────────────────────────
  id, patient_id(FK), doctor_id(FK),
  appointment_at, duration_minutes,
  status (scheduled|completed|cancelled|no_show),
  reason, notes, cancelled_by, cancel_reason

chat_messages ───────────────────────────────
  id, patient_id(FK), role(user|assistant),
  content, created_at

feedback ────────────────────────────────────
  id, appointment_id(FK unique), patient_id,
  doctor_id, raw_feedback, ai_rating(1-5),
  ai_summary
```

---

## Step-by-Step Setup

### Step 1 — Prerequisites

```bash
# Python 3.11+
python --version

# PostgreSQL 15+
psql --version
```

### Step 2 — Clone & install dependencies

```bash
git clone <your-repo> medapp
cd medapp
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 3 — Configure environment

```bash
cp .env.example .env
```

Edit `.env`:
```
DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@localhost:5432/medapp
SYNC_DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/medapp
SECRET_KEY=<run: python -c "import secrets; print(secrets.token_hex(32))">
ANTHROPIC_API_KEY=sk-ant-...
```

### Step 4 — Create the database

```bash
psql -U postgres -c "CREATE DATABASE medapp;"
psql -U postgres -d medapp -f db/schema.sql
```

### Step 5 — Run the FastAPI backend

```bash
# From project root
uvicorn backend.main:app --reload --port 8000
```

Swagger UI → http://localhost:8000/docs

### Step 6 — Run the Streamlit UI

```bash
# In a separate terminal (same venv)
cd frontend
streamlit run streamlit_app.py
```

Streamlit → http://localhost:8501

---

## API Reference

| Method | Endpoint | Role | Description |
|--------|----------|------|-------------|
| POST | `/auth/register` | Public | Register patient/doctor/nurse |
| POST | `/auth/login` | Public | Get JWT token |
| GET  | `/doctors` | Any auth | List all doctors |
| POST | `/chat` | Patient | LLM booking chat |
| GET  | `/appointments` | Patient | List own appointments |
| POST | `/appointments/cancel` | Patient, Nurse | Cancel appointment |
| GET  | `/doctor/appointments` | Doctor, Nurse | View schedule |
| POST | `/feedback` | Patient | Submit feedback (AI rated) |

---

## How the Chat Booking Works

```
Patient types: "Book Dr. Sharma on 25th March at 11am"
         │
         ▼
FastAPI /chat
         │
         ├─► llm_service.chat()
         │     Claude reads conversation history
         │     Parses intent → emits ```action {"action":"book", ...}```
         │
         ├─► appointment_service.get_doctor_by_name()
         │     Finds doctor in DB (fuzzy match)
         │
         ├─► appointment_service.is_slot_free()
         │     Checks doctor_availability rules
         │     Checks no conflicting appointment in DB
         │
         ├── SLOT FREE  →  book_appointment() → confirm message
         │
         └── SLOT BUSY  →  suggest_free_slots() → show 3 alternatives
```

---

## How Feedback Rating Works

```
Patient writes: "The doctor was excellent, very thorough."
         │
         ▼
POST /feedback
         │
         ├─► llm_service.rate_feedback()
         │     Sends feedback to Claude
         │     Claude returns JSON: {"rating": 5, "summary": "..."}
         │
         └─► Stored in feedback table → returned to UI
```

---

## User Roles

| Role | Can do |
|------|--------|
| **Patient** | Register, login, book via chat, cancel own appointments, leave feedback |
| **Doctor** | Login, view their own schedule |
| **Nurse** | Login, view all appointments, cancel any appointment |

---

## Running in Production

```bash
# Backend with gunicorn
pip install gunicorn
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Use Alembic for migrations instead of create_all
alembic init alembic
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

---

## Environment Variables Reference

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | Async PostgreSQL URL (`postgresql+asyncpg://...`) |
| `SYNC_DATABASE_URL` | Sync URL for Alembic (`postgresql://...`) |
| `SECRET_KEY` | 32-byte hex for JWT signing |
| `ALGORITHM` | JWT algorithm (default: HS256) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token TTL (default: 480 = 8 hrs) |
| `ANTHROPIC_API_KEY` | Claude API key |
| `BACKEND_URL` | FastAPI base URL for Streamlit to call |
