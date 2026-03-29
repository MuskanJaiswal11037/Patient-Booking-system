from typing import Any, List, Optional
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
          AND appointment_at >= NOW()
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