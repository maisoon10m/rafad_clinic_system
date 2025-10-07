"""
Rafad Clinic System
Flask application factory
"""
from datetime import datetime
from flask import Flask, render_template, request
from flask_login import LoginManager
from flask_migrate import Migrate
from config import config_dict
from sqlalchemy.exc import SQLAlchemyError
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
    
    # Register all blueprints using the centralized registration function
    from app.routes import register_blueprints
    register_blueprints(app)
    
    # Error handlers
    @app.errorhandler(403)
    def forbidden(e):
        app.logger.warning(f"403 Forbidden access: {request.path} - {request.remote_addr}")
        return render_template('errors/403.html', 
                              error=e, 
                              title="Access Forbidden",
                              message="You do not have permission to access this resource"), 403
        
    @app.errorhandler(404)
    def page_not_found(e):
        app.logger.info(f"404 Page not found: {request.path} - {request.remote_addr}")
        return render_template('errors/404.html', 
                              error=e, 
                              title="Page Not Found", 
                              message="The requested page could not be found"), 404
    
    @app.errorhandler(500)
    def internal_server_error(e):
        # Log the error with traceback
        from app.utils.error_handler import ErrorHandler
        ErrorHandler.log_error(e, context={"path": request.path, "method": request.method})
        
        return render_template('errors/500.html',
                              error=e if app.debug else None,
                              title="Server Error",
                              message="An unexpected error has occurred. Our technical team has been notified."), 500
                              
    # Handle SQLAlchemy errors
    @app.errorhandler(SQLAlchemyError)
    def handle_sqlalchemy_error(e):
        from app.utils.error_handler import ErrorHandler
        ErrorHandler.log_error(e, context={"path": request.path, "method": request.method})
        
        db.session.rollback()
        return render_template('errors/500.html',
                              error=e if app.debug else None,
                              title="Database Error",
                              message="A database error has occurred. Please try again later."), 500
        
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