"""
Tests for admin functionality in Rafad Clinic System
"""
import pytest
from app.models.user import User
from app.models.patient import Patient
from app.models.doctor import Doctor


def test_admin_user_creation(_db):
    """Test admin user creation"""
    admin = User(
        username='admin_test_user',
        email='admin_test@example.com',
        role='admin'
    )
    admin.password = 'adminpassword'
    _db.session.add(admin)
    _db.session.commit()
    
    # Retrieve the admin user
    retrieved = User.query.filter_by(email='admin_test@example.com').first()
    assert retrieved is not None
    assert retrieved.role == 'admin'
    assert retrieved.verify_password('adminpassword')


def test_admin_user_management(_db):
    """Test admin ability to create and manage users"""
    # Create an admin user
    admin = User(
        username='user_admin',
        email='user_admin@example.com',
        role='admin'
    )
    admin.password = 'adminpass'
    _db.session.add(admin)
    _db.session.commit()
    
    # Admin creates a new patient user
    new_patient_user = User(
        username='new_patient',
        email='new_patient@example.com',
        role='patient'
    )
    new_patient_user.password = 'patientpass'
    _db.session.add(new_patient_user)
    _db.session.flush()
    
    # Create patient profile
    from datetime import datetime, date
    new_patient = Patient(
        user_id=new_patient_user.id,
        first_name='New',
        last_name='Patient',
        gender='male',
        phone='1231231234',
        date_of_birth=date(1990, 1, 1)  # Use proper date object instead of string
    )
    _db.session.add(new_patient)
    _db.session.commit()
    
    # Admin creates a new doctor user
    new_doctor_user = User(
        username='new_doctor',
        email='new_doctor@example.com',
        role='doctor'
    )
    new_doctor_user.password = 'doctorpass'
    _db.session.add(new_doctor_user)
    _db.session.flush()
    
    # Create doctor profile
    new_doctor = Doctor(
        user_id=new_doctor_user.id,
        first_name='New',
        last_name='Doctor',
        specialization='Dermatology',
        phone='4564564567'
    )
    _db.session.add(new_doctor)
    _db.session.commit()
    
    # Admin can retrieve all users
    all_users = User.query.all()
    assert len(all_users) >= 3  # Admin, patient, and doctor
    
    # Admin can update user status
    new_patient_user.is_active = False
    _db.session.commit()
    
    updated_user = User.query.filter_by(id=new_patient_user.id).first()
    assert updated_user.is_active is False


def test_admin_auth_client(admin_auth_client):
    """Test admin authenticated client can access admin routes"""
    # This uses the admin_auth_client fixture from conftest.py
    response = admin_auth_client.get('/admin/dashboard')
    assert response.status_code == 200  # Should be able to access admin dashboard


def test_non_admin_cannot_access_admin_routes(auth_client):
    """Test non-admin users cannot access admin routes"""
    # This uses the auth_client fixture from conftest.py (which is a patient)
    response = auth_client.get('/admin/dashboard')
    assert response.status_code in [302, 401, 403]  # Should be redirected or forbidden
    

def test_admin_user_search(_db, test_admin):
    """Test admin ability to search for users"""
    # Create some test users
    users = [
        User(username=f'test_user_{i}', 
             email=f'test_user_{i}@example.com',
             role='patient')
        for i in range(3)
    ]
    
    for user in users:
        user.password = 'password123'
        _db.session.add(user)
    
    _db.session.commit()
    
    # Test searching by username
    found_users = User.query.filter(User.username.like('test_user_%')).all()
    assert len(found_users) >= 3
    
    # Test searching by email
    found_users = User.query.filter(User.email.like('test_user_%@example.com')).all()
    assert len(found_users) >= 3
    
    # Test searching by role
    patient_users = User.query.filter_by(role='patient').all()
    assert len(patient_users) >= 3