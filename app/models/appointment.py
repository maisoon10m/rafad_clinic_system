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
    status = db.Column(db.String(20), default='booked')  # booked, cancelled, completed
    reason = db.Column(db.Text)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    @property
    def duration_minutes(self):
        """Calculate appointment duration in minutes"""
        if self.start_time and self.end_time:
            start_datetime = datetime.combine(datetime.today(), self.start_time)
            end_datetime = datetime.combine(datetime.today(), self.end_time)
            delta = end_datetime - start_datetime
            return delta.seconds // 60
        return 0
    
    @property
    def is_past(self):
        """Check if appointment is in the past"""
        now = datetime.utcnow().date()
        return self.appointment_date < now or (
            self.appointment_date == now and 
            datetime.utcnow().time() > self.end_time
        )
    
    @property
    def formatted_date(self):
        """Return formatted appointment date"""
        return self.appointment_date.strftime('%Y-%m-%d')
    
    @property
    def formatted_time(self):
        """Return formatted appointment time slot"""
        start = self.start_time.strftime('%H:%M')
        end = self.end_time.strftime('%H:%M')
        return f"{start} - {end}"
    
    def __repr__(self):
        return f'<Appointment {self.id}: {self.patient.full_name if self.patient else "Unknown"} with {self.doctor.full_name if self.doctor else "Unknown"} on {self.formatted_date} at {self.formatted_time}>'