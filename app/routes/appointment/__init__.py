"""
Appointment and Schedule routes for Rafad Clinic System
"""
from flask import Blueprint
from .appointment import appointment_bp
from .schedule import schedule_bp

# Create parent blueprint for appointment management
appointment_module = Blueprint('appointment_module', __name__)

# Register the child blueprints
appointment_module.register_blueprint(appointment_bp)
appointment_module.register_blueprint(schedule_bp)

__all__ = ['appointment_module', 'appointment_bp', 'schedule_bp']