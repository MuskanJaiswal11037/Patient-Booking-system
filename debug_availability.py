"""
Diagnostic script to debug Dr. Sneha's availability and slot generation.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from backend.utils.database_handler import db_handler
import datetime

def check_doctor_availability():
    """Check Dr. Sneha's availability configuration."""
    print("\n" + "="*80)
    print("DR. SNEHA'S AVAILABILITY CONFIGURATION")
    print("="*80)
    
    try:
        # First find Dr. Sneha's doctor_id
        query = """
        SELECT d.id, u.full_name, u.email
        FROM doctors d
        JOIN users u ON d.user_email = u.email
        WHERE LOWER(u.full_name) LIKE LOWER('%Sneha%')
        """
        result = db_handler.execute_query(query)
        
        if not result:
            print("❌ Dr. Sneha not found in database")
            return None
        
        doctor = result[0]
        doctor_id = doctor['id']
        doctor_name = doctor['full_name']
        print(f"\n✅ Found: {doctor_name} (ID: {doctor_id})")
        
        # Get availability
        avail_query = """
        SELECT day_of_week, start_time, end_time, slot_duration_minutes
        FROM doctor_availability
        WHERE doctor_id = %s
        ORDER BY day_of_week, start_time
        """
        avail_result = db_handler.execute_query(avail_query, (str(doctor_id),))
        
        if not avail_result:
            print("❌ No availability schedule configured!")
            return doctor_id
        
        print(f"\n✅ Availability Schedule ({len(avail_result)} slots):")
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        for slot in avail_result:
            dow = slot['day_of_week']
            day_name = day_names[dow] if 0 <= dow < 7 else f"Day {dow}"
            print(f"   {day_name}: {slot['start_time']} - {slot['end_time']}")
        
        return doctor_id
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def check_booked_appointments(doctor_id):
    """Check booked appointments for Dr. Sneha today."""
    print("\n" + "="*80)
    print("BOOKED APPOINTMENTS TODAY")
    print("="*80)
    
    try:
        today = datetime.datetime.now().date()
        tomorrow = today + datetime.timedelta(days=1)
        
        query = """
        SELECT a.id, a.appointment_at, a.status, a.duration_minutes,
               u.full_name as patient_name
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN users u ON p.user_email = u.email
        WHERE a.doctor_id = %s
          AND DATE(a.appointment_at) = %s
          AND a.status IN ('scheduled', 'rescheduled', 'in-progress')
        ORDER BY a.appointment_at
        """
        
        result = db_handler.execute_query(query, (str(doctor_id), today))
        
        if not result:
            print(f"✅ No booked appointments today ({today})")
            return
        
        print(f"\n✅ Found {len(result)} appointment(s) today:")
        for apt in result:
            print(f"   {apt['appointment_at']} - {apt['patient_name']} ({apt['status']})")
    
    except Exception as e:
        print(f"❌ Error: {e}")


def check_current_time_and_availability():
    """Check current time vs availability window."""
    print("\n" + "="*80)
    print("CURRENT TIME ANALYSIS")
    print("="*80)
    
    now = datetime.datetime.now()
    print(f"\n⏰ Current Time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏰ Current Day: {['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][now.weekday()]}")
    
    # Check if it's past 8 PM
    eight_pm = datetime.time(20, 0, 0)
    current_time = now.time()
    
    if current_time >= eight_pm:
        print(f"\n❌ CRITICAL: Current time ({current_time.strftime('%H:%M:%S')}) is PAST 8 PM!")
        print("   This means Dr. Sneha's availability window (till 8PM) has already ended for today.")
    else:
        time_until_eightpm = datetime.datetime.combine(now.date(), eight_pm) - now
        hours = time_until_eightpm.seconds // 3600
        minutes = (time_until_eightpm.seconds % 3600) // 60
        print(f"\n✅ Time remaining until 8 PM: {hours} hours {minutes} minutes")


def test_slot_generation(doctor_id):
    """Test the slot generation function."""
    print("\n" + "="*80)
    print("TESTING SLOT GENERATION")
    print("="*80)
    
    try:
        from backend.tools import get_doctor_available_slots
        
        # Test with current time
        result = get_doctor_available_slots(doctor_id=str(doctor_id), days_ahead=7, num_slots=10)
        
        print(f"\n📋 Slot Generation Result:")
        print(f"   Success: {result['success']}")
        print(f"   Message: {result['message']}")
        print(f"   Doctor: {result.get('doctor_name', 'N/A')}")
        print(f"   Total Available: {result.get('total_available_slots', 0)}")
        print(f"   Returned Slots: {len(result.get('available_slots', []))}")
        
        if result.get('available_slots'):
            print(f"\n✅ Top available slots:")
            for slot in result['available_slots'][:5]:
                print(f"   {slot['datetime']} ({slot['day_of_week']})")
        else:
            print("\n❌ NO SLOTS RETURNED!")
    
    except Exception as e:
        print(f"❌ Error testing slots: {e}")
        import traceback
        traceback.print_exc()


def main():
    """Run diagnostic checks."""
    print("\n" + "="*80)
    print("🏥 DR. SNEHA AVAILABILITY DIAGNOSTIC")
    print("="*80)
    
    # Check current time first
    check_current_time_and_availability()
    
    # Get doctor ID and availability
    doctor_id = check_doctor_availability()
    if not doctor_id:
        print("\n❌ Cannot continue without doctor ID")
        return
    
    # Check booked appointments
    check_booked_appointments(doctor_id)
    
    # Test slot generation
    test_slot_generation(doctor_id)
    
    print("\n" + "="*80)
    print("DIAGNOSTIC COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":
    main()
