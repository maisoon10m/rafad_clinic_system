"""
Tests for Schedule model in Rafad Clinic System
"""
import pytest
from datetime import datetime, timedelta, time
from wtforms.validators import ValidationError
from app.models.schedule import Schedule
from app.models.doctor import Doctor
from app.models.user import User


def test_schedule_creation(_db, test_doctor):
    """Test schedule creation and retrieval"""
    # Create a schedule for Monday
    monday_schedule = Schedule(
        doctor_id=test_doctor.id,
        day_of_week=0,  # Monday
        start_time=datetime.strptime('09:00', '%H:%M').time(),
        end_time=datetime.strptime('17:00', '%H:%M').time(),
        is_active=True
    )
    _db.session.add(monday_schedule)
    _db.session.commit()
    
    # Retrieve the schedule
    retrieved = Schedule.query.filter_by(id=monday_schedule.id).first()
    assert retrieved is not None
    assert retrieved.doctor_id == test_doctor.id
    assert retrieved.day_of_week == 0
    assert retrieved.start_time == datetime.strptime('09:00', '%H:%M').time()
    assert retrieved.end_time == datetime.strptime('17:00', '%H:%M').time()
    assert retrieved.is_active is True


def test_schedule_update(_db, test_doctor):
    """Test updating a schedule"""
    # Create a schedule
    schedule = Schedule(
        doctor_id=test_doctor.id,
        day_of_week=1,  # Tuesday
        start_time=datetime.strptime('08:00', '%H:%M').time(),
        end_time=datetime.strptime('16:00', '%H:%M').time(),
        is_active=True
    )
    _db.session.add(schedule)
    _db.session.commit()
    
    # Update the schedule
    schedule.start_time = datetime.strptime('09:00', '%H:%M').time()
    schedule.end_time = datetime.strptime('17:00', '%H:%M').time()
    schedule.is_active = False
    _db.session.commit()
    
    # Retrieve the updated schedule
    updated = Schedule.query.filter_by(id=schedule.id).first()
    assert updated.start_time == datetime.strptime('09:00', '%H:%M').time()
    assert updated.end_time == datetime.strptime('17:00', '%H:%M').time()
    assert updated.is_active is False


def test_multiple_schedules_per_doctor(_db, test_doctor):
    """Test that a doctor can have multiple schedules"""
    # Create schedules for different days
    schedules = [
        Schedule(
            doctor_id=test_doctor.id,
            day_of_week=day,
            start_time=datetime.strptime('09:00', '%H:%M').time(),
            end_time=datetime.strptime('17:00', '%H:%M').time(),
            is_active=True
        ) for day in range(5)  # Monday to Friday
    ]
    
    _db.session.add_all(schedules)
    _db.session.commit()
    
    # Check that all schedules were created
    doctor_schedules = Schedule.query.filter_by(doctor_id=test_doctor.id).all()
    assert len(doctor_schedules) >= 5
    
    # Check days of week are correct
    days = sorted([s.day_of_week for s in doctor_schedules])
    assert 0 in days  # Monday
    assert 1 in days  # Tuesday
    assert 2 in days  # Wednesday
    assert 3 in days  # Thursday
    assert 4 in days  # Friday


def test_schedule_time_validation(_db, test_doctor):
    """Test schedule with invalid time (end before start)"""
    # Create a schedule with end time before start time
    invalid_schedule = Schedule(
        doctor_id=test_doctor.id,
        day_of_week=0,
        start_time=datetime.strptime('17:00', '%H:%M').time(),
        end_time=datetime.strptime('09:00', '%H:%M').time(),  # Earlier than start time
        is_active=True
    )
    
    _db.session.add(invalid_schedule)
    
    # Since the database doesn't enforce this constraint directly,
    # we'll test it with our validator logic instead
    from app.forms.validators import EndTimeAfterStartTime
    validator = EndTimeAfterStartTime(start_time_field='start_time')
    
    # Mock form and fields for validator
    class MockField:
        def __init__(self, data):
            self.data = data
    
    class MockForm:
        def __init__(self, start_time, end_time):
            self.start_time = MockField(start_time)
            self.end_time = MockField(end_time)
            
    mock_form = MockForm(
        start_time=invalid_schedule.start_time,
        end_time=invalid_schedule.end_time
    )
    
    # Should raise ValidationError
    with pytest.raises(ValidationError):
        validator(mock_form, MockField(invalid_schedule.end_time))
        
    # Clean up
    _db.session.rollback()


def test_doctor_schedule_availability(_db):
    """Test finding available schedules for a doctor"""
    # Create test user with doctor role
    test_user = User(
        username='schedule_test_doctor',
        email='schedule_test@example.com',
        role='doctor'
    )
    test_user.password = 'password123'
    
    _db.session.add(test_user)
    _db.session.flush()
    
    # Create doctor record
    test_doctor = Doctor(
        user_id=test_user.id,
        first_name='Schedule',
        last_name='Test',
        specialization='General Medicine',
        phone='5551234567'
    )
    
    _db.session.add(test_doctor)
    _db.session.flush()
    
    # Create active and inactive schedules
    active_schedule = Schedule(
        doctor_id=test_doctor.id,
        day_of_week=0,  # Monday
        start_time=datetime.strptime('09:00', '%H:%M').time(),
        end_time=datetime.strptime('17:00', '%H:%M').time(),
        is_active=True
    )
    
    inactive_schedule = Schedule(
        doctor_id=test_doctor.id,
        day_of_week=1,  # Tuesday
        start_time=datetime.strptime('09:00', '%H:%M').time(),
        end_time=datetime.strptime('17:00', '%H:%M').time(),
        is_active=False
    )
    
    _db.session.add(active_schedule)
    _db.session.add(inactive_schedule)
    _db.session.commit()
    
    # Get active schedules only
    active_schedules = Schedule.query.filter_by(
        doctor_id=test_doctor.id,
        is_active=True
    ).all()
    
    assert len(active_schedules) == 1
    assert active_schedules[0].day_of_week == 0
    
    # Get all schedules
    all_schedules = Schedule.query.filter_by(doctor_id=test_doctor.id).all()
    assert len(all_schedules) == 2