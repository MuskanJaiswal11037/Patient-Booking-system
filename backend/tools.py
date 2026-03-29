
import os
import datetime
from dotenv import load_dotenv
    
from langchain_core.tools import tool
import uuid

from backend.utils.gmail_service import send_calendar_invite
from .utils.database_handler import db_handler, DatabaseException
from textblob import TextBlob
from .utils.mongodb_connection import medical_records_collection 
import datetime


@tool
def resolve_user_identity(name_or_email: str) -> dict:
    """
    Smart resolver:
    - Detects 'Dr.' → doctor
    - Detects 'patient' → patient
    - Otherwise falls back to DB role

    Returns:
    {
        success: bool,
        role: str | None,
        patient_id: str | None,
        doctor_id: str | None
    }
    """

    identifier = name_or_email.lower().strip()

    # 🔥 Step 1: detect hints
    is_doctor_hint = "dr" in identifier or "doctor" in identifier
    is_patient_hint = "patient" in identifier

    # 🔥 Step 2: clean input (remove prefixes)
    cleaned_name = identifier.replace("dr.", "").replace("dr", "").replace("doctor", "").replace("patient", "").strip()

    query = """
    SELECT 
        u.email,
        u.role,
        p.id AS patient_id,
        d.id AS doctor_id
    FROM users u
    LEFT JOIN patients p ON u.email = p.user_email
    LEFT JOIN doctors d ON u.email = d.user_email
    WHERE u.full_name ILIKE %s OR u.email = %s
    LIMIT 1
    """

    params = (f"%{cleaned_name}%", name_or_email)
    result = db_handler.execute_query(query, params)

    if not result:
        return {
            "success": False,
            "role": None,
            "patient_id": None,
            "doctor_id": None,
            "message": "User not found"
        }

    row = result[0]
    # 🔥 Step 3: enforce hint-based resolution
    if is_doctor_hint:
        if row["doctor_id"]:
            return {
                "success": True,
                "role": "doctor",
                "doctor_id": row["doctor_id"],
                "patient_id": None
            }
        else:
            return {
                "success": False,
                "message": "User is not a doctor"
            }

    if is_patient_hint:
        if row["patient_id"]:
            return {
                "success": True,
                "role": "patient",
                "patient_id": row["patient_id"],
                "doctor_id": None
            }
        else:
            return {
                "success": False,
                "message": "User is not a patient"
            }

    # 🔥 Step 4: fallback to actual DB role
    return {
        "success": True,
        "role": row["role"],
        "patient_id": row["patient_id"],
        "doctor_id": row["doctor_id"]
    }


@tool 
def insert_update_doctor_availability(doctor_id: str, role: str, day_of_week: int, start_time: str, end_time: str, slot_duration_minutes: int) -> dict:
   
    """Insert or update doctor availability based on doctor_id and day_of_week and start_time in doctor_availability table

    Args:
        doctor_id: UUID of the doctor (as string)
        role: User role (should be 'doctor')
        day_of_week: Day of week (1=Monday, 0=Sunday)
        start_time: Start time as string (format: HH:MM:SS)
        end_time: End time as string (format: HH:MM:SS)
        slot_duration_minutes: Duration of appointment slots in minutes
    """
    if role == "doctor":
        #Insert or update doctor availability based on doctor_id and day_of_week and start_time
        query = """
        INSERT INTO doctor_availability (doctor_id, day_of_week, start_time, end_time, slot_duration_minutes)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (doctor_id, day_of_week, start_time) 
        DO UPDATE SET 
            end_time = EXCLUDED.end_time, 
            slot_duration_minutes = EXCLUDED.slot_duration_minutes
        RETURNING doctor_id, day_of_week, start_time, end_time, slot_duration_minutes
        """                     
        params = (
            doctor_id,
            day_of_week,
            start_time,
            end_time,
            slot_duration_minutes,
            )
        result = db_handler.execute_query(query, params)
        print("Doctor availability insert/update result:", result)
        if result:
            return {
                "success": True,
                "message": "Doctor availability inserted/updated successfully.",
                "availability": result[0],
            }
        else:
            return {
                "success": False,
                "message": "Failed to insert/update doctor availability.",
            }

