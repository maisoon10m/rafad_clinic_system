"""
Tests for database integrity and model relationships in Rafad Clinic System
"""
import pytest
from datetime import datetime
from app.models.user import User
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.appointment import Appointment
from app.models.schedule import Schedule


def test_user_patient_relationship(_db):
    """Test relationship between User and Patient models"""
    # Create test user with patient role
    test_user = User(
        username='test_db_patient',
        email='test_db_patient@example.com',
        role='patient'
    )
    test_user.password = 'password123'
    
    _db.session.add(test_user)
    _db.session.flush()
    
    # Create patient record linked to user
    test_patient = Patient(
        user_id=test_user.id,
        first_name='Test',
        last_name='Database',
        date_of_birth=datetime(1990, 1, 1),
        gender='male',
        phone='1234567890',
        address='123 Test St'
    )
    
    _db.session.add(test_patient)
    _db.session.commit()
    
    # Verify relationship
    assert test_user.patient is not None
    assert test_user.patient.id == test_patient.id
    assert test_patient.user is not None
    assert test_patient.user.id == test_user.id


def test_user_doctor_relationship(_db):
    """Test relationship between User and Doctor models"""
    # Create test user with doctor role
    test_user = User(
        username='test_db_doctor',
        email='test_db_doctor@example.com',
        role='doctor'
    )
    test_user.password = 'password123'
    
    _db.session.add(test_user)
    _db.session.flush()
    
    # Create doctor record linked to user
    test_doctor = Doctor(
        user_id=test_user.id,
        first_name='Test',
        last_name='Doctor',
        specialization='General Medicine',
        phone='0987654321'
    )
    
    _db.session.add(test_doctor)
    _db.session.commit()
    
    # Verify relationship
    assert test_user.doctor is not None
    assert test_user.doctor.id == test_doctor.id
    assert test_doctor.user is not None
    assert test_doctor.user.id == test_user.id


def test_doctor_schedule_relationship(_db):
    """Test relationship between Doctor and Schedule models"""
    # Create test user with doctor role
    test_user = User(
        username='test_schedule_doctor',
        email='test_schedule_doctor@example.com',
        role='doctor'
    )
    test_user.password = 'password123'
    
    _db.session.add(test_user)
    _db.session.flush()
    
    # Create doctor record
    test_doctor = Doctor(
        user_id=test_user.id,
        first_name='Test',
        last_name='Schedule Doctor',
        specialization='General Medicine',
        phone='0987654321'
    )
    
    _db.session.add(test_doctor)
    _db.session.flush()
    
    # Create schedule for the doctor
    test_schedule = Schedule(
        doctor_id=test_doctor.id,
        day_of_week=0,  # Monday
        start_time=datetime.strptime('09:00', '%H:%M').time(),
        end_time=datetime.strptime('17:00', '%H:%M').time(),
        is_active=True
    )
    
    _db.session.add(test_schedule)
    _db.session.commit()
    
    # Verify relationship
    assert test_doctor.schedules.count() == 1
    assert test_doctor.schedules.first().id == test_schedule.id
    assert test_schedule.doctor_id == test_doctor.id
    
    # Check if we can access the doctor from the schedule
    assert test_schedule.doctor is not None
    assert test_schedule.doctor.id == test_doctor.id


def test_appointment_relationships(_db):
    """Test relationships between Appointment, Doctor, and Patient models"""
    # Create test patient user and record
    patient_user = User(
        username='test_appointment_patient',
        email='test_appointment_patient@example.com',
        role='patient'
    )
    patient_user.password = 'password123'
    _db.session.add(patient_user)
    _db.session.flush()
    
    patient = Patient(
        user_id=patient_user.id,
        first_name='Test',
        last_name='Patient',
        date_of_birth=datetime(1990, 1, 1),
        gender='female',
        phone='1234567890'
    )
    _db.session.add(patient)
    
    # Create test doctor user and record
    doctor_user = User(
        username='test_appointment_doctor',
        email='test_appointment_doctor@example.com',
        role='doctor'
    )
    doctor_user.password = 'password123'
    _db.session.add(doctor_user)
    _db.session.flush()
    
    doctor = Doctor(
        user_id=doctor_user.id,
        first_name='Test',
        last_name='Doctor',
        specialization='Cardiology',
        phone='0987654321'
    )
    _db.session.add(doctor)
    _db.session.flush()
    
    # Create an appointment
    tomorrow = datetime.now().date()
    appointment = Appointment(
        patient_id=patient.id,
        doctor_id=doctor.id,
        appointment_date=tomorrow,
        start_time=datetime.strptime('10:00', '%H:%M').time(),
        end_time=datetime.strptime('10:30', '%H:%M').time(),
        status='scheduled',
        reason='Test appointment'
    )
    
    _db.session.add(appointment)
    _db.session.commit()
    
    # Verify relationships
    assert appointment.patient_id == patient.id
    assert appointment.doctor_id == doctor.id
    
    assert appointment.patient is not None
    assert appointment.patient.id == patient.id
    
    assert appointment.doctor is not None
    assert appointment.doctor.id == doctor.id
    
    # Check if we can access appointments from doctor and patient
    assert doctor.appointments.count() == 1
    assert doctor.appointments.first().id == appointment.id
    
    assert patient.appointments.count() == 1
    assert patient.appointments.first().id == appointment.id