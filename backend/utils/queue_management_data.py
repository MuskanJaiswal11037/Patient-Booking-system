from typing import Any, Dict, List, Optional, Tuple
import uuid
from .database_handler import db_handler

def extract_appointments_data(
    doctor_email: Optional[str], status: Optional[str]
) -> dict:
    query = "SELECT * FROM appointments"
    conditions: List[str] = []
    params: List[Any] = []

    if status != "All":
        conditions.append("status = %s")
        params.append(status)
    if doctor_email is not None:
        query2 = "SELECT d.id FROM doctors d WHERE d.user_email = %s"
        res = db_handler.execute_query(query2, (doctor_email,))
        doctor_id = res[0]["id"] if res else None
        print(doctor_id)
        conditions.append("doctor_id = %s")
        params.append(doctor_id)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    qparams = tuple(params) if len(params) > 1 else params
    result = db_handler.execute_query(query, qparams)
    if result:
        return {
            "success": True,
            "message": "Sent all the required appointment details",
            "availability": result,
        }
    return {
        "success": False,
        "message": "Failed to load appointment",
        "availability": [],
    }

def update_status(appointment_id, status):
    query = """
    UPDATE appointments SET status = %s WHERE id = %s
    RETURNING id, status
    """
    params = (status, appointment_id)
    result = db_handler.execute_query(query, params)
    if result:
        return {
            "success": True,
            "message": "Detailes updated successfully",
            "availability": result[0],
        }
    return {
        "success": False,
        "message": "Failed to update appointment",
    }

def waiting_list_people():
    query = """
        SELECT *
        FROM appointments
        WHERE status IN ('scheduled', 'rescheduled')
          AND appointment_at <= NOW()
          AND DATE(appointment_at) = CURRENT_DATE
        ORDER BY criticality_level, appointment_at, created_at
    """
    result = db_handler.execute_query(query, ())
    # Empty list is valid: no one in the waiting queue today (still HTTP 200).
    rows = result if result is not None else []
    return {
        "success": True,
        "message": "Waiting list sent successfully!"
        if rows
        else "No scheduled appointments in the waiting queue for today",
        "availability": rows,
    }


# criticality_level: 0 = EMERGENCY, 1 = NORMAL (schema CHECK 0..1)
_EMERGENCY_LEVEL = 0


def list_emergency_appointments() -> dict:
    query = """
        SELECT
            a.*,
            up.full_name AS patient_name
        FROM appointments a
        JOIN patients p ON p.id = a.patient_id
        JOIN users up ON up.email = p.user_email
        WHERE a.criticality_level = %s
          AND a.status IN ('pending', 'scheduled', 'in-progress')
        ORDER BY a.appointment_at ASC NULLS LAST, a.created_at ASC
    """
    rows = db_handler.execute_query(query, (_EMERGENCY_LEVEL,))
    out = rows if rows is not None else []
    return {
        "success": True,
        "message": "Emergency cases loaded"
        if out
        else "No active emergency appointments",
        "availability": out,
    }


def list_doctors_for_queue() -> dict:
    query = """
        SELECT d.id::text AS id, d.user_email, u.full_name, d.specialty
        FROM doctors d
        JOIN users u ON u.email = d.user_email
        WHERE COALESCE(u.is_active, TRUE)
        ORDER BY u.full_name
    """
    rows = db_handler.execute_query(query, ())
    out = rows if rows is not None else []
    return {
        "success": True,
        "message": "Doctors loaded",
        "doctors": out,
    }

def create_emergency_appointment_now(
    patient_email: str,
    reason: str,
    doctor_email: Optional[str] = None,
    patient_name: Optional[str] = None,
    duration_minutes: int = 15,
    status: str = "scheduled",
) -> dict:
    """Insert emergency row with appointment_at = NOW() in the database."""
    pq = "SELECT id FROM patients WHERE user_email = %s"
    pr = db_handler.execute_query(pq, (patient_email,))
    if not pr:
        id = uuid.uuid4()
        query2 = "INSERT INTO users (email, full_name, role, created_at) VALUES (%s, %s, %s, NOW())"
        db_handler.execute_query(query2, (patient_email, patient_name or "Unknown", "patient"))
        query3 = "INSERT INTO patients (id, user_email) VALUES (%s, %s) returning id"
        
        pr = db_handler.execute_query(query3, (id, patient_email,))
        if not pr:
            return {
                "success": False,
                "message": "Patient not found for that email. Facing error in registration.",
                "availability": None,
            }
    patient_row_id = pr[0]["id"]

    dq = "SELECT id FROM doctors WHERE user_email = %s"
    dr = db_handler.execute_query(dq, (doctor_email,))
    resolved_doctor_id = dr[0]["id"] if dr else None
    if not resolved_doctor_id:
        return {
            "success": False,
            "message": "Doctor email not found. Please provide a valid doctor email or leave it blank.",
            "availability": None,
        }
    ins = """
        INSERT INTO appointments (
            patient_id, doctor_id, appointment_at, duration_minutes,
            status, reason, notes, criticality_level
        )
        VALUES (%s, %s, NOW(), %s, %s, %s, %s, %s)
        RETURNING id, patient_id, doctor_id, appointment_at, status, criticality_level
    """
    result = db_handler.execute_query(
        ins,
        (
            patient_row_id,
            resolved_doctor_id,
            duration_minutes,
            status,
            reason,
            None,
            0,
        ),
    )
    if result:
        return {
            "success": True,
            "message": "Emergency appointment created (time set to database NOW())",
            "availability": result[0],
        }
    return {
        "success": False,
        "message": "Failed to create emergency appointment",
        "availability": None,
    }