@tool 
def insert_update_appointment_status(user_email:str, id:uuid.UUID, new_status: str, action: str, appointment_data: dict = None, role: str = None, updated_appointment_time: datetime = None) -> dict:
    """
    Add or cancel an appointment.

    Args:
        user_email: Email of the user with doctor_id
        id: ID of the appointment to update or cancel.
        new_status: New status (e.g., 'scheduled', 'completed', 'cancelled').
        action: Action to perform ('add', 'update_status', 'update_time').
        appointment_data: Dictionary containing details i.e (patient_id, doctor_id, name, appointment_at, duration_minutes, reason) required for adding new appointment. appointment_At should be in the format "YYYY-MM-DD HH:MM:SS"
        role: Role of the user performing the action (e.g., 'patient', 'doctor').
        updated_appointment_time: New appointment time for reschedulling
    Returns:
        Dictionary with success status and message.
    """
    try:
        db = db_handler
        load_dotenv()
        appointment_id = uuid.uuid4()
        if action == "add":
            if not appointment_data:
                return {
                    "success": False,
                    "message": "Appointment data is required for adding a new appointment."
                }
 
            query = """
            INSERT INTO appointments (id, patient_id, doctor_id, appointment_at, status,duration_minutes, reason, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            RETURNING id, patient_id, doctor_id, appointment_at, status;
            """
            params = (
                str(appointment_id),
                appointment_data["patient_id"],
                appointment_data["doctor_id"],
                appointment_data["appointment_at"],
                'pending',
                appointment_data.get("duration_minutes", 30),
                appointment_data.get("reason", ""),
            )
            result = db.execute_query(query, params)
 
            if result:  
                return {
                    "success": True,
                    "message": "New appointment added successfully.",
                    "appointment": result[0],
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to add new appointment.",
                }

        elif action == "update_status":
            query = """
            UPDATE appointments
            SET status = %s, updated_at = NOW()
            WHERE id = %s
            RETURNING id, patient_id, doctor_id, appointment_at, status, reason;
            """
            params = (new_status, id)
            result = db.execute_query(query, params)

            if result:
                updated_appointment = result[0]
                recipient_name = ""
                event_description = updated_appointment.get("reason", "")
                start_time = updated_appointment.get("appointment_at")

                if new_status == "cancelled":
                    if start_time:
                        send_calendar_invite(
                            app_id=str(id),
                            sender_email=os.getenv("GMAIL_SENDER_ADDRESS"),
                            sender_password=os.getenv("GMAIL_SENDER_PASSWORD"),
                            recipient_email=user_email,
                            recipient_name=recipient_name,
                            event_title="Doctor Appointment",
                            event_description=event_description,
                            start_time=start_time,
                            db_handler=db_handler,
                            method="CANCEL"
                        )
                elif new_status == "scheduled":
                    if start_time:
                        send_calendar_invite(
                            sender_email=os.getenv("GMAIL_SENDER_ADDRESS"),
                            sender_password=os.getenv("GMAIL_SENDER_PASSWORD"),
                            recipient_email=user_email,
                            recipient_name=recipient_name or "Patient",
                            event_title="Doctor Appointment",
                            event_description=event_description,
                            start_time=start_time,
                            app_id=str(id),
                            db_handler=db_handler,
                            method="REQUEST"
                        )
                    pass
                return {
                    "success": True,
                    "message": f"Appointment {id} updated successfully.",
                    "updated_appointment": updated_appointment,
                }
            else:
                return {
                    "success": False,
                    "message": f"No appointment found with ID {id}",
                }
        elif action == "update_time":
            if role == "patient":
                 return {
                    "success": False,
                    "message": f"Cannot update appointment time. Only doctors can update appointment time.",
                }
            

            query = """
            UPDATE appointments
            SET appointment_at = %s, updated_at = NOW()
            WHERE id = %s
            RETURNING id, patient_id, doctor_id, appointment_at, status;
            """

            params = (updated_appointment_time, id)
            result = db.execute_query(query, params)

            if result:
                details = appointment_data or {}
                # Send calendar update invite
                send_calendar_invite(
                        sender_email=os.getenv("GMAIL_SENDER_ADDRESS"),
                        sender_password=os.getenv("GMAIL_SENDER_PASSWORD"),
                        recipient_email="radhe.muskan26@gmail.com",
                        recipient_name=details.get("name", "Patient"),
                        event_title="Doctor Appointment Rescheduled",
                        event_description=details.get("reason", ""),
                        start_time=updated_appointment_time,
                        app_id=str(id),
                        db_handler=db_handler,
                        method="UPDATE"
                    )

                return {
                    "success": True,
                    "message": f"Appointment {id} updated successfully.",
                    "updated_appointment": result[0],
                }
            else:
                return {
                    "success": False,
                    "message": f"No appointment found with ID {id}",
                }

        else:
            return {
                "success": False,
                "message": "Invalid action specified. Use 'add', 'update', or 'cancel'."
            }

    except Exception as e:
        return {
            "success": False,
            "message": f"An error occurred: {str(e)}",
        }
    

