"""
Appointment model for Rafad Clinic System
"""
from datetime import datetime
from . import db


class Appointment(db.Model):
    """Appointment model for storing appointment information"""
    __tablename__ = 'appointments'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, completed, cancelled, no_show
    reason = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Property to support code that uses appointment_time
    @property
    def appointment_time(self):
        """Return the start_time for backward compatibility"""
        return self.start_time
        
    @appointment_time.setter
    def appointment_time(self, value):
        """Set the start_time for backward compatibility"""
        self.start_time = value
        # Set end_time to 30 minutes after start time by default
        if value:
            from datetime import datetime, timedelta
            dt = datetime.combine(datetime.today(), value) + timedelta(minutes=30)
            self.end_time = dt.time()
    
    @property
    def is_past(self):
        """Check if appointment is in the past"""
        now = datetime.utcnow().date()
        return self.appointment_date < now or (
            self.appointment_date == now and 
            datetime.utcnow().time() > self.start_time
        )
    
    @property
    def formatted_date(self):
        """Return formatted appointment date"""
        return self.appointment_date.strftime('%d/%m/%Y')
    
    @property
    def formatted_time(self):
        """Return formatted appointment time"""
        return self.start_time.strftime('%H:%M')
        
    @property
    def can_be_cancelled(self):
        """Check if appointment can be cancelled"""
        return self.status == 'scheduled' and not self.is_past
    
    def __repr__(self):
        return f'<Appointment {self.id}: {self.patient.full_name if self.patient else "Unknown"} with {self.doctor.full_name if self.doctor else "Unknown"} on {self.formatted_date} at {self.formatted_time}>'
        
    @classmethod
    def get_appointments_by_date_range(cls, start_date, end_date, doctor_id=None):
        """Get appointments within a date range, optionally filtered by doctor"""
        query = cls.query.filter(
            cls.appointment_date >= start_date,
            cls.appointment_date <= end_date
        )
        
        if doctor_id:
            query = query.filter(cls.doctor_id == doctor_id)
            
        return query.all()
        
    @classmethod
    def check_availability(cls, doctor_id, date, time, exclude_appointment_id=None, duration_minutes=30):
        """
        Check if a doctor is available at the specified date and time
        
        Args:
            doctor_id: The ID of the doctor
            date: The appointment date (can be string or date object)
            time: The appointment start time (can be string or time object)
            exclude_appointment_id: Optional ID of an appointment to exclude from the check (for updates)
            duration_minutes: Duration of the appointment in minutes (default: 30)
            
        Returns:
            tuple: (is_available, reason)
                is_available (bool): True if the doctor is available, False otherwise
                reason (str): Reason why the doctor is not available, or None if available
        """
        from app.models.schedule import Schedule
        from app.models.doctor import Doctor
        from datetime import datetime, timedelta
        from sqlalchemy import and_, or_
        import calendar
        
        # Convert date string to datetime object if needed
        if isinstance(date, str):
            date = datetime.strptime(date, '%Y-%m-%d').date()
        
        # Convert time string to time object if needed
        if isinstance(time, str):
            time = datetime.strptime(time, '%H:%M').time()
        
        # Calculate end time based on duration
        dt_start = datetime.combine(date, time)
        dt_end = dt_start + timedelta(minutes=duration_minutes)
        end_time = dt_end.time()
        
        # Get the day of week (0=Monday, 6=Sunday)
        day_index = date.weekday()
        
        # Check if doctor has schedule for this day
        schedule = Schedule.query.filter_by(
            doctor_id=doctor_id,
            day_of_week=day_index,
            is_active=True
        ).first()
        
        if not schedule:
            return False, "Doctor does not have office hours on this day"
            
        # Check if requested time is within doctor's working hours
        if time < schedule.start_time or end_time > schedule.end_time:
            return False, "Requested time is outside of doctor's working hours"
            
        # Check for conflicting appointments
        # Query for appointments that overlap with the requested time
        query = cls.query.filter(
            cls.doctor_id == doctor_id,
            cls.appointment_date == date,
            cls.status.in_(['scheduled', 'confirmed']),
            or_(
                # Case 1: New appointment starts during an existing one
                and_(
                    cls.start_time <= time,
                    cls.end_time > time
                ),
                # Case 2: New appointment ends during an existing one
                and_(
                    cls.start_time < end_time,
                    cls.end_time >= end_time
                ),
                # Case 3: New appointment completely contains an existing one
                and_(
                    cls.start_time >= time,
                    cls.end_time <= end_time
                ),
                # Case 4: New appointment is contained within an existing one
                and_(
                    cls.start_time <= time,
                    cls.end_time >= end_time
                )
            )
        )
        
        # Exclude the appointment being updated if an ID is provided
        if exclude_appointment_id:
            query = query.filter(cls.id != exclude_appointment_id)
            
        conflicting_appointment = query.first()
        
        if conflicting_appointment:
            return False, f"Time slot conflicts with existing appointment at {conflicting_appointment.formatted_time}"
            
        # All checks passed
        return True, None