"""
GMAIL CALENDAR INVITE SENDER
Send calendar invites to recipients via email
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import ssl
from datetime import datetime, timedelta, timezone
import uuid

from numpy import select


def send_calendar_invite(app_id, sender_email, sender_password, recipient_email, recipient_name, 
                        event_title, event_description, start_time,location="", method="REQUEST", db_handler=None, sequence=0):
    """
    Send a calendar invite (iCalendar format) to a recipient
    
    Args:
        sender_email: Your Gmail address (e.g., 'your_email@gmail.com')
        sender_password: Your 16-character App Password
        recipient_email: Recipient's email address (e.g., 'friend@example.com')
        recipient_name: Recipient's name (e.g., 'John Doe')
        event_title: Title of the event (e.g., 'Meeting with John')
        event_description: Description of the event
        start_time: Start time as datetime object or string "YYYY-MM-DD HH:MM:SS"
        end_time: End time as datetime object or string "YYYY-MM-DD HH:MM:SS"
        location: Location of the event (optional)
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print("\n📅 Creating calendar invite...")
        if not sender_email or not sender_password or not recipient_email:
            print("❌ Missing sender/recipient email configuration.")
            return False

        # Accept both datetime and string formats.
        if isinstance(start_time, datetime):
            if start_time.tzinfo is not None:
                start_time = start_time.astimezone(timezone.utc).replace(tzinfo=None) + timedelta(hours=5, minutes=30)
        elif isinstance(start_time, str):
            start_time = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        else:
            print(f"❌ Unsupported start_time type: {type(start_time)}")
            return False
        end_time = start_time + timedelta(minutes=15)

        # 🔥 Convert IST → UTC
        start_utc = start_time - timedelta(hours=5, minutes=30)
        end_utc = end_time - timedelta(hours=5, minutes=30)

        start_str = start_utc.strftime("%Y%m%dT%H%M%S")
        end_str = end_utc.strftime("%Y%m%dT%H%M%S")
        now_str = datetime.utcnow().strftime("%Y%m%dT%H%M%S")

        event_uid = str(uuid.uuid4())
        Method2 = "CANCEL" if method == "CANCEL" else "SCHEDULE"
        if method == "CANCEL":
            status = "CANCELLED"
        else:
            status = "CONFIRMED"

        if db_handler:
            query = "SELECT event_uid, sequence FROM calender_events WHERE appointment_id = %s"
            result = db_handler.execute_query(query, (app_id,))
            if not result:
                insert_query = """
                    INSERT INTO calender_events (appointment_id, event_uid, sequence)
                    VALUES (%s, %s, %s)
                """
                db_handler.execute_query(insert_query, (app_id, event_uid, sequence))
            else:
                event_uid = result[0].get("event_uid") or event_uid
                sequence = int(result[0].get("sequence", 0))
                if method in ("UPDATE", "CANCEL"):
                    sequence += 1
                    update_query = """
                        UPDATE calender_events 
                        SET sequence = %s
                        WHERE appointment_id = %s
                    """
                    db_handler.execute_query(update_query, (sequence, app_id))


        # ✅ Proper ICS format
        ics_content = f"""BEGIN:VCALENDAR\r\n
VERSION:2.0\r\n
PRODID:-//HospitalApp//Appointment System//EN\r\n
CALSCALE:GREGORIAN\r\n
METHOD:{method}\r\n
BEGIN:VEVENT\r\n
UID:{event_uid}@hospitalapp.com\r\n
DTSTAMP:{now_str}Z\r\n
DTSTART:{start_str}Z\r\n
DTEND:{end_str}Z\r\n
SUMMARY:{event_title}\r\n
DESCRIPTION:{event_description}\r\n
LOCATION:{location}\r\n
ORGANIZER;CN={sender_email}:MAILTO:{sender_email}\r\n
ATTENDEE;CN={recipient_name};ROLE=REQ-PARTICIPANT;PARTSTAT=NEEDS-ACTION;RSVP=TRUE:MAILTO:{recipient_email}\r\n
STATUS:{status}\r\n
SEQUENCE:{sequence}\r\n
TRANSP:OPAQUE\r\n
CLASS:PUBLIC\r\n
END:VEVENT\r\n
END:VCALENDAR\r\n
"""

        # ✅ Email message
        message = MIMEMultipart("mixed")
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Subject"] = f"Calendar Invite: {event_title}"

        # HTML fallback
        html_body = f"""
        <html>
        <body>
            <h3>📅 {event_title}</h3>
            <p><b>Hi Doctor,</b></p>
            <p>You have a {Method2} appointment.</p>
            <p><b>Date:</b> {start_time.strftime('%B %d, %Y')}</p>
            <p><b>Time:</b> {start_time.strftime('%I:%M %p')} - {end_time.strftime('%I:%M %p')}</p>
            <p><b>Location:</b> {location or "Not specified"}</p>
            <p>{event_description}</p>
        </body>
        </html>
        """

        # message.attach(MIMEText(html_body, "html"))

        # 🔥 CRITICAL: Calendar part (NOT attachment)
        calendar_part = MIMEText(ics_content, f"calendar;method={method}", "utf-8")
        calendar_part.add_header("Content-Disposition", "inline")

        message.attach(calendar_part)

        # Send email
        context = ssl.create_default_context()

        print("🔌 Connecting to SMTP...")
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls(context=context)

        print("🔐 Logging in...")
        server.login(sender_email, sender_password)

        print("📤 Sending invite...")
        server.sendmail(sender_email, recipient_email, message.as_string())
        server.quit()

        print("✅ Invite sent successfully!\n")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def send_confirmation_email(sender_email, sender_password, recipient_email, recipient_name, subject, status):
    """
    Send a confirmation email to a recipient.

    Args:
        sender_email: Your Gmail address (e.g., 'your_email@gmail.com')
        sender_password: Your 16-character App Password
        recipient_email: Recipient's email address (e.g., 'friend@example.com')
        recipient_name: Recipient's name (e.g., 'John Doe')
        subject: Subject of the email
        status: Status of the appointment (e.g., 'CONFIRMED', 'CANCELLED')

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        print("\n📧 Creating confirmation email...")

        if not sender_email or not sender_password or not recipient_email:
            print("❌ Missing sender/recipient email configuration.")
            return False

        # Create the email message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = recipient_email
        message["Subject"] = subject

        # Add the email body
        html_body = f"""
        <html>
        <body>
            <p><b>Hi {recipient_name},</b></p>
            <p>Your appointment has been {status}. Thank you for your attention.</p>
        </body>
        </html>
        """
        message.attach(MIMEText(html_body, "html"))

        # Send the email
        context = ssl.create_default_context()

        print("🔌 Connecting to SMTP...")
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls(context=context)

        print("🔐 Logging in...")
        server.login(sender_email, sender_password)

        print("📤 Sending confirmation email...")
        server.sendmail(sender_email, recipient_email, message.as_string())
        server.quit()

        print("✅ Confirmation email sent successfully!\n")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def example_5_interactive():
    """Example 5: Interactive calendar invite"""
    print("\n" + "="*70)
    print("INTERACTIVE CALENDAR INVITE SENDER")
    print("="*70)
    
    print("\n--- SENDER INFO ---")
    sender_email = 'jaiswalmuskan2603@gmail.com'
    sender_password = 'mtacvxkxquhvvmzf'
    
    print("\n--- RECIPIENT INFO ---")
    recipient_email = 'radhe.muskan26@gmail.com'
    recipient_name ='Muskan'
    
    print("\n--- EVENT INFO ---")
    event_title = 'Having a meeting with doctor'
    event_description = ''
    location = ''
    
    print("\n--- TIMING ---")
   
    start_str = '2026-01-01 10:00:00' #input("Start time (YYYY-MM-DD HH:MM:SS): ").strip()
      
    send_calendar_invite(
            sender_email=sender_email,
            sender_password=sender_password,
            recipient_email=recipient_email,
            recipient_name=recipient_name,
            event_title=event_title,
            event_description=event_description,
            start_time=start_str,
            location=location
        )

if __name__ == "__main__":
    example_5_interactive()