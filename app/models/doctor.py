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
    medical_records = db.relationship('MedicalRecord', backref='doctor', lazy='dynamic',
                                     foreign_keys='MedicalRecord.doctor_id')
    
    @property
    def full_name(self):
        """Return full name of doctor"""
        return f"Dr. {self.first_name} {self.last_name}"
    
    def is_available(self, date, start_time, end_time):
        """Check if doctor is available at a specific time"""
        # To be implemented
        return True
    
    def __repr__(self):
        return f'<Doctor {self.full_name} - {self.specialization}>'