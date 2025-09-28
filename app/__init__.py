"""
Rafad Clinic System
Flask application factory
"""
from datetime import datetime
from flask import Flask, render_template
from flask_login import LoginManager
from flask_migrate import Migrate
from config import config_dict
from app.models import db, User


# Initialize Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))


def create_app(config_name='development'):
    """
    Create and configure the Flask application
    
    Args:
        config_name (str): The configuration to use (development, testing, production)
        
    Returns:
        Flask: The configured Flask application
    """
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config_dict[config_name])
    config_dict[config_name].init_app(app)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    migrate = Migrate(app, db)
    
    # Register blueprints
    from app.routes import main_bp
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.patient import patient_bp
    from app.routes.doctor import doctor_bp
    from app.routes.appointment import appointment_bp
    from app.routes.schedule import schedule_bp
    from app.routes.api.appointment import api_bp
    from app.routes.api.validation import validate_bp
    from app.routes.api.schedule import schedule_api_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(patient_bp, url_prefix='/patient')
    app.register_blueprint(doctor_bp, url_prefix='/doctor')
    app.register_blueprint(appointment_bp, url_prefix='/appointment')
    app.register_blueprint(schedule_bp, url_prefix='/schedule')
    
    # Register API blueprints
    app.register_blueprint(api_bp)
    app.register_blueprint(validate_bp)
    app.register_blueprint(schedule_api_bp)
    
    # Error handlers
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403
        
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('errors/500.html'), 500
        
    # Add context processor for templates
    @app.context_processor
    def inject_now():
        """
        Inject the current datetime into all templates
        """
        return {'now': datetime.now()}
    
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
    
    return app