"""
Tests for Doctor model in Rafad Clinic System
"""
import pytest
from datetime import datetime, timedelta
from app.models.doctor import Doctor
from app.models.user import User
from app.models.schedule import Schedule
from app.models.appointment import Appointment


def test_doctor_creation(_db, test_doctor):
    """Test that a doctor can be created and retrieved from DB"""
    assert test_doctor is not None
    assert test_doctor.first_name == 'Test'
    assert test_doctor.last_name == 'Doctor'
    assert test_doctor.specialization == 'General Medicine'
    
    # Test doctor was properly added to DB
    doctor_from_db = Doctor.query.filter_by(id=test_doctor.id).first()
    assert doctor_from_db is not None
    assert doctor_from_db.id == test_doctor.id


def test_doctor_full_name(test_doctor):
    """Test the full_name property of a doctor"""
    assert test_doctor.full_name == 'Dr. Test Doctor'


def test_doctor_is_available_no_schedule(_db):
    """Test availability check for a doctor with no schedule"""
    # Create a new doctor with no schedule
    user = User(username='newdoc', email='newdoc@example.com', role='doctor')
    user.password = 'password'
    _db.session.add(user)
    _db.session.flush()
    
    doctor = Doctor(
        user_id=user.id,
        first_name='New',
        last_name='Doctor',
        specialization='Pediatrics'
    )
    _db.session.add(doctor)
    _db.session.commit()
    
    # Doctor should not be available without a schedule
    check_date = datetime.now().date()
    check_time_start = datetime.strptime('14:00', '%H:%M').time()
    check_time_end = datetime.strptime('14:30', '%H:%M').time()
    
    is_available, reason = doctor.is_available(check_date, check_time_start, check_time_end)
    assert is_available is False
    assert "does not have office hours" in reason


def test_doctor_is_available_with_schedule(_db, test_doctor):
    """Test availability check for a doctor with a schedule"""
    today = datetime.now().date()
    day_of_week = today.weekday()
    
    # Create a schedule for today
    schedule = Schedule(
        doctor_id=test_doctor.id,
        day_of_week=day_of_week,
        start_time=datetime.strptime('09:00', '%H:%M').time(),
        end_time=datetime.strptime('17:00', '%H:%M').time(),
        is_active=True
    )
    _db.session.add(schedule)
    _db.session.commit()
    
    # Doctor should be available during schedule hours
    start_time = datetime.strptime('10:00', '%H:%M').time()
    end_time = datetime.strptime('10:30', '%H:%M').time()
    is_available, reason = test_doctor.is_available(today, start_time, end_time)
    assert is_available is True
    assert reason is None
    
    # Doctor should not be available outside schedule hours
    start_time = datetime.strptime('08:00', '%H:%M').time()
    end_time = datetime.strptime('08:30', '%H:%M').time()
    is_available, reason = test_doctor.is_available(today, start_time, end_time)
    assert is_available is False
    assert "outside of doctor's working hours" in reason
    
    start_time = datetime.strptime('18:00', '%H:%M').time()
    end_time = datetime.strptime('18:30', '%H:%M').time()
    is_available, reason = test_doctor.is_available(today, start_time, end_time)
    assert is_available is False
    assert "outside of doctor's working hours" in reason


def test_doctor_is_available_with_appointment(_db, test_doctor, test_patient):
    """Test availability check for a doctor with existing appointments"""
    today = datetime.now().date()
    day_of_week = today.weekday()
    
    # Create a schedule for today
    schedule = Schedule(
        doctor_id=test_doctor.id,
        day_of_week=day_of_week,
        start_time=datetime.strptime('09:00', '%H:%M').time(),
        end_time=datetime.strptime('17:00', '%H:%M').time(),
        is_active=True
    )
    _db.session.add(schedule)
    
    # Create an appointment for today at 11:00-11:30
    appointment = Appointment(
        doctor_id=test_doctor.id,
        patient_id=test_patient.id,
        appointment_date=today,
        start_time=datetime.strptime('11:00', '%H:%M').time(),
        end_time=datetime.strptime('11:30', '%H:%M').time(),
        status='scheduled',
        reason='Test appointment'
    )
    _db.session.add(appointment)
    _db.session.commit()
    
    # Doctor should be available at 10:00-10:30
    start_time = datetime.strptime('10:00', '%H:%M').time()
    end_time = datetime.strptime('10:30', '%H:%M').time()
    is_available, reason = test_doctor.is_available(today, start_time, end_time)
    assert is_available is True
    assert reason is None
    
    # Doctor should not be available at 11:00-11:30 (has appointment)
    start_time = datetime.strptime('11:00', '%H:%M').time()
    end_time = datetime.strptime('11:30', '%H:%M').time()
    is_available, reason = test_doctor.is_available(today, start_time, end_time)
    assert is_available is False
    assert "conflicting appointment" in reason
    
    # Doctor should not be available at 11:15-11:45 (overlaps with appointment)
    start_time = datetime.strptime('11:15', '%H:%M').time()
    end_time = datetime.strptime('11:45', '%H:%M').time()
    is_available, reason = test_doctor.is_available(today, start_time, end_time)
    assert is_available is False
    assert "conflicting appointment" in reason
    
    # Doctor should be available at 11:30-12:00 (after appointment ends)
    start_time = datetime.strptime('11:30', '%H:%M').time()
    end_time = datetime.strptime('12:00', '%H:%M').time()
    is_available, reason = test_doctor.is_available(today, start_time, end_time)
    assert is_available is True
    assert reason is None


def test_doctor_is_available_for_date_without_schedule(_db, test_doctor):
    """Test doctor is not available for date without a schedule"""
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)
    day_of_week = today.weekday()
    
    # Create a schedule for today only
    schedule = Schedule(
        doctor_id=test_doctor.id,
        day_of_week=day_of_week,
        start_time=datetime.strptime('09:00', '%H:%M').time(),
        end_time=datetime.strptime('17:00', '%H:%M').time(),
        is_active=True
    )
    _db.session.add(schedule)
    _db.session.commit()
    
    # Doctor should be available today during schedule hours
    start_time = datetime.strptime('10:00', '%H:%M').time()
    end_time = datetime.strptime('10:30', '%H:%M').time()
    is_available, reason = test_doctor.is_available(today, start_time, end_time)
    assert is_available is True
    assert reason is None
    
    # Doctor should not be available tomorrow (no schedule)
    is_available, reason = test_doctor.is_available(tomorrow, start_time, end_time)
    assert is_available is False
    assert "does not have office hours" in reason