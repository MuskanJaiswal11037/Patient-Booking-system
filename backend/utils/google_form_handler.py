"""
Google Form Submission Handler - Processes Google Form responses and syncs with database.

Workflow:
1. Fetch submissions from Google Sheets
2. Check if user exists by email
3. If not, create user → patient, then create appointment
4. If exists, create appointment for existing user
5. Track processed submissions to avoid duplicates
"""

import requests
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path
import os
from dotenv import load_dotenv
from google.oauth2.service_account import Credentials
import gspread
from backend.utils.gmail_service import send_calendar_invite, send_confirmation_email
from backend.utils.database_handler import db_handler, DatabaseException
import hashlib

logger = logging.getLogger(__name__)
load_dotenv()

SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
# Google Sheets configuration
SHEET_ID = os.getenv("SHEET_ID")
CREDENTIALS_PATH = Path(__file__).parent / "credentials.json"

def fetch_google_form_submissions() -> List[Dict[str, Any]]:
    """
    Fetch all submissions from Google Sheets connected to Google Form.
    
    Returns:
        List of submission dictionaries (JSON format) with form responses
        Format: [
            {
                "Name": "John Doe",
                "Email": "john@example.com",
                "Phone number": "9876543210",
                "Doctor's name": "Dr. Smith",
                "Appointment Date": "2026-04-10",
                "Time": "10:00 AM",
                "Reason": "Checkup"
            },
            ...
        ]
    """
    try:
        creds = Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=SCOPES)
        client = gspread.authorize(creds)
        
        # Open your sheet by ID
        sheet = client.open_by_key(os.getenv("SHEET_ID")).sheet1

        # Get all form responses as list of dictionaries (JSON format)
        submissions = sheet.get_all_records()
        
        if not submissions:
            logger.warning("No data found in Google Sheet")
            return []
        
        logger.info(f"Fetched {len(submissions)} submissions from Google Sheets")
        return submissions
        
    except Exception as e:
        logger.error(f"Error fetching Google Sheets data: {e}")
        return []


