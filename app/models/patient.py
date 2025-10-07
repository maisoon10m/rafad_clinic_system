"""
Patient model for Rafad Clinic System
"""
from datetime import datetime
from . import db


class Patient(db.Model):
    """Patient model for storing patient-specific data"""
    __tablename__ = 'patients'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    address = db.Column(db.String(256))
    medical_history = db.Column(db.Text)
    
    # Relationships
    appointments = db.relationship('Appointment', backref='patient', lazy='dynamic',
                                  cascade='all, delete-orphan')
    medical_records = db.relationship('MedicalRecord', backref='patient', lazy='dynamic',
                                    cascade='all, delete-orphan')
    
    @property
    def full_name(self):
        """Return full name of patient"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def age(self):
        """Calculate patient's age based on date of birth"""
        if self.date_of_birth:
            today = datetime.utcnow().date()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        return None
    
    def __repr__(self):
        return f'<Patient {self.full_name}>'