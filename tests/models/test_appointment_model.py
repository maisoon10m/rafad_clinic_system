"""
Tests for Appointment model in Rafad Clinic System
"""
import pytest
from datetime import datetime, timedelta
from app.models.appointment import Appointment
from app.models.schedule import Schedule


def test_appointment_creation(_db, test_patient, test_doctor):
    """Test creating and retrieving an appointment"""
    tomorrow = datetime.now().date() + timedelta(days=1)
    
    appointment = Appointment(
        patient_id=test_patient.id,
        doctor_id=test_doctor.id,
        appointment_date=tomorrow,
        start_time=datetime.strptime('10:00', '%H:%M').time(),
        end_time=datetime.strptime('10:30', '%H:%M').time(),
        status='scheduled',
        reason='Test appointment reason',
        notes='Test appointment notes'
    )
    _db.session.add(appointment)
    _db.session.commit()
    
    # Retrieve the appointment
    retrieved = Appointment.query.filter_by(id=appointment.id).first()
    assert retrieved is not None
    assert retrieved.patient_id == test_patient.id
    assert retrieved.doctor_id == test_doctor.id
    assert retrieved.appointment_date == tomorrow
    assert retrieved.start_time == datetime.strptime('10:00', '%H:%M').time()
    assert retrieved.status == 'scheduled'


def test_appointment_status_transitions(_db, test_appointment):
    """Test appointment status transitions"""
    # Initial status should be 'confirmed' from the fixture
    assert test_appointment.status == 'confirmed'
    
    # Update status to completed
    test_appointment.status = 'completed'
    _db.session.commit()
    
    # Retrieve the appointment again
    retrieved = Appointment.query.filter_by(id=test_appointment.id).first()
    assert retrieved.status == 'completed'
    
    # Update status to cancelled
    retrieved.status = 'cancelled'
    _db.session.commit()
    
    # Retrieve the appointment once more
    retrieved = Appointment.query.filter_by(id=test_appointment.id).first()
    assert retrieved.status == 'cancelled'


def test_check_availability_no_conflicts(_db, test_doctor, test_patient):
    """Test appointment availability check with no conflicts"""
    tomorrow = datetime.now().date() + timedelta(days=1)
    day_of_week = tomorrow.weekday()
    
    # Create schedule for tomorrow
    schedule = Schedule(
        doctor_id=test_doctor.id,
        day_of_week=day_of_week,
        start_time=datetime.strptime('09:00', '%H:%M').time(),
        end_time=datetime.strptime('17:00', '%H:%M').time(),
        is_active=True
    )
    _db.session.add(schedule)
    _db.session.commit()
    
    # Create a new appointment
    appointment = Appointment(
        patient_id=test_patient.id,
        doctor_id=test_doctor.id,
        appointment_date=tomorrow,
        start_time=datetime.strptime('10:00', '%H:%M').time(),
        end_time=datetime.strptime('10:30', '%H:%M').time()
    )
    
    # Check availability - using the class method properly
    is_available, reason = Appointment.check_availability(
        doctor_id=test_doctor.id,
        date=tomorrow,
        time=datetime.strptime('10:00', '%H:%M').time()
    )
    assert is_available is True


def test_check_availability_with_schedule_conflict(_db, test_doctor, test_patient):
    """Test appointment availability check with schedule conflict"""
    tomorrow = datetime.now().date() + timedelta(days=1)
    day_of_week = tomorrow.weekday()
    
    # Create schedule for tomorrow but with limited hours
    schedule = Schedule(
        doctor_id=test_doctor.id,
        day_of_week=day_of_week,
        start_time=datetime.strptime('13:00', '%H:%M').time(),  # Only afternoon availability
        end_time=datetime.strptime('17:00', '%H:%M').time(),
        is_active=True
    )
    _db.session.add(schedule)
    _db.session.commit()
    
    # Create a morning appointment outside of schedule
    appointment = Appointment(
        patient_id=test_patient.id,
        doctor_id=test_doctor.id,
        appointment_date=tomorrow,
        start_time=datetime.strptime('10:00', '%H:%M').time(),
        end_time=datetime.strptime('10:30', '%H:%M').time()
    )
    
    # Check availability - should fail due to schedule conflict
    is_available, reason = Appointment.check_availability(
        doctor_id=test_doctor.id,
        date=tomorrow,
        time=datetime.strptime('10:00', '%H:%M').time()
    )
    assert is_available is False
    assert "outside of doctor's working hours" in reason
def test_check_availability_with_appointment_conflict(_db, test_doctor, test_patient):
    """Test appointment availability check with existing appointment conflict"""
    tomorrow = datetime.now().date() + timedelta(days=1)
    day_of_week = tomorrow.weekday()
    
    # Create schedule for tomorrow
    schedule = Schedule(
        doctor_id=test_doctor.id,
        day_of_week=day_of_week,
        start_time=datetime.strptime('09:00', '%H:%M').time(),
        end_time=datetime.strptime('17:00', '%H:%M').time(),
        is_active=True
    )
    _db.session.add(schedule)
    
    # Create an existing appointment
    existing_appointment = Appointment(
        patient_id=test_patient.id,
        doctor_id=test_doctor.id,
        appointment_date=tomorrow,
        start_time=datetime.strptime('10:00', '%H:%M').time(),
        end_time=datetime.strptime('10:30', '%H:%M').time(),
        status='scheduled'
    )
    _db.session.add(existing_appointment)
    _db.session.commit()
    
    # Create a conflicting appointment
    appointment = Appointment(
        patient_id=test_patient.id,
        doctor_id=test_doctor.id,
        appointment_date=tomorrow,
        start_time=datetime.strptime('10:15', '%H:%M').time(),
        end_time=datetime.strptime('10:45', '%H:%M').time()
    )
    
    # Check availability - should fail due to appointment conflict
    is_available, reason = Appointment.check_availability(
        doctor_id=test_doctor.id,
        date=tomorrow,
        time=datetime.strptime('10:15', '%H:%M').time()
    )
    assert is_available is False
    assert "conflicts with existing appointment" in reason
    
    # Create a non-conflicting appointment
    appointment = Appointment(
        patient_id=test_patient.id,
        doctor_id=test_doctor.id,
        appointment_date=tomorrow,
        start_time=datetime.strptime('11:00', '%H:%M').time(),
        end_time=datetime.strptime('11:30', '%H:%M').time()
    )
    
    # Check availability - should succeed
    is_available, reason = Appointment.check_availability(
        doctor_id=test_doctor.id,
        date=tomorrow,
        time=datetime.strptime('11:00', '%H:%M').time()
    )
    assert is_available is True
    assert reason is None


def test_appointment_in_past(_db, test_doctor, test_patient):
    """Test that appointments cannot be created in the past"""
    yesterday = datetime.now().date() - timedelta(days=1)
    
    # Create an appointment for yesterday
    appointment = Appointment(
        patient_id=test_patient.id,
        doctor_id=test_doctor.id,
        appointment_date=yesterday,
        start_time=datetime.strptime('10:00', '%H:%M').time(),
        end_time=datetime.strptime('10:30', '%H:%M').time()
    )
    
    # Check availability - should fail due to past date
    is_available, reason = Appointment.check_availability(
        doctor_id=test_doctor.id,
        date=yesterday,
        time=datetime.strptime('10:00', '%H:%M').time()
    )
    assert is_available is False