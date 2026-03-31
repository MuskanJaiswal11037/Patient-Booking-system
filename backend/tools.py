
import os
import datetime
from dotenv import load_dotenv
    
from langchain_core.tools import tool
import uuid

from backend.utils.gmail_service import send_calendar_invite, send_confirmation_email
from .utils.database_handler import db_handler, DatabaseException
from textblob import TextBlob
from .utils.mongodb_connection import medical_records_collection 
from .utils.drive_service import upload_medical_record_to_drive
import datetime


@tool
def resolve_user_identity(full_name: str = None, email: str = None) -> dict:
    """
    Smart resolver to find user details by name or email.
    
    Args:
        full_name: Full name/name  of the user (supports 'Dr.', 'Doctor','patient' prefixes for doctors) or the user who has logged in.
        email: Email address of the user
    
    Detects:
    - 'Dr.' or 'Doctor' prefix → doctor
    - 'patient' keyword → patient
    - Otherwise falls back to DB role

    Returns:
    {
        success: bool,
        role: str | None,
        patient_id: str | None,
        doctor_id: str | None,
        email: str,
        full_name: str
    }
    """

    try:
        # 🔥 Step 1: Validate inputs
        if not full_name and not email:
            return {
                "success": False,
                "role": None,
                "patient_id": None,
                "doctor_id": None,
                "message": "Either full_name or email is required"
            }

        # 🔥 Step 2: Try exact email match first
        if email:
            query = """
            SELECT 
                u.email,
                u.role,
                u.full_name,
                p.id AS patient_id,
                d.id AS doctor_id
            FROM users u
            LEFT JOIN patients p ON u.email = p.user_email
            LEFT JOIN doctors d ON u.email = d.user_email
            WHERE u.email = %s 
            LIMIT 1
            """
            result = db_handler.execute_query(query, (email,))
            if result:
                row = result[0]
                return {
                    "success": True,
                    "role": row["role"],
                    "patient_id": row["patient_id"],
                    "doctor_id": row["doctor_id"],
                    "email": row["email"],
                    "full_name": row["full_name"]
                }

        # 🔥 Step 3: Search by full_name with hint detection
        if full_name:
            identifier = full_name.lower().strip()

            # Detect role hints
            is_doctor_hint = "dr" in identifier or "doctor" in identifier
            is_patient_hint = "patient" in identifier

            # Clean input (remove prefixes)
            cleaned_name = identifier.replace("dr.", "").replace("dr", "").replace("doctor", "").replace("patient", "").strip()

            query = """
            SELECT 
                u.email,
                u.role,
                u.full_name,
                p.id AS patient_id,
                d.id AS doctor_id
            FROM users u
            LEFT JOIN patients p ON u.email = p.user_email
            LEFT JOIN doctors d ON u.email = d.user_email
            WHERE u.full_name ILIKE %s 
            LIMIT 1
            """

            params = (f"%{cleaned_name}%",)
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
            
            # 🔥 Step 4: Enforce hint-based resolution
            if is_doctor_hint:
                if row["doctor_id"]:
                    return {
                        "success": True,
                        "role": "doctor",
                        "doctor_id": row["doctor_id"],
                        "patient_id": None,
                        "email": row["email"],
                        "full_name": row["full_name"]
                    }
                else:
                    return {
                        "success": False,
                        "role": None,
                        "patient_id": None,
                        "doctor_id": None,
                        "message": "User is not a doctor"
                    }

            if is_patient_hint:
                if row["patient_id"]:
                    return {
                        "success": True,
                        "role": "patient",
                        "patient_id": row["patient_id"],
                        "doctor_id": None,
                        "email": row["email"],
                        "full_name": row["full_name"]
                    }
                else:
                    return {
                        "success": False,
                        "role": None,
                        "patient_id": None,
                        "doctor_id": None,
                        "message": "User is not a patient"
                    }

            # 🔥 Step 5: Fallback to actual DB role
            return {
                "success": True,
                "role": row["role"],
                "patient_id": row["patient_id"],
                "doctor_id": row["doctor_id"],
                "email": row["email"],
                "full_name": row["full_name"]
            }

    except Exception as e:
        return {
            "success": False,
            "role": None,
            "patient_id": None,
            "doctor_id": None,
            "message": f"Error resolving user identity: {str(e)}"
        }

    


