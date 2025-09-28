"""
API routes for Rafad Clinic System
"""
from flask import Blueprint
from .appointment import api_bp

# Create parent blueprint for API
api_module = Blueprint('api_module', __name__)

# Register the child blueprints
api_module.register_blueprint(api_bp)

__all__ = ['api_module', 'api_bp']