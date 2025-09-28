"""
Database models for Rafad Clinic System
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

# Initialize SQLAlchemy database instance
db = SQLAlchemy()

# Import models after db is defined to avoid circular imports
from .user import User
from .patient import Patient
from .doctor import Doctor
from .schedule import Schedule
from .appointment import Appointment
from .setting import Setting