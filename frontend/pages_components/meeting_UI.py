"""
Gmail API Email Invite Sender with Calendar Attachment
Sends email invites with .ics calendar attachments using Gmail API
"""

import os
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime, timedelta
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pickle

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.send']


def create_ics_attachment(event_title, event_description, start_time, end_time, location=""):
    """
    Create an .ics calendar file content
    
    Args:
        event_title: Title of the event
        event_description: Description of the event
        start_time: datetime object for event start
        end_time: datetime object for event end
        location: Event location (optional)
    
    Returns:
        String containing .ics file content
    """
    # Format datetime to iCal format (YYYYMMDDTHHMMSSZ)
    start_str = start_time.strftime('%Y%m%dT%H%M%SZ')
    end_str = end_time.strftime('%Y%m%dT%H%M%SZ')
    now_str = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    
    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Email Invite//EN
CALSCALE:GREGORIAN
METHOD:REQUEST
BEGIN:VEVENT
DTSTART:{start_str}
DTEND:{end_str}
DTSTAMP:{now_str}
SUMMARY:{event_title}
DESCRIPTION:{event_description}
LOCATION:{location}
STATUS:CONFIRMED
SEQUENCE:0
BEGIN:VALARM
TRIGGER:-PT15M
ACTION:DISPLAY
DESCRIPTION:Reminder
END:VALARM
END:VEVENT
END:VCALENDAR"""
    
    return ics_content


def authenticate_gmail():
    """
    Authenticate with Gmail API using OAuth 2.0
    
    Returns:
        Authenticated Gmail API service object
    """
    creds = None
    
    # Token file stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials, let user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # You need to download credentials.json from Google Cloud Console
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return build('gmail', 'v1', credentials=creds)


def create_email_with_attachment(to_email, subject, body_text, body_html, ics_content, event_title):
    """
    Create email message with calendar attachment
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        body_text: Plain text email body
        body_html: HTML email body
        ics_content: Content of .ics file
        event_title: Title for the .ics filename
    
    Returns:
        Encoded email message ready to send
    """
    message = MIMEMultipart('mixed')
    message['To'] = to_email
    message['Subject'] = subject
    
    # Create alternative part for text/html
    msg_alternative = MIMEMultipart('alternative')
    message.attach(msg_alternative)
    
    # Add plain text version
    part_text = MIMEText(body_text, 'plain')
    msg_alternative.attach(part_text)
    
    # Add HTML version
    part_html = MIMEText(body_html, 'html')
    msg_alternative.attach(part_html)
    
    # Add .ics calendar attachment
    attachment = MIMEBase('text', 'calendar', method='REQUEST')
    attachment.set_payload(ics_content)
    encoders.encode_base64(attachment)
    
    # Safe filename
    safe_filename = "".join(c for c in event_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
    attachment.add_header('Content-Disposition', f'attachment; filename="{safe_filename}.ics"')
    attachment.add_header('Content-class', 'urn:content-classes:calendarmessage')
    
    message.attach(attachment)
    
    # Encode message
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    return {'raw': raw_message}


def send_email_invite(service, to_email, event_details):
    """
    Send email invite with calendar attachment
    
    Args:
        service: Authenticated Gmail API service
        to_email: Recipient email address
        event_details: Dictionary containing event information
            - title: Event title
            - description: Event description
            - start_time: datetime object
            - end_time: datetime object
            - location: Event location (optional)
    
    Returns:
        Sent message object or None if failed
    """
    try:
        # Create .ics content
        ics_content = create_ics_attachment(
            event_title=event_details['title'],
            event_description=event_details['description'],
            start_time=event_details['start_time'],
            end_time=event_details['end_time'],
            location=event_details.get('location', '')
        )
        
        # Email subject
        subject = f"Invitation: {event_details['title']}"
        
        # Plain text body
        body_text = f"""You're invited!

Event: {event_details['title']}
When: {event_details['start_time'].strftime('%B %d, %Y at %I:%M %p')}
Location: {event_details.get('location', 'TBD')}

Description:
{event_details['description']}

Please find the calendar invitation attached.
"""
        
        # HTML body
        body_html = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <h2 style="color: #4285f4;">You're Invited!</h2>
    
    <div style="background-color: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0;">
        <h3 style="margin-top: 0;">{event_details['title']}</h3>
        <p><strong>📅 When:</strong> {event_details['start_time'].strftime('%B %d, %Y at %I:%M %p')}</p>
        <p><strong>📍 Where:</strong> {event_details.get('location', 'TBD')}</p>
        <p><strong>⏱️ Duration:</strong> {int((event_details['end_time'] - event_details['start_time']).total_seconds() / 60)} minutes</p>
    </div>
    
    <div style="margin: 20px 0;">
        <h4>Description:</h4>
        <p>{event_details['description']}</p>
    </div>
    
    <p style="color: #666; font-size: 0.9em;">A calendar invitation (.ics file) is attached to this email. Click to add it to your calendar.</p>
</body>
</html>
"""
        
        # Create message
        message = create_email_with_attachment(
            to_email=to_email,
            subject=subject,
            body_text=body_text,
            body_html=body_html,
            ics_content=ics_content,
            event_title=event_details['title']
        )
        
        # Send message
        sent_message = service.users().messages().send(
            userId='me',
            body=message
        ).execute()
        
        print(f"✅ Email invite sent successfully to {to_email}")
        print(f"   Message ID: {sent_message['id']}")
        return sent_message
        
    except HttpError as error:
        print(f"❌ An error occurred: {error}")
        return None


def main():
    """
    Example usage
    """
    # Authenticate with Gmail
    print("Authenticating with Gmail API...")
    service = authenticate_gmail()
    print("✅ Authentication successful!\n")
    
    # Example event details
    event_details = {
        'title': 'Team Meeting - Q1 Planning',
        'description': 'Quarterly planning meeting to discuss goals and objectives for Q1 2024.',
        'start_time': datetime(2024, 4, 15, 14, 0, 0),  # April 15, 2024, 2:00 PM
        'end_time': datetime(2024, 4, 15, 15, 30, 0),   # April 15, 2024, 3:30 PM
    }
    
    # Recipient email
    recipient_email = "recipient@example.com"  # Change this to actual email
    
    # Send invite
    print(f"Sending invite to {recipient_email}...")
    send_email_invite(service, recipient_email, event_details)


if __name__ == '__main__':
    main()