@tool
def execute_sql_query(query: str) -> dict:
    """
    Execute a SELECT query against the hospital database.
    
    Tables available:
    - users: email, full_name, role, phone, is_active, created_at
    - doctors: id, user_email, specialty, qualification, consultation_fee
    - patients: id, user_email, date_of_birth, blood_group, allergies
    - nurses: id, user_email, department
    - doctor_availability: id, doctor_id, day_of_week, start_time, end_time
    - appointments: id, patient_id, doctor_id, appointment_at, duration_minutes, status, reason
    - chat_messages: id, user_id, role, content, created_at
    - feedback: id, appointment_id, patient_email, doctor_id, raw_feedback, ai_rating
    

    Args:
        query: SELECT query string
    
    Returns:
        Dictionary with success status and data
    """
    try:
        db = db_handler
        result = db.execute_query(query)
        print("Query Result:", query)
        for row in result:
            print(row)

        return {
            "success": True,
            "row_count": len(result),
            "data": result,
        }
    except DatabaseException as e:
        return {
            "success": False,
            "error": f"Database error: {str(e)}",
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to execute query: {str(e)}",
        }

@tool
def insert_medical_record(full_name: str, role: str, patient_id: str, doctor_id: str, appointment_id: str, symptoms: list = None, diagnosis: str = None, prescriptions: list = None, tests: list = None, doctor_notes: str = None, vitals: dict = None, follow_up_date: str = None) -> dict:
    """
    Insert a medical record from a doctor's appointment with patient.
    
    Args:
        full_name: Full name of the patient
        role: Role of the user ( 'doctor')
        patient_id: UUID of the patient
        doctor_id: UUID of the doctor
        appointment_id: UUID of the appointment
        symptoms: List of symptoms reported by patient
        diagnosis: Clinical diagnosis provided by doctor
        prescriptions: List of prescribed medications
        tests: List of recommended lab tests
        doctor_notes: Additional notes from doctor
        vitals: Dictionary of vital signs (e.g., {"blood_pressure": "120/80", "heart_rate": 72})
        follow_up_date: ISO format date string for follow-up appointment
    
    Returns:
        Dictionary with success status and created record ID
    """
    try:
        # if role != "doctor":
        #     return {
        #         "success": False,
        #         "message": "Only doctors can insert medical records."
        #     }
        # Validate required fields
        if not all([patient_id, doctor_id, appointment_id, diagnosis]):
            return {
                "success": False,
                "message": "Missing required fields: patient_id, doctor_id, appointment_id, diagnosis"
            }
        
        # Create medical record document
        medical_record = {
            "patient_id": patient_id,
            "doctor_id": doctor_id,
            "full Name": full_name,
            "appointment_id": appointment_id,
            "date": datetime.datetime.utcnow(),
            "symptoms": symptoms if isinstance(symptoms, list) else [],
            "diagnosis": diagnosis,
            "prescriptions": prescriptions if isinstance(prescriptions, list) else [],
            "tests": tests if isinstance(tests, list) else [],
            "doctor_notes": doctor_notes,
            "vitals": vitals if isinstance(vitals, dict) else {},
            "follow_up_date": follow_up_date,
            "created_at": datetime.datetime.utcnow()
        }
        
        # Insert into MongoDB
        result = medical_records_collection.insert_one(medical_record)
        
        return {
            "success": True,
            "message": "Medical record inserted successfully.",
            "record_id": str(result.inserted_id),
            "patient_id": patient_id,
            "created_at": medical_record["created_at"].isoformat()
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to insert medical record: {str(e)}",
            "error": str(e)
        }

