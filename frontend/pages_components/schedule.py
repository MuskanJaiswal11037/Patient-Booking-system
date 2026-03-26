# """Doctor/Nurse schedule page component."""
# import streamlit as st
# from datetime import datetime
# from itertools import groupby
# # from components.api import get_doctor_appointments, cancel_appointment
# from components.config import STATUS_COLORS


# def render_schedule_page(role: str):
#     """Render appointment schedule for doctor or nurse."""
#     st.title("📅 Appointment Schedule")
    
#     response = get_doctor_appointments()
    
#     if response and response.status_code == 200:
#         appointments = response.json()
        
#         if not appointments:
#             st.info("📭 No appointments found.")
#         else:
#             # Group appointments by date
#             _render_grouped_appointments(appointments, role)
#     elif response:
#         st.error(f"❌ Error: {response.json().get('detail', 'Failed to load appointments')}")


# def _render_grouped_appointments(appointments: list, role: str):
#     """Render appointments grouped by date."""
#     # Sort by appointment time
#     appointments_sorted = sorted(appointments, key=lambda x: x["appointment_at"])
    
#     # Group by date
#     for date_str, group in groupby(appointments_sorted, key=lambda x: x["appointment_at"][:10]):
#         # Format date header
#         date_obj = datetime.strptime(date_str, "%Y-%m-%d")
#         date_label = date_obj.strftime("%A, %d %B %Y")
#         st.subheader(date_label)
        
#         # Display appointments for this date
#         for appointment in group:
#             _render_appointment_row(appointment, role)
        
#         st.divider()


# def _render_appointment_row(appointment: dict, role: str):
#     """Render a single appointment row."""
#     appointment_dt = datetime.fromisoformat(appointment["appointment_at"])
#     status = appointment["status"]
#     color = STATUS_COLORS.get(status, "⚪")
    
#     # Create columns for appointment info
#     cols = st.columns([1, 3, 2, 1.5])
    
#     cols[0].write(color)
#     cols[1].write(f"**{appointment['patient_name']}**")
#     cols[2].write(appointment_dt.strftime("%I:%M %p"))
#     cols[3].write(status.capitalize())
    
#     # Cancel button for nurses on scheduled appointments
#     if role == "nurse" and status == "scheduled":
#         col1, col2 = st.columns([4, 1])
        
#         with col1:
#             cancel_reason = st.text_input(
#                 "Cancel reason",
#                 key=f"nurse_cancel_reason_{appointment['id']}",
#                 label_visibility="collapsed"
#             )
        
#         with col2:
#             if st.button(
#                 "❌ Cancel",
#                 key=f"nurse_cancel_{appointment['id']}",
#                 use_container_width=True
#             ):
#                 response = cancel_appointment(appointment["id"], cancel_reason)
#                 if response and response.status_code == 200:
#                     st.success("✅ Appointment cancelled.")
#                     st.rerun()
#                 elif response:
#                     st.error(f"❌ {response.json().get('detail', 'Cancel failed')}")
