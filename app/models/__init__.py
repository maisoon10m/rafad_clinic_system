"""
Database models for Rafad Clinic System
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

# Initialize SQLAlchemy database instance
db = SQLAlchemy()

# Importing models at the end of the file prevents circular imports
# These imports are used by other modules to access models through app.models
# But we import them after db is defined to avoid circular dependencies

def load_models():
    """Import all models to make them available through the models module"""
    from .user import User
    from .patient import Patient
    from .doctor import Doctor
    from .schedule import Schedule
    from .appointment import Appointment
    from .setting import Setting
    
    return {
        'User': User,
        'Patient': Patient,
        'Doctor': Doctor,
        'Schedule': Schedule,
        'Appointment': Appointment,
        'Setting': Setting,
    }

# Make models available at module level
models_dict = load_models()
User = models_dict['User']
Patient = models_dict['Patient']
Doctor = models_dict['Doctor']
Schedule = models_dict['Schedule']
Appointment = models_dict['Appointment']
Setting = models_dict['Setting']