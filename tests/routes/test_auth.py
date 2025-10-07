"""
Tests for authentication functionality in Rafad Clinic System
"""
import pytest
from app.models.user import User


def test_user_auth(_db):
    """Test user authentication"""
    # Create a test user
    user = User(
        username='testuser',
        email='test@example.com',
        role='admin'
    )
    user.password = 'password123'
    _db.session.add(user)
    _db.session.commit()
    
    # Retrieve user and verify password
    fetched_user = User.query.filter_by(email='test@example.com').first()
    assert fetched_user is not None
    assert fetched_user.verify_password('password123') is True
    assert fetched_user.verify_password('wrongpassword') is False