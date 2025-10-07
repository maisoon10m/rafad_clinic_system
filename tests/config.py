"""
Test configuration for Rafad Clinic System
"""
from config import Config


class TestConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False  # Disable CSRF tokens in tests
    SECRET_KEY = 'test-secret-key'
    DEBUG = False
    SERVER_NAME = 'localhost'  # Required for url_for to work in tests
    PRESERVE_CONTEXT_ON_EXCEPTION = False