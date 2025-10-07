"""
Tests for User model in Rafad Clinic System
"""
import pytest
from app.models.user import User


def test_password_setter(_db):
    """Test that password setter creates a password hash"""
    user = User(username='test', email='test@example.com')
    user.password = 'cat'
    assert user.password_hash is not None
    # Cannot directly access password attribute, it should be hashed


def test_no_password_getter(_db):
    """Test that password property is not accessible"""
    user = User(username='test', email='test@example.com')
    user.password = 'cat'
    with pytest.raises(AttributeError):
        # Accessing password directly should raise an exception
        password = user.password


def test_password_verification(_db):
    """Test password verification with correct and incorrect passwords"""
    user = User(username='test', email='test@example.com')
    user.password = 'cat'
    assert user.verify_password('cat') is True
    assert user.verify_password('dog') is False


def test_password_salts_are_random(_db):
    """Test that password hashes are different even with the same password"""
    user1 = User(username='test1', email='test1@example.com')
    user2 = User(username='test2', email='test2@example.com')
    user1.password = 'cat'
    user2.password = 'cat'
    assert user1.password_hash != user2.password_hash


def test_user_role(_db):
    """Test default user role assignment"""
    # Create user without explicit role and check default value when saved
    user = User(username='test', email='test@example.com')
    user.password = 'testpassword'  # Set password to satisfy NOT NULL constraint
    _db.session.add(user)
    _db.session.commit()
    assert user.role == 'patient'  # Default role in the DB
    
    # Explicit role assignment
    admin = User(username='admin', email='admin@example.com', role='admin')
    admin.password = 'adminpassword'  # Set password
    assert admin.role == 'admin'
    
    doctor = User(username='doctor', email='doctor@example.com', role='doctor')
    doctor.password = 'doctorpassword'  # Set password
    assert doctor.role == 'doctor'


def test_user_registration(_db):
    """Test registering a user and checking database presence"""
    user = User(username='newuser', email='newuser@example.com')
    user.password = 'password'
    _db.session.add(user)
    _db.session.commit()
    
    # Retrieve the user
    retrieved = User.query.filter_by(email='newuser@example.com').first()
    assert retrieved is not None
    assert retrieved.username == 'newuser'
    assert retrieved.verify_password('password')


def test_duplicate_email(_db):
    """Test that duplicate emails are not allowed"""
    user1 = User(username='user1', email='same@example.com')
    user1.password = 'password'
    _db.session.add(user1)
    _db.session.commit()
    
    user2 = User(username='user2', email='same@example.com')
    user2.password = 'password'
    _db.session.add(user2)
    
    # Should raise an integrity error due to unique constraint
    with pytest.raises(Exception) as e:
        _db.session.commit()
    _db.session.rollback()


def test_duplicate_username(_db):
    """Test that duplicate usernames are not allowed"""
    user1 = User(username='samename', email='user1@example.com')
    user1.password = 'password'
    _db.session.add(user1)
    _db.session.commit()
    
    user2 = User(username='samename', email='user2@example.com')
    user2.password = 'password'
    _db.session.add(user2)
    
    # Should raise an integrity error due to unique constraint
    with pytest.raises(Exception) as e:
        _db.session.commit()
    _db.session.rollback()