"""
Forms module for Rafad Clinic System
"""
from flask_wtf import FlaskForm

# Import forms from submodules
from .auth import (
    LoginForm, RegistrationForm, 
    PasswordResetRequestForm, PasswordResetForm
)

from .patient import PatientProfileForm
from .doctor import DoctorProfileForm