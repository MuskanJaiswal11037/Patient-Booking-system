"""
Google Drive Service for uploading medical records as PDFs
Uses Gmail credentials and Google Drive API
"""

import os
import io
import json
from datetime import datetime
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.api_core.exceptions import GoogleAPIError
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors


# Google Drive API scope
SCOPES = ['https://www.googleapis.com/auth/drive.file']


def get_drive_service():
    """
    Get Google Drive service using environment variables for authentication.
    
    Supports:
    1. Service account credentials from GOOGLE_SERVICE_ACCOUNT_JSON env variable
    2. OAuth token from token.json file (if previously saved)
    3. Falls back to installed app flow with client_secret.json if available
    
    Returns:
        googleapiclient.discovery.Resource: Google Drive API service
    """
    try:
        creds = None
        
        # 🔥 Step 1: Try service account credentials from environment variable
        service_account_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
        if service_account_json:
            try:
                service_account_info = json.loads(service_account_json)
                creds = service_account.Credentials.from_service_account_info(
                    service_account_info, scopes=SCOPES)
                print("✅ Authenticated using service account credentials from environment")
                service = build('drive', 'v3', credentials=creds)
                return service
            except Exception as e:
                print(f"⚠️ Service account authentication failed: {str(e)}")
        
        # 🔥 Step 2: Try to load previously saved OAuth token
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            if creds and creds.valid:
                print("✅ Authenticated using saved token.json")
                service = build('drive', 'v3', credentials=creds)
                return service
        
        # # 🔥 Step 3: Try client_secret.json (configured in frontend folder)
        # client_secret_path = 'frontend/client_secret.json'
        # if os.path.exists(client_secret_path):
        #     flow = InstalledAppFlow.from_client_secrets_file(
        #         client_secret_path, SCOPES)
        #     creds = flow.run_local_server(port=0)
            
        #     # Save credentials for future use
        #     with open('token.json', 'w') as token:
        #         token.write(creds.to_json())
            
        #     print("✅ Authenticated using client_secret.json OAuth flow")
        #     service = build('drive', 'v3', credentials=creds)
        #     return service
        
        print("❌ No authentication method available")
        return None
    
    except Exception as e:
        print(f"❌ Error initializing Google Drive service: {str(e)}")
        return None


def create_medical_record_pdf(medical_record: dict) -> io.BytesIO:
    """
    Generate PDF from medical record data
    
    Args:
        medical_record: Dictionary containing medical record details
    
    Returns:
        io.BytesIO: PDF content as bytes
    """
    try:
        pdf_buffer = io.BytesIO()
        doc = SimpleDocTemplate(pdf_buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title style
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        
        # Heading style
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#1f4788'),
            spaceAfter=12,
            spaceBefore=12
        )
        
        # Add title
        elements.append(Paragraph("Medical Record Report", title_style))
        elements.append(Spacer(1, 0.2*inch))
        
        # Patient Information Section
        elements.append(Paragraph("Patient Information", heading_style))
        patient_data = [
            ['Field', 'Details'],
            ['Patient Name', medical_record.get('full Name', 'N/A')],
            ['Patient ID', medical_record.get('patient_id', 'N/A')],
            ['Date', medical_record.get('date', datetime.utcnow()).strftime("%Y-%m-%d %H:%M:%S") if isinstance(medical_record.get('date'), datetime) else medical_record.get('date', 'N/A')],
        ]
        
        patient_table = Table(patient_data, colWidths=[2*inch, 4*inch])
        patient_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
        ]))
        elements.append(patient_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Clinical Information Section
        elements.append(Paragraph("Clinical Information", heading_style))
        
        # Symptoms
        if medical_record.get('symptoms'):
            elements.append(Paragraph("<b>Symptoms:</b>", styles['Normal']))
            symptoms_text = ", ".join(medical_record.get('symptoms', []))
            elements.append(Paragraph(symptoms_text, styles['Normal']))
            elements.append(Spacer(1, 0.1*inch))
        
        # Diagnosis
        if medical_record.get('diagnosis'):
            elements.append(Paragraph("<b>Diagnosis:</b>", styles['Normal']))
            elements.append(Paragraph(medical_record.get('diagnosis', 'N/A'), styles['Normal']))
            elements.append(Spacer(1, 0.1*inch))
        
        # Vitals
        if medical_record.get('vitals'):
            elements.append(Paragraph("<b>Vital Signs:</b>", styles['Normal']))
            vitals_data = [['Vital', 'Value']]
            for key, value in medical_record.get('vitals', {}).items():
                vitals_data.append([key.replace('_', ' ').title(), str(value)])
            
            vitals_table = Table(vitals_data, colWidths=[2*inch, 2*inch])
            vitals_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4788')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')])
            ]))
            elements.append(vitals_table)
            elements.append(Spacer(1, 0.2*inch))
        
        # Prescriptions
        if medical_record.get('prescriptions'):
            elements.append(Paragraph("<b>Prescriptions:</b>", styles['Normal']))
            prescriptions_text = ", ".join(medical_record.get('prescriptions', []))
            elements.append(Paragraph(prescriptions_text, styles['Normal']))
            elements.append(Spacer(1, 0.1*inch))
        
        # Tests
        if medical_record.get('tests'):
            elements.append(Paragraph("<b>Recommended Tests:</b>", styles['Normal']))
            tests_text = ", ".join(medical_record.get('tests', []))
            elements.append(Paragraph(tests_text, styles['Normal']))
            elements.append(Spacer(1, 0.1*inch))
        
        # Doctor Notes
        if medical_record.get('doctor_notes'):
            elements.append(Paragraph("<b>Doctor Notes:</b>", styles['Normal']))
            elements.append(Paragraph(medical_record.get('doctor_notes', 'N/A'), styles['Normal']))
            elements.append(Spacer(1, 0.1*inch))
        
        # Follow-up Date
        if medical_record.get('follow_up_date'):
            elements.append(Paragraph("<b>Follow-up Date:</b>", styles['Normal']))
            elements.append(Paragraph(medical_record.get('follow_up_date', 'N/A'), styles['Normal']))
        
        # Build PDF
        doc.build(elements)
        pdf_buffer.seek(0)
        return pdf_buffer
    
    except Exception as e:
        print(f"❌ Error creating PDF: {str(e)}")
        return None


