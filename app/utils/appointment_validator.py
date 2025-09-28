"""
Utility functions for appointment validation and conflict prevention
"""
from datetime import datetime, timedelta


def is_valid_appointment_time(doctor_schedule, appointment_time):
    """
    Check if the appointment time is valid based on the doctor's schedule
    
    Args:
        doctor_schedule: The doctor's schedule object
        appointment_time: The appointment time to check
        
    Returns:
        bool: True if the time is valid, False otherwise
    """
    if not doctor_schedule or not appointment_time:
        return False
    
    # Check if time is within doctor's working hours
    if appointment_time < doctor_schedule.start_time or appointment_time > doctor_schedule.end_time:
        return False
    
    # If schedule has a break, check if time falls within break time
    if (doctor_schedule.break_start and doctor_schedule.break_end and
            doctor_schedule.break_start <= appointment_time < doctor_schedule.break_end):
        return False
    
    return True


def get_appointment_end_time(start_time, duration_minutes):
    """
    Calculate the end time of an appointment based on start time and duration
    
    Args:
        start_time: The start time of the appointment
        duration_minutes: The duration of the appointment in minutes
        
    Returns:
        time: The end time of the appointment
    """
    if not start_time:
        return None
    
    # Combine with today's date to get a datetime object
    start_datetime = datetime.combine(datetime.today(), start_time)
    end_datetime = start_datetime + timedelta(minutes=duration_minutes)
    
    return end_datetime.time()


def check_appointment_conflicts(doctor_id, date, time, duration_minutes, exclude_appointment_id=None):
    """
    Check for appointment conflicts
    
    Args:
        doctor_id: The ID of the doctor
        date: The appointment date
        time: The appointment time
        duration_minutes: The duration of the appointment in minutes
        exclude_appointment_id: Optional ID of an appointment to exclude from the check
        
    Returns:
        tuple: (bool, str) - (True, None) if no conflict, (False, error_message) if conflict exists
    """
    from app.models.appointment import Appointment
    
    # Calculate end time
    start_datetime = datetime.combine(date, time)
    end_datetime = start_datetime + timedelta(minutes=duration_minutes)
    end_time = end_datetime.time()
    
    # Build query to find conflicting appointments
    query = Appointment.query.filter(
        Appointment.doctor_id == doctor_id,
        Appointment.appointment_date == date,
        Appointment.status.in_(['scheduled', 'confirmed'])
    )
    
    if exclude_appointment_id:
        query = query.filter(Appointment.id != exclude_appointment_id)
    
    # Check for time conflicts
    conflicts = []
    for appt in query.all():
        appt_start = appt.appointment_time
        
        # Calculate appointment end time based on doctor's schedule
        from app.models.schedule import Schedule
        doctor_schedule = Schedule.query.filter_by(
            doctor_id=doctor_id,
            day_of_week=date.weekday(),
            is_active=True
        ).first()
        
        appt_duration = doctor_schedule.appointment_duration if doctor_schedule else 30
        appt_end_datetime = datetime.combine(date, appt_start) + timedelta(minutes=appt_duration)
        appt_end = appt_end_datetime.time()
        
        # Check if there's an overlap
        if (time < appt_end and end_time > appt_start):
            conflicts.append(appt)
    
    if conflicts:
        conflict_times = [f"{appt.appointment_time.strftime('%H:%M')}" for appt in conflicts]
        error_message = f"Appointment conflicts with existing appointments at: {', '.join(conflict_times)}"
        return False, error_message
    
    return True, None


def validate_appointment_request(doctor_id, date, time, duration_minutes=None, exclude_appointment_id=None):
    """
    Validate an appointment request
    
    Args:
        doctor_id: The ID of the doctor
        date: The appointment date
        time: The appointment time
        duration_minutes: Optional duration of the appointment in minutes
        exclude_appointment_id: Optional ID of an appointment to exclude from the conflict check
        
    Returns:
        tuple: (bool, str) - (True, None) if valid, (False, error_message) if invalid
    """
    from app.models.schedule import Schedule
    
    # Check if date is in the past
    if date < datetime.now().date():
        return False, "Cannot book appointments in the past"
    
    # Get the day of week (0=Monday, 6=Sunday)
    day_of_week = date.weekday()
    
    # Check if doctor has a schedule for this day
    doctor_schedule = Schedule.query.filter_by(
        doctor_id=doctor_id,
        day_of_week=day_of_week,
        is_active=True
    ).first()
    
    if not doctor_schedule:
        return False, "Doctor is not available on this day"
    
    # Use schedule's appointment duration if not provided
    if duration_minutes is None:
        duration_minutes = doctor_schedule.appointment_duration
    
    # Check if time is valid
    if not is_valid_appointment_time(doctor_schedule, time):
        return False, "Invalid appointment time"
    
    # Check for conflicts
    no_conflicts, conflict_message = check_appointment_conflicts(
        doctor_id, date, time, duration_minutes, exclude_appointment_id
    )
    
    if not no_conflicts:
        return False, conflict_message
    
    return True, None