def check_user_exists(email: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Check if user with given email exists.
    
    Args:
        email: User email to check
    
    Returns:
        Tuple of (exists: bool, user_data: dict or None)
    """
    try:
        query = """
        SELECT email, full_name, phone, role, is_active 
        FROM users 
        WHERE email = %s
        """
        result = db_handler.execute_query(query, (email,))
        
        if result:
            return True, result[0]
        return False, None
    
    except DatabaseException as e:
        logger.error(f"Error checking user existence: {e}")
        return False, None


def get_doctor_by_name(doctor_name: str) -> Optional[Dict[str, Any]]:
    """
    Get doctor ID by name.
    
    Args:
        doctor_name: Doctor's full name
    
    Returns:
        Dictionary with doctor data or None
    """
    try:
        partial_query = """
        SELECT d.id, d.user_email, u.full_name, d.specialty
        FROM doctors d
        JOIN users u ON d.user_email = u.email
        WHERE LOWER(u.full_name) LIKE LOWER(%s)
        ORDER BY u.full_name, d.id
        LIMIT 1
        """
        result = db_handler.execute_query(partial_query, (f"%{doctor_name}%",))
        
        if result:
            logger.info(f"Found doctor by partial match: {doctor_name} -> {result[0]['full_name']}")
            return result[0]
        
        logger.warning(f"Doctor not found: {doctor_name}")
        return None
    
    except DatabaseException as e:
        logger.error(f"Error getting doctor: {e}")
        return None


def create_new_user_and_patient(email: str, name: str, phone: str) -> Optional[Dict[str, Any]]:
    """
    Create new user and patient records.
    
    Args:
        email: User email
        name: Full name
        phone: Phone number
    
    Returns:
        Dictionary with created user/patient data or None
    """
    try:
        # Create user
        user_query = """
        INSERT INTO users (email, full_name, role, phone, is_active)
        VALUES (%s, %s, %s, %s, TRUE)
        ON CONFLICT (email) DO NOTHING
        RETURNING email, full_name, role
        """
        user_result = db_handler.execute_query(user_query, (email, name, 'patient', phone))
        
        if not user_result:
            logger.warning(f"User creation failed or already exists: {email}")
            return None
        
        # Create patient profile
        patient_query = """
        INSERT INTO patients (user_email)
        VALUES (%s)
        RETURNING id, user_email
        """
        patient_result = db_handler.execute_query(patient_query, (email,))
        
        if patient_result:
            logger.info(f"Created new user and patient: {email}")
            return {
                "email": email,
                "patient_id": str(patient_result[0]['id']),
                "full_name": name,
                "phone": phone
            }
        
        return None
    
    except DatabaseException as e:
        logger.error(f"Error creating user/patient: {e}")
        return None


def create_appointment(patient_id: str, doctor_id: str, appointment_date: str, 
                     appointment_time: str, reason: str, user_email:str, doctor_email:str) -> Optional[Dict[str, Any]]:
    """
    Create appointment for patient.
    
    Args:
        patient_id: UUID of patient
        doctor_id: UUID of doctor
        appointment_date: Date in DD/MM/YYYY format (from Google Form)
        appointment_time: Time in HH:MM or HH:MM:SS format
        reason: Appointment reason
    
    Returns:
        Dictionary with appointment data or None
    """
    try:
        # Parse date from DD/MM/YYYY to YYYY-MM-DD
        date_obj = datetime.strptime(appointment_date, "%d/%m/%Y")
        formatted_date = date_obj.strftime("%Y-%m-%d")
        
        # Handle time format - check if it already has seconds
        time_parts = appointment_time.split(":")
        if len(time_parts) == 2:
            # Format is HH:MM, add seconds
            formatted_time = f"{appointment_time}:00"
        else:
            # Format is HH:MM:SS already
            formatted_time = appointment_time
        
        # Combine date and time into ISO format (YYYY-MM-DDTHH:MM:SS)
        datetime_str = f"{formatted_date}T{formatted_time}"
        
        appointment_query = """
        INSERT INTO appointments (patient_id, doctor_id, appointment_at, status, reason, duration_minutes)
        VALUES (%s, %s, %s, 'scheduled', %s, 15)
        RETURNING id, patient_id, doctor_id, appointment_at, status, reason
        """
        
        result = db_handler.execute_query(appointment_query, (patient_id, doctor_id, datetime_str, reason))
        
        if result:
            logger.info(f"Created appointment: {result[0]['id']}")
            # Send confirmation email
            send_confirmation_email(
                        sender_email=os.getenv("GMAIL_SENDER_ADDRESS"),     
                        sender_password=os.getenv("GMAIL_SENDER_PASSWORD"),
                        recipient_email=user_email,
                        recipient_name="Patient",
                        subject="Appointment Confirmation",
                        status="CONFIRMED"
                    )  
            id =  result[0]['id']
            send_calendar_invite(
                        sender_email=os.getenv("GMAIL_SENDER_ADDRESS"),
                        sender_password=os.getenv("GMAIL_SENDER_PASSWORD"),
                        recipient_email=doctor_email,
                        recipient_name=result[0].get("name", "Patient"),
                        event_title="Doctor Appointment Scheduled",
                        event_description=reason,
                        start_time=datetime_str,
                        app_id=str(id),
                        db_handler=db_handler,
                        method="REQUEST"
                    )
            return result[0]
        
        return None
    
    except ValueError as e:  
        logger.error(f"Error parsing appointment date/time: {e}")
        return None
    except DatabaseException as e:
        send_confirmation_email(
                        sender_email=os.getenv("GMAIL_SENDER_ADDRESS"),     
                        sender_password=os.getenv("GMAIL_SENDER_PASSWORD"),
                        recipient_email=user_email,
                        recipient_name="Patient",
                        subject="Appointment Creation Failed",
                        status="FAILED"
                    )   
        logger.error(f"Error creating appointment: {e}")
        return None


def get_patient_id_by_email(email: str) -> Optional[str]:
    """
    Get patient ID by user email.
    
    Args:
        email: User email
    
    Returns:
        Patient UUID or None
    """
    try:
        query = """
        SELECT id FROM patients WHERE user_email = %s
        """
        result = db_handler.execute_query(query, (email,))
        
        if result:
            return str(result[0]['id'])
        return None
    
    except DatabaseException as e:
        logger.error(f"Error getting patient ID: {e}")
        return None


def create_submission_hash(email: str, appointment_date: str, appointment_time: str) -> str:
    """
    Create unique hash for a submission to prevent duplicates.
    
    Args:
        email: User email
        appointment_date: Appointment date
        appointment_time: Appointment time
    
    Returns:
        SHA256 hash of submission
    """
    submission_str = f"{email}|{appointment_date}|{appointment_time}"
    return hashlib.sha256(submission_str.encode()).hexdigest()


def check_submission_processed(submission_hash: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
    """
    Check if a submission has already been processed.
    
    Args:
        submission_hash: Hash of the submission
    
    Returns:
        Tuple of (processed: bool, submission_data: dict or None)
    """
    try:
        query = """
        SELECT id, email, appointment_id, processed_at
        FROM google_form_submissions_log
        WHERE submission_hash = %s
        """
        result = db_handler.execute_query(query, (submission_hash,))
        
        if result:
            return True, result[0]
        return False, None
    
    except DatabaseException as e:
        logger.error(f"Error checking submission: {e}")
        return False, None


def log_submission(email: str, appointment_date: str, appointment_time: str, 
                  submission_hash: str, appointment_id: str = None, 
                  error_message: str = None) -> bool:
    """
    Log a processed (or failed) submission to prevent reprocessing.
    
    Args:
        email: User email
        appointment_date: Appointment date
        appointment_time: Appointment time
        submission_hash: Hash of the submission
        appointment_id: Created appointment ID (if successful)
        error_message: Error message (if failed)
    
    Returns:
        True if logged successfully, False otherwise
    """
    try:
        query = """
        INSERT INTO google_form_submissions_log 
        (email, appointment_date, appointment_time, submission_hash, appointment_id, error_message, processed)
        VALUES (%s, %s, %s, %s, %s, %s, TRUE)
        ON CONFLICT (submission_hash) DO NOTHING
        """
        db_handler.execute_query(query, (email, appointment_date, appointment_time, submission_hash, appointment_id, error_message))
        logger.info(f"Logged submission: {email} on {appointment_date}")
        return True
    
    except DatabaseException as e:
        logger.error(f"Error logging submission: {e}")
        return False


def process_google_form_submission(submission: Dict[str, Any]) -> Dict[str, Any]:
    """
    Process a single Google Form submission.
    
    Workflow:
    1. Extract form fields
    2. Create submission hash
    3. Check if already processed (deduplication)
    4. If not: Check if user exists
    5. If not: Create user & patient
    6. Get doctor info
    7. Create appointment
    8. Log submission
    
    Args:
        submission: Dictionary with form data
    
    Returns:
        Processing result dictionary
    """
    
    # Extract form fields (adjust column names based on your Google Form)
    email = submission.get("Email", "").strip()
    name = submission.get("Name", "").strip()
    phone = submission.get("Phone number", "")
    doctor_name = submission.get("Doctor's Name", "").strip()
    appointment_date = submission.get("Appointment Date", "").strip()
    appointment_time = submission.get("Time", "").strip()
    reason = submission.get("Reason", "").strip()
    
    logger.info(f"Processing submission - Email: {email}, Doctor Name: '{doctor_name}'")
    print(f"Processing submission - Email: {email}, Doctor Name: '{doctor_name}'")
    
    try:
        # Step 1: Create submission hash to check for duplicates
        submission_hash = create_submission_hash(email, appointment_date, appointment_time)
        
        # Step 2: Check if this submission was already processed
        already_processed, existing_data = check_submission_processed(submission_hash)
        
        if already_processed:
            logger.warning(f"Submission already processed: {email} on {appointment_date} at {appointment_time}")
            return {
                "success": False,
                "skip": True,
                "message": "This submission was already processed",
                "email": email,
                "appointment_id": existing_data.get("appointment_id") if existing_data else None
            }
        
        # Step 3: Check if user exists
        user_exists, user_data = check_user_exists(email)
        
        if user_exists:
            logger.info(f"User exists: {email}")
            patient_id = get_patient_id_by_email(email)
        else:
            logger.info(f"Creating new user: {email}")
            user_data = create_new_user_and_patient(email, name, phone)
            
            if not user_data:
                error_msg = "Failed to create user and patient"
                log_submission(email, appointment_date, appointment_time, submission_hash, error_message=error_msg)
                return {
                    "success": False,
                    "error": error_msg,
                    "email": email
                }
            
            patient_id = user_data.get("patient_id")
        
        if not patient_id:
            error_msg = "Could not get patient ID"
            log_submission(email, appointment_date, appointment_time, submission_hash, error_message=error_msg)
            return {
                "success": False,
                "error": error_msg,
                "email": email
            }
        
        # Step 4: Get doctor info
        doctor_info = get_doctor_by_name(doctor_name)
        
        if not doctor_info:
            error_msg = f"Doctor not found: {doctor_name}"
            log_submission(email, appointment_date, appointment_time, submission_hash, error_message=error_msg)
            return {
                "success": False,
                "error": error_msg,
                "email": email
            }
        
        doctor_id = doctor_info.get("id")
        doctor_email = doctor_info.get("user_email")
        
        # Step 5: Create appointment
        appointment = create_appointment(patient_id, doctor_id, appointment_date, appointment_time, reason, user_email=email, doctor_email=doctor_email)
        
        if appointment:
            appointment_id = str(appointment.get("id"))
            # Log successful processing
            log_submission(email, appointment_date, appointment_time, submission_hash, appointment_id=appointment_id)
            
            return {
                "success": True,
                "message": "Appointment created successfully",
                "email": email,
                "appointment_id": appointment_id,
                "patient_id": patient_id,
                "doctor_id": doctor_id,
                "appointment_date": appointment_date,
                "appointment_time": appointment_time
            }
        else:
            error_msg = "Failed to create appointment"
            log_submission(email, appointment_date, appointment_time, submission_hash, error_message=error_msg)
            return {
                "success": False,
                "error": error_msg,
                "email": email
            }
    
    except Exception as e:
        logger.error(f"Error processing submission for {email}: {e}")
        try:
            submission_hash = create_submission_hash(email, appointment_date, appointment_time)
            log_submission(email, appointment_date, appointment_time, submission_hash, error_message=str(e))
        except:
            pass
        return {
            "success": False,
            "error": str(e),
            "email": email
        }


def sync_google_form_submissions() -> Dict[str, Any]:
    """
    Main function to sync all Google Form submissions to database.
    Only processes NEW submissions (skips duplicates).
    
    Returns:
        Summary of processing results
    """
    logger.info("Starting Google Form sync...")
    
    submissions = fetch_google_form_submissions()
    
    if not submissions:
        return {
            "success": False,
            "message": "No submissions found",
            "processed": 0,
            "successful": 0,
            "skipped": 0,
            "failed": 0
        }
    
    successful = 0
    skipped = 0
    failed = 0
    errors = []
    
    for submission in submissions:
        result = process_google_form_submission(submission)
        print(result)
        
        if result.get("success"):
            successful += 1
            logger.info(f"✅ Processed: {result.get('email')}")
        elif result.get("skip"):
            skipped += 1
            logger.info(f"⏭️ Skipped (duplicate): {result.get('email')}")
        else:
            failed += 1
            errors.append({
                "email": result.get("email"),
                "error": result.get("error")
            })
            logger.error(f"❌ Failed: {result.get('email')} - {result.get('error')}")
    
    logger.info(f"Sync complete: {successful} new, {skipped} skipped (duplicates), {failed} failed")
    
    return {
        "success": True,
        "message": "Google Form sync completed",
        "total_submissions": len(submissions),
        "successful": successful,
        "skipped_duplicates": skipped,
        "failed": failed,
        "errors": errors
    }

if __name__ == "__main__":
    response = sync_google_form_submissions()
    print(response)
