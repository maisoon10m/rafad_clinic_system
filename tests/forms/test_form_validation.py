"""
Tests for form validations in Rafad Clinic System
"""
import pytest
from datetime import datetime, timedelta
from wtforms.validators import ValidationError
from app.forms.validators import DateInFuture, TimeInBusinessHours, EndTimeAfterStartTime, AppointmentDateTimeValidator
from app.forms.auth import LoginForm, RegistrationForm, PasswordResetRequestForm, PasswordResetForm
from app.forms.appointment.appointment import AppointmentForm
from app.forms.appointment.schedule import ScheduleForm


class TestCustomValidators:
    """Tests for custom form validators"""
    
    def test_date_in_future(self):
        """Test DateInFuture validator"""
        # Create validator instance
        validator = DateInFuture(allow_today=True)
        
        # Create mock field with today's date
        class Field:
            def __init__(self, data):
                self.data = data
        
        today = datetime.now().date()
        tomorrow = today + timedelta(days=1)
        yesterday = today - timedelta(days=1)
        
        today_field = Field(today)
        tomorrow_field = Field(tomorrow)
        yesterday_field = Field(yesterday)
        
        # Test with today's date - should pass
        validator(None, today_field)
        
        # Test with future date - should pass
        validator(None, tomorrow_field)
        
        # Test with past date - should fail
        with pytest.raises(ValidationError):
            validator(None, yesterday_field)
            
        # Test with allow_today=False
        validator = DateInFuture(allow_today=False)
        
        # Today's date should now fail
        with pytest.raises(ValidationError):
            validator(None, today_field)

    def test_time_in_business_hours(self):
        """Test TimeInBusinessHours validator"""
        # Create validator instance
        validator = TimeInBusinessHours(start_hour=9, end_hour=17)
        
        # Create mock fields
        class Field:
            def __init__(self, data):
                self.data = data
        
        # Test times
        before_hours = datetime.strptime('08:00', '%H:%M').time()
        during_hours_start = datetime.strptime('09:00', '%H:%M').time()
        during_hours_middle = datetime.strptime('13:00', '%H:%M').time()
        during_hours_end = datetime.strptime('17:00', '%H:%M').time()
        after_hours = datetime.strptime('18:00', '%H:%M').time()
        
        # Time before business hours should fail
        with pytest.raises(ValidationError):
            validator(None, Field(before_hours))
        
        # Times during business hours should pass
        validator(None, Field(during_hours_start))
        validator(None, Field(during_hours_middle))
        validator(None, Field(during_hours_end))
        
        # Time after business hours should fail
        with pytest.raises(ValidationError):
            validator(None, Field(after_hours))

    def test_end_time_after_start_time(self):
        """Test EndTimeAfterStartTime validator"""
        # Create validator instance
        validator = EndTimeAfterStartTime('start_time')
        
        # Create mock form and fields
        class MockForm:
            def __init__(self):
                self.start_time = None
        
        class Field:
            def __init__(self, data):
                self.data = data
        
        form = MockForm()
        form.start_time = Field(datetime.strptime('10:00', '%H:%M').time())
        
        # End time before start time should fail
        end_time_before = Field(datetime.strptime('09:00', '%H:%M').time())
        with pytest.raises(ValidationError):
            validator(form, end_time_before)
        
        # End time equal to start time should fail
        end_time_equal = Field(datetime.strptime('10:00', '%H:%M').time())
        with pytest.raises(ValidationError):
            validator(form, end_time_equal)
        
        # End time after start time should pass
        end_time_after = Field(datetime.strptime('11:00', '%H:%M').time())
        validator(form, end_time_after)


class TestRegistrationForm:
    """Tests for the RegistrationForm"""
    
    def test_valid_registration_form(self, app):
        """Test with valid data"""
        with app.test_request_context():
            form_data = {
                'first_name': 'John',
                'last_name': 'Doe',
                'username': 'johndoe',
                'email': 'john@example.com',
                'role': 'patient',
                'phone': '1234567890',
                'date_of_birth': '1990-01-01',
                'gender': 'male',
                'password': 'Password1!',
                'confirm_password': 'Password1!'
            }
            
            form = RegistrationForm(**form_data, meta={'csrf': False})
            assert form.validate() is True
    
    def test_password_validation(self, app):
        """Test password validation rules"""
        with app.test_request_context():
            form_data = {
                'first_name': 'John',
                'last_name': 'Doe',
                'username': 'johndoe',
                'email': 'john@example.com',
                'role': 'patient',
                'phone': '1234567890',
                'date_of_birth': '1990-01-01',
                'gender': 'male',
                'password': 'weak',  # Too short and missing requirements
                'confirm_password': 'weak'
            }
            
            form = RegistrationForm(**form_data, meta={'csrf': False})
            assert form.validate() is False
        assert 'password' in form.errors
    
    def test_passwords_must_match(self, app):
        """Test passwords must match validation"""
        with app.test_request_context():
            form_data = {
                'first_name': 'John',
                'last_name': 'Doe',
                'username': 'johndoe',
                'email': 'john@example.com',
                'role': 'patient',
                'phone': '1234567890',
                'date_of_birth': '1990-01-01',
                'gender': 'male',
                'password': 'Password1!',
                'confirm_password': 'DifferentPassword1!'
            }
            
            form = RegistrationForm(**form_data, meta={'csrf': False})
            assert form.validate() is False
            assert 'confirm_password' in form.errors
    
    def test_name_validation(self, app):
        """Test name validation rules"""
        with app.test_request_context():
            form_data = {
                'first_name': 'John123',  # Invalid characters
                'last_name': 'Doe',
                'username': 'johndoe',
                'email': 'john@example.com',
                'role': 'patient',
                'phone': '1234567890',
                'date_of_birth': '1990-01-01',
                'gender': 'male',
                'password': 'Password1!',
                'confirm_password': 'Password1!'
            }
            
            form = RegistrationForm(**form_data, meta={'csrf': False})
            assert form.validate() is False
            assert 'first_name' in form.errors


class TestAppointmentForm:
    """Tests for the AppointmentForm"""
    
    def test_appointment_date_validation(self, app):
        """Test appointment date validation"""
        with app.test_request_context():
            # Create form with past date
            yesterday = datetime.now() - timedelta(days=1)
            form_data = {
                'appointment_date': yesterday.strftime('%Y-%m-%d'),
                'appointment_time': '10:00',
                'reason': 'Test appointment'
            }
            
            form = AppointmentForm(**form_data, meta={'csrf': False})
            assert form.validate() is False
            assert 'appointment_date' in form.errors


class TestScheduleForm:
    """Tests for the ScheduleForm"""
    
    def test_end_time_after_start_time(self, app):
        """Test end time must be after start time"""
        with app.test_request_context():
            # Create form with end time before start time
            form_data = {
                'day_of_week': 1,  # Tuesday
                'start_time': '10:00',
                'end_time': '09:00',  # Before start time
            }
            
            form = ScheduleForm(**form_data, meta={'csrf': False})
            assert form.validate() is False