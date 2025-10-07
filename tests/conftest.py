"""
Pytest fixtures for Rafad Clinic System tests
"""
import os
import sys
import pytest
from datetime import datetime, timedelta

# Add the parent directory to the path so we can import app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.user import User
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.schedule import Schedule
from app.models.appointment import Appointment
from tests.config import TestConfig


@pytest.fixture(scope='function')
def app():
    """Create and configure a Flask app for testing"""
    app = create_app('testing')
    app.config.from_object(TestConfig)
    
    # Establish application context
    with app.app_context():
        # Create all tables
        db.create_all()
        yield app
        
        # Clean up
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """A test client for the app"""
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """A test CLI runner for the app"""
    return app.test_cli_runner()


@pytest.fixture(scope='function')
def _db(app):
    """Create and configure a database for testing"""
    with app.app_context():
        db.create_all()
        yield db
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def test_admin(app, _db):
    """Create a test admin user"""
    admin = User(
        username='admin_test',
        email='admin@example.com',
        role='admin',
        is_active=True
    )
    admin.password = 'password'
    _db.session.add(admin)
    _db.session.commit()
    return admin


@pytest.fixture(scope='function')
def test_patient_user(app, _db):
    """Create a test patient user"""
    user = User(
        username='patient_test',
        email='patient@example.com',
        role='patient',
        is_active=True
    )
    user.password = 'password'
    _db.session.add(user)
    _db.session.flush()  # Flush to get the user ID
    
    patient = Patient(
        user_id=user.id,
        first_name='Test',
        last_name='Patient',
        phone='1234567890',
        date_of_birth=datetime(1990, 1, 1),
        gender='male',
        address='123 Test St',
        medical_history='No significant medical history'
    )
    _db.session.add(patient)
    _db.session.commit()
    return user

@pytest.fixture(scope='function')
def test_patient(app, _db, test_patient_user):
    """Return the patient instance directly for tests that need it"""
    return test_patient_user.patient


@pytest.fixture(scope='function')
def test_doctor_user(app, _db):
    """Create a test doctor user"""
    user = User(
        username='doctor_test',
        email='doctor@example.com',
        role='doctor',
        is_active=True
    )
    user.password = 'password'
    _db.session.add(user)
    _db.session.flush()  # Flush to get the user ID
    
    doctor = Doctor(
        user_id=user.id,
        first_name='Test',
        last_name='Doctor',
        specialization='General Medicine',
        phone='1234567890',
        qualification='MD',
        bio='Test doctor bio',
        experience_years=10
    )
    _db.session.add(doctor)
    _db.session.commit()
    return user

@pytest.fixture(scope='function')
def test_doctor(app, _db, test_doctor_user):
    """Return the doctor instance directly for tests that need it"""
    return test_doctor_user.doctor


@pytest.fixture(scope='function')
def test_schedule(app, _db, test_doctor):
    """Create a test schedule for the doctor"""
    today = datetime.now().date()
    
    # Create a schedule for the next 7 days
    schedule = Schedule(
        doctor_id=test_doctor.id,
        day_of_week=today.weekday(),
        start_time=datetime.strptime('09:00', '%H:%M').time(),
        end_time=datetime.strptime('17:00', '%H:%M').time(),
        is_active=True
    )
    _db.session.add(schedule)
    _db.session.commit()
    return schedule


@pytest.fixture(scope='function')
def test_appointment(app, _db, test_patient, test_doctor):
    """Create a test appointment"""
    tomorrow = datetime.now() + timedelta(days=1)
    
    appointment = Appointment(
        patient_id=test_patient.id,
        doctor_id=test_doctor.id,
        appointment_date=tomorrow.date(),
        start_time=datetime.strptime('10:00', '%H:%M').time(),
        end_time=datetime.strptime('10:30', '%H:%M').time(),
        status='confirmed',
        reason='Test appointment reason',
        notes='Test appointment notes'
    )
    _db.session.add(appointment)
    _db.session.commit()
    return appointment


# Medical records functionality has been removed as it was out of scope

@pytest.fixture(scope='function')
def app_with_db(app):
    """Create and configure a Flask app with database for testing"""
    with app.app_context():
        # Create all tables
        db.create_all()
        yield app
        
        # Clean up
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def auth_client(client, test_patient_user):
    """Create a client that's already logged in as a patient"""
    with client.session_transaction() as session:
        # Flask-Login's session format
        session['_user_id'] = str(test_patient_user.id)
        session['_fresh'] = True
    return client


@pytest.fixture(scope='function')
def doctor_auth_client(client, test_doctor_user):
    """Create a client that's already logged in as a doctor"""
    with client.session_transaction() as session:
        # Flask-Login's session format
        session['_user_id'] = str(test_doctor_user.id)
        session['_fresh'] = True
    return client


@pytest.fixture(scope='function')
def admin_auth_client(client, test_admin):
    """Create a client that's already logged in as an admin"""
    with client.session_transaction() as session:
        # Flask-Login's session format
        session['_user_id'] = str(test_admin.id)
        session['_fresh'] = True
    return client