@tool
def retrieve_medical_records(patient_id: str, doctor_id: str = None, appointment_id: str = None, limit: int = 10) -> dict:
    """
    Retrieve medical records from MongoDB.
    
    Args:
        patient_id: UUID of patient (optional - retrieve all records for patient)
        doctor_id: UUID of doctor (optional - retrieve all records created by doctor)
        appointment_id: UUID of appointment (optional - retrieve record for specific appointment)
    
    Returns:
        Dictionary with success status and list of medical records
    """
    try:
        query_filter = {}
        
        if patient_id:
            query_filter["patient_id"] = patient_id
        if doctor_id:
            query_filter["doctor_id"] = doctor_id
        if appointment_id:
            query_filter["appointment_id"] = appointment_id
        
        # if not patient_id:
        #     return {
        #         "success": False,
        #         "message": "At least one filter parameter (patient_id, doctor_id, or appointment_id) is required"
        #     }
        
        # Query MongoDB
        records = list(medical_records_collection.find(query_filter).sort("created_at", -1).limit(limit))
        
        # Convert ObjectId to string for serialization
        for record in records:
            record["_id"] = str(record["_id"])
            record["date"] = record["date"].isoformat() if isinstance(record["date"], datetime.datetime) else record["date"]
            record["created_at"] = record["created_at"].isoformat() if isinstance(record["created_at"], datetime.datetime) else record["created_at"]
        
        return {
            "success": True,
            "record_count": len(records),
            "records": records
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to retrieve medical records: {str(e)}",
            "error": str(e)
        }
    

# Function to calculate rating from user message
def calculate_rating_from_message(message):
    analysis = TextBlob(message)
    sentiment = analysis.sentiment.polarity

    # Map sentiment polarity to a rating between 1 and 5
    if sentiment <= -0.5:
        return 1
    elif -0.5 < sentiment <= 0:
        return 2
    elif 0 < sentiment <= 0.5:
        return 4
    else:
        return 5

@tool
# Function to insert feedback into the feedback table
def insert_feedback(patient_id, doctor_id, message):
    """
    Insert feedback into the feedback table.
    - schema feedback: id, appointment_id, patient_email, doctor_id, ai_rating, raw_feedback
    If the patient_id is not know it can be found out using user_email
    Args:
        patient_id (str): The ID of the patient providing the feedback.
        doctor_id (str): The ID of the doctor receiving the feedback.
        message (str): The raw feedback message from the patient.

    Returns:
        str: A confirmation message indicating the feedback was inserted.
    """
    rating = calculate_rating_from_message(message)
    
    id = uuid.uuid4()  # Generate a unique ID for the feedback entry
    query = """
    INSERT INTO feedback (id, patient_id, doctor_id, raw_feedback, ai_rating, created_at)
    VALUES (%s, %s, %s, %s, %s, NOW());
    """

    params = (id, patient_id, doctor_id, message, rating)
    db_handler.execute_query(query, params)

    return f"Feedback inserted with rating {rating}"
