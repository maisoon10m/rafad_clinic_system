"""
Route management for the Rafad Clinic System
This module handles all blueprint registration and route organization
"""
from flask import Blueprint, render_template, Flask

# Create main blueprint
main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Home page route"""
    return render_template('index.html', title='Rafad Clinic System')


@main_bp.route('/about')
def about():
    """About page route"""
    return render_template('about.html', title='About Us')


def register_blueprints(app: Flask):
    """
    Register all blueprints with the Flask application
    
    Args:
        app: The Flask application instance
    """
    # Import blueprints
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.patient import patient_bp
    from app.routes.doctor import doctor_bp
    from app.routes.appointment import appointment_bp
    from app.routes.schedule import schedule_bp
    from app.routes.reporting import reporting_bp
    from app.routes.api.appointment import api_bp
    from app.routes.api.validation import validate_bp
    from app.routes.api.schedule import schedule_api_bp
    
    # Main routes
    app.register_blueprint(main_bp)
    
    # User-related routes
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(patient_bp, url_prefix='/patient')
    app.register_blueprint(doctor_bp, url_prefix='/doctor')
    
    # Functional routes
    app.register_blueprint(appointment_bp, url_prefix='/appointment')
    app.register_blueprint(schedule_bp, url_prefix='/schedule')
    app.register_blueprint(reporting_bp, url_prefix='/reporting')
    
    # API routes
    app.register_blueprint(api_bp)
    app.register_blueprint(validate_bp)
    app.register_blueprint(schedule_api_bp)