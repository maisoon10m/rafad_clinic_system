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
    appointment_time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, completed, cancelled, no_show
    reason = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def is_past(self):
        """Check if appointment is in the past"""
        now = datetime.utcnow().date()
        return self.appointment_date < now or (
            self.appointment_date == now and 
            datetime.utcnow().time() > self.appointment_time
        )
    
    @property
    def formatted_date(self):
        """Return formatted appointment date"""
        return self.appointment_date.strftime('%d/%m/%Y')
    
    @property
    def formatted_time(self):
        """Return formatted appointment time"""
        return self.appointment_time.strftime('%H:%M')
        
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
    def check_availability(cls, doctor_id, date, time, exclude_appointment_id=None):
        """
        Check if a doctor is available at the specified date and time
        
        Returns:
            bool: True if the doctor is available, False otherwise
        """
        from app.models.schedule import Schedule
        from datetime import datetime, timedelta
        import calendar
        
        # Convert date string to datetime object if needed
        if isinstance(date, str):
            date = datetime.strptime(date, '%Y-%m-%d').date()
        
        # Convert time string to time object if needed
        if isinstance(time, str):
            time = datetime.strptime(time, '%H:%M').time()
            
        # Get the day of week (0=Monday, 6=Sunday)
        day_index = date.weekday()
        
        # Check if doctor has schedule for this day
        schedule = Schedule.query.filter_by(
            doctor_id=doctor_id,
            day_of_week=day_index,
            is_available=True
        ).first()
        
        if not schedule:
            return False
            
        # Check if requested time is within doctor's working hours
        if time < schedule.start_time or time > schedule.end_time:
            return False
            
        # Check for any existing appointments at the same time
        existing_appointment = cls.query.filter(
            cls.doctor_id == doctor_id,
            cls.appointment_date == date,
            cls.appointment_time == time,
            cls.status.in_(['scheduled', 'confirmed'])
        )
        
        if exclude_appointment_id:
            existing_appointment = existing_appointment.filter(cls.id != exclude_appointment_id)
            
        if existing_appointment.first():
            return False
            
        return True