@tool 
def insert_update_doctor_availability(doctor_id: str, role: str, day_of_week: int, start_time: str, end_time: str, slot_duration_minutes = 15) -> dict:
   
    """Insert or update doctor availability based on doctor_id and day_of_week and start_time in doctor_availability table

    Args:
        doctor_id: UUID of the doctor (as string)
        role: User role (should be 'doctor')
        day_of_week: Day of week (1=Monday, 0=Sunday)
        start_time: Start time as string (format: HH:MM:SS)
        end_time: End time as string (format: HH:MM:SS)
        slot_duration_minutes: Duration of appointment slots in minutes (default: 15)
        slot_duration_minutes: Duration of appointment slots in minutes (default: 15)
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
    Add or cancel an appointment. If u want to cancel the appointment then new sttus should be cancelled.

    Args:
        user_email: Email of the user who is patient
        id: ID of the appointment to update or cancel.
        new_status: New status (e.g., 'scheduled', 'completed', 'cancelled').
        action: Action to perform ('add', 'update_status', 'update_time').
        appointment_data: Dictionary containing details i.e (patient_id, doctor_id, name, appointment_at, duration_minutes, reason) required for adding new appointment or cancelling the appointment. appointment_at should be in the format "YYYY-MM-DD HH:MM:SS"
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
            
            query ="select user_email from doctors where id = %s"
            doctor_result = db.execute_query(query, (appointment_data["doctor_id"],))
            if doctor_result:
                doctor_email = doctor_result[0].get("user_email", "")
            
            if  appointment_data["appointment_at"] < str(datetime.datetime.now()):
                return {
                    "success": False,
                    "message": "Appointment time must be in the future."
                }
             # Insert new appointment
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
                'scheduled',
                appointment_data.get("duration_minutes", 15),
                'scheduled',
                appointment_data.get("duration_minutes", 15),
                appointment_data.get("reason", ""),
            )
            result = db.execute_query(query, params)
 
            if result:  
                # Send confirmation email
                send_confirmation_email(
                        sender_email=os.getenv("GMAIL_SENDER_ADDRESS"),     
                        sender_password=os.getenv("GMAIL_SENDER_PASSWORD"),
                        recipient_email=user_email,
                        recipient_name=appointment_data.get("name", "Patient"),
                        subject="Appointment Confirmation",
                        status="CONFIRMED"
                    )   
                send_calendar_invite(
                        sender_email=os.getenv("GMAIL_SENDER_ADDRESS"),
                        sender_password=os.getenv("GMAIL_SENDER_PASSWORD"),
                        recipient_email=doctor_email,
                        recipient_name=result[0].get("name", "Patient"),
                        event_title="Doctor Appointment Scheduled",
                        event_description=result[0].get("reason", ""),
                        start_time=appointment_data["appointment_at"],
                        app_id=str(id),
                        db_handler=db_handler,
                        method="REQUEST"
                    )
                
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
                event_description = updated_appointment.get("reason", "")
                start_time = updated_appointment.get("appointment_at")

                query ="select user_email from doctors where  id= %s"
                doctor_result = db.execute_query(query, (updated_appointment["doctor_id"],))
                if doctor_result:
                    doctor_email = doctor_result[0].get("user_email", "")

                if new_status == "cancelled" and doctor_result:
                    send_confirmation_email(
                        sender_email=os.getenv("GMAIL_SENDER_ADDRESS"),     
                        sender_password=os.getenv("GMAIL_SENDER_PASSWORD"),
                        recipient_email=user_email,
                        recipient_name= "",
                        subject="Appointment Cancellation",
                        status="CANCELLED"
                    )   
                    send_calendar_invite(
                            app_id=str(id),
                            sender_email=os.getenv("GMAIL_SENDER_ADDRESS"),
                            sender_password=os.getenv("GMAIL_SENDER_PASSWORD"),
                            recipient_email=doctor_email,
                            recipient_name=doctor_result[0].get("full_name", ""),
                            event_title="Doctor Appointment",
                            event_description=event_description,
                            start_time=start_time,
                            db_handler=db_handler,
                            method="CANCEL"
                        )
                    
                    return {
                    "success": True,
                    "message": "Appointment cancelled successfully",
                    "appointment": result[0],
                }
                        
            else:
                return {
                    "success": False,
                    "message": f"No appointment found with ID {id}",
                }
        elif action == "update_time":
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
                send_confirmation_email(
                        sender_email=os.getenv("GMAIL_SENDER_ADDRESS"),     
                        sender_password=os.getenv("GMAIL_SENDER_PASSWORD"),
                        recipient_email=user_email,
                        recipient_name=appointment_data.get("name", "Patient"),
                        subject="Appointment Rescheduled",
                        status="RESCHEDULED"
                )
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
def insert_medical_record(full_name: str, role: str, patient_id: str, doctor_id: str, appointment_id: str, symptoms: list = None, diagnosis: str = None, prescriptions: list = None, tests: list = None, doctor_notes: str = None, vitals: dict = None, follow_up_date: str = None, upload_to_drive: bool = True) -> dict:
    """
    Insert a medical record from a doctor's appointment with patient and optionally upload to Google Drive as PDF.
    
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
        upload_to_drive: Boolean flag to upload PDF to Google Drive (default: True)
    
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
        response = {
            "success": True,
            "message": "Medical record inserted successfully.",
            "record_id": str(result.inserted_id),
            "patient_id": patient_id,
            "created_at": medical_record["created_at"].isoformat()
        }
        
        # Optionally upload to Google Drive
        if upload_to_drive:
            print("📁 Uploading medical record to Google Drive...")
            drive_result = upload_medical_record_to_drive(medical_record, patient_id, doctor_id)
            
            if drive_result["success"]:
                response["drive_upload"] = {
                    "success": True,
                    "file_id": drive_result.get("file_id"),
                    "file_url": drive_result.get("file_url"),
                    "folder_id": drive_result.get("folder_id"),
                    "file_name": drive_result.get("file_name"),
                    "message": drive_result.get("message")
                }
                print(f"✅ Medical record uploaded to Drive: {drive_result.get('file_url')}")
            else:
                response["drive_upload"] = {
                    "success": False,
                    "message": drive_result.get("message", "Failed to upload to Google Drive"),
                    "error": "Google Drive upload failed but medical record was saved to MongoDB"
                }
                print(f"⚠️ Drive upload failed: {drive_result.get('message')}")
        
        return response
    
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