def upload_medical_record_to_drive(medical_record: dict, patient_id: str, doctor_id: str) -> dict:
    """
    Upload medical record as PDF to Google Drive in a patient-specific folder
    
    Args:
        medical_record: Dictionary containing medical record details
        patient_id: UUID of the patient
        doctor_id: UUID of the doctor
    
    Returns:
        Dictionary with success status and file details
            {
                "success": bool,
                "message": str,
                "file_id": str (if successful),
                "file_url": str (if successful),
                "folder_id": str (if successful)
            }
    """
    try:
        service = get_drive_service()
        if not service:
            return {
                "success": False,
                "message": "Failed to initialize Google Drive service"
            }
        
        # Create or get patient folder
        folder_name = f"Medical_Records_{patient_id}"
        query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
        
        results = service.files().list(q=query, spaces='drive', pageSize=1, fields='files(id, name)').execute()
        folders = results.get('files', [])
        
        if folders:
            folder_id = folders[0]['id']
        else:
            # Create new folder
            file_metadata = {
                'name': folder_name,
                'mimeType': 'application/vnd.google-apps.folder'
            }
            folder = service.files().create(body=file_metadata, fields='id').execute()
            folder_id = folder.get('id')
        
        # Generate PDF
        pdf_buffer = create_medical_record_pdf(medical_record)
        if not pdf_buffer:
            return {
                "success": False,
                "message": "Failed to generate PDF"
            }
        
        # Upload PDF to folder
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        file_name = f"Medical_Record_{patient_id}_{timestamp}.pdf"
        
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        
        media = MediaIoBaseUpload(pdf_buffer, mimetype='application/pdf', resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields='id, webViewLink').execute()
        
        file_id = file.get('id')
        file_url = file.get('webViewLink')
        
        return {
            "success": True,
            "message": "Medical record uploaded to Google Drive successfully",
            "file_id": file_id,
            "file_url": file_url,
            "folder_id": folder_id,
            "file_name": file_name
        }
    
    except GoogleAPIError as e:
        return {
            "success": False,
            "message": f"Google Drive API error: {str(e)}"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to upload medical record to Drive: {str(e)}"
        }


if __name__ == "__main__":
    """
    Test the Google Drive upload functionality with sample medical record
    """
    import json
    from datetime import datetime
    
    # Sample medical record data
    sample_medical_record = {
        "patient_id": "patient-12345",
        "doctor_id": "doctor-67890",
        "full Name": "John Smith",
        "appointment_id": "appt-11111",
        "date": datetime.utcnow(),
        "symptoms": ["Fever", "Cough", "Fatigue"],
        "diagnosis": "Common Cold with Secondary Infection",
        "prescriptions": ["Amoxicillin 500mg", "Acetaminophen 500mg"],
        "tests": ["Chest X-ray", "Complete Blood Count (CBC)"],
        "doctor_notes": "Patient presents with persistent cough lasting 5 days. Oxygen levels stable. Prescribed antibiotics and pain relief. Follow-up in 3 days.",
        "vitals": {
            "blood_pressure": "130/85",
            "heart_rate": 92,
            "temperature": "99.5°F",
            "respiratory_rate": 20
        },
        "follow_up_date": "2026-04-03",
        "created_at": datetime.utcnow()
    }
    
    print("=" * 60)
    print("🏥 Medical Record Google Drive Upload Test")
    print("=" * 60)
    print("")
    
    # Test 1: Create PDF
    print("📄 Test 1: Creating PDF from medical record...")
    pdf_buffer = create_medical_record_pdf(sample_medical_record)
    if pdf_buffer:
        pdf_size = len(pdf_buffer.getvalue())
        print(f"✅ PDF created successfully! Size: {pdf_size / 1024:.2f} KB")
    else:
        print("❌ Failed to create PDF")
    
    print("")
    
    # Test 2: Upload to Google Drive
    print("📁 Test 2: Uploading medical record to Google Drive...")
    result = upload_medical_record_to_drive(
        medical_record=sample_medical_record,
        patient_id=sample_medical_record["patient_id"],
        doctor_id=sample_medical_record["doctor_id"]
    )
    
    print("")
    print("Upload Result:")
    print("-" * 60)
    if result["success"]:
        print(f"✅ Success: {result['message']}")
        print(f"📄 File Name: {result.get('file_name')}")
        print(f"🔗 File URL: {result.get('file_url')}")
        print(f"📁 Folder ID: {result.get('folder_id')}")
        print(f"📋 File ID: {result.get('file_id')}")
    else:
        print(f"❌ Failed: {result['message']}")
    
    print("")
    print("=" * 60)
    print("test complete!")
    print("=" * 60)
