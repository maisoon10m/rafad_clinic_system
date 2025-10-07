"""
Doctor model for Rafad Clinic System
"""
from . import db


class Doctor(db.Model):
    """Doctor model for storing doctor-specific data"""
    __tablename__ = 'doctors'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    specialization = db.Column(db.String(64), nullable=False)
    bio = db.Column(db.Text)
    phone = db.Column(db.String(20))
    qualification = db.Column(db.String(128))
    experience_years = db.Column(db.Integer)
    profile_image = db.Column(db.String(128))  # Stores path to profile image
    
    # Relationships
    schedules = db.relationship('Schedule', backref='doctor', lazy='dynamic',
                               cascade='all, delete-orphan')
    appointments = db.relationship('Appointment', backref='doctor', lazy='dynamic',
                                  cascade='all, delete-orphan')
    
    @property
    def full_name(self):
        """Return full name of doctor"""
        return f"Dr. {self.first_name} {self.last_name}"
    
    def is_available(self, date, start_time, end_time, exclude_appointment_id=None):
        """
        Check if doctor is available at a specific time
        
        Args:
            date: The date to check (datetime.date)
            start_time: The start time to check (datetime.time)
            end_time: The end time to check (datetime.time)
            exclude_appointment_id: Optional appointment ID to exclude from the check (for updates)
            
        Returns:
            tuple: (is_available, reason)
                is_available (bool): True if the doctor is available, False otherwise
                reason (str): Reason why the doctor is not available, or None if available
        """
        from datetime import datetime
        import calendar
        from sqlalchemy import and_, or_
        from app.models.appointment import Appointment
        
        # Check if the doctor has a schedule for that day
        day_of_week = date.weekday()  # 0=Monday, 6=Sunday
        
        # Find doctor's schedule for this day
        schedule = self.schedules.filter_by(
            day_of_week=day_of_week, 
            is_active=True
        ).first()
        
        # If no schedule for this day, doctor is not available
        if not schedule:
            return False, "Doctor does not have office hours on this day"
        
        # Check if the requested time is within the doctor's schedule
        if start_time < schedule.start_time or end_time > schedule.end_time:
            return False, "Requested time is outside of doctor's working hours"
            
        # Check for conflicting appointments
        # Query for appointments that overlap with the requested time
        query = Appointment.query.filter(
            Appointment.doctor_id == self.id,
            Appointment.appointment_date == date,
            Appointment.status != 'cancelled',  # Exclude cancelled appointments
            or_(
                # Case 1: New appointment starts during an existing one
                and_(
                    Appointment.start_time <= start_time,
                    Appointment.end_time > start_time
                ),
                # Case 2: New appointment ends during an existing one
                and_(
                    Appointment.start_time < end_time,
                    Appointment.end_time >= end_time
                ),
                # Case 3: New appointment completely contains an existing one
                and_(
                    Appointment.start_time >= start_time,
                    Appointment.end_time <= end_time
                )
            )
        )
        
        # Exclude the appointment being updated if an ID is provided
        if exclude_appointment_id:
            query = query.filter(Appointment.id != exclude_appointment_id)
            
        conflicting_appointments = query.all()
        
        if conflicting_appointments:
            return False, "Doctor has a conflicting appointment at this time"
            
        return True, None
    
    def __repr__(self):
        return f'<Doctor {self.full_name} - {self.specialization}>'