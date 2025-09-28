"""
Schedule model for Rafad Clinic System
"""
from datetime import datetime
from . import db


class Schedule(db.Model):
    """Schedule model for storing doctor's availability"""
    __tablename__ = 'schedules'

    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    appointment_duration = db.Column(db.Integer, default=30)  # in minutes
    break_duration = db.Column(db.Integer, default=0)  # in minutes
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def day_name(self):
        """Return name of day of week"""
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        return days[self.day_of_week]
    
    @property
    def day_name_lower(self):
        """Return lowercase name of day of week for API use"""
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        return days[self.day_of_week]
    
    @property
    def time_slot(self):
        """Return formatted time slot"""
        start = self.start_time.strftime("%H:%M")
        end = self.end_time.strftime("%H:%M")
        return f"{start} - {end}"
    
    def __repr__(self):
        return f'<Schedule {self.doctor.full_name if self.doctor else "Unknown"}: {self.day_name} {self.time_slot}>'
        
    @classmethod
    def get_available_slots(cls, doctor_id, date, exclude_appointment_id=None):
        """
        Calculate available time slots for a given doctor on a specific date.
        
        Args:
            doctor_id: The ID of the doctor
            date: The date to check for availability
            exclude_appointment_id: Optional appointment ID to exclude (for editing existing)
            
        Returns:
            list: List of available time slots in 'HH:MM' format
        """
        from app.models.appointment import Appointment
        from datetime import datetime, timedelta
        
        # Convert date string to datetime object if needed
        if isinstance(date, str):
            date = datetime.strptime(date, '%Y-%m-%d').date()
            
        # Get the day of week (0 is Monday, 6 is Sunday)
        day_index = date.weekday()
        
        # Find the doctor's schedule for this day
        schedule = cls.query.filter_by(
            doctor_id=doctor_id,
            day_of_week=day_index,
            is_active=True
        ).first()
        
        if not schedule:
            return []
        
        # Generate all possible time slots based on schedule
        all_slots = []
        current_time = datetime.combine(date, schedule.start_time)
        end_datetime = datetime.combine(date, schedule.end_time)
        
        slot_duration = timedelta(minutes=schedule.appointment_duration)
        break_duration = timedelta(minutes=schedule.break_duration)
        
        while current_time + slot_duration <= end_datetime:
            all_slots.append(current_time.strftime('%H:%M'))
            current_time += slot_duration + break_duration
        
        # Get all appointments for this doctor on this day
        appointments = Appointment.query.filter(
            Appointment.doctor_id == doctor_id,
            Appointment.appointment_date == date,
            Appointment.status.in_(['scheduled', 'confirmed'])
        )
        
        if exclude_appointment_id:
            appointments = appointments.filter(Appointment.id != exclude_appointment_id)
            
        booked_slots = [appt.appointment_time.strftime('%H:%M') for appt in appointments]
        
        # Remove booked slots from available slots
        available_slots = [slot for slot in all_slots if slot not in booked_slots]
        
        return available_slots