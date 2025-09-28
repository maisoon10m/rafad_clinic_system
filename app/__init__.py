"""
Rafad Clinic System
Flask application factory
"""
from flask import Flask
from config import config_dict


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
    # db.init_app(app)  # Uncomment when SQLAlchemy is added
    # login_manager.init_app(app)  # Uncomment when Flask-Login is added
    
    # Register blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)
    
    # Additional blueprints will be registered here
    # app.register_blueprint(auth_bp)
    # app.register_blueprint(admin_bp)
    # app.register_blueprint(patient_bp)
    # app.register_blueprint(doctor_bp)
    
    return app