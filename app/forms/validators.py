"""
Custom form validators for Rafad Clinic System
"""
from datetime import datetime, time, date
from wtforms.validators import ValidationError


class DateInFuture(object):
    """
    Validates that a date is in the future
    
    :param allow_today: Whether to allow today's date
    :param message: Error message to display
    """
    
    def __init__(self, allow_today=True, message=None):
        self.allow_today = allow_today
        self.message = message
        
    def __call__(self, form, field):
        if field.data is None:
            return
            
        today = date.today()
        
        if isinstance(field.data, datetime):
            validate_date = field.data.date()
        elif isinstance(field.data, str):
            try:
                # Try to parse string date
                validate_date = datetime.strptime(field.data, '%Y-%m-%d').date()
            except ValueError:
                raise ValidationError("Invalid date format. Use YYYY-MM-DD")
        else:
            validate_date = field.data
            
        if validate_date < today or (validate_date == today and not self.allow_today):
            if self.message is None:
                if self.allow_today:
                    self.message = "Date must be today or in the future"
                else:
                    self.message = "Date must be in the future"
            raise ValidationError(self.message)


class TimeInBusinessHours(object):
    """
    Validates that a time is within business hours
    
    :param start_hour: Start of business hours (24-hour format)
    :param end_hour: End of business hours (24-hour format)
    :param message: Error message to display
    """
    
    def __init__(self, start_hour=8, end_hour=17, message=None):
        self.start_hour = start_hour
        self.end_hour = end_hour
        self.message = message or f"Time must be between {self.start_hour:02d}:00 and {self.end_hour:02d}:00"
        
    def __call__(self, form, field):
        if field.data is None:
            return
            
        if isinstance(field.data, time):
            validate_time = field.data
        else:
            try:
                # Try to parse string to time
                validate_time = datetime.strptime(field.data, "%H:%M").time()
            except (ValueError, TypeError):
                # If we can't parse it, let other validators handle the format error
                return
                
        business_start = time(hour=self.start_hour)
        business_end = time(hour=self.end_hour)
        
        if validate_time < business_start or validate_time > business_end:
            raise ValidationError(self.message)


class EndTimeAfterStartTime(object):
    """
    Validates that the end time is after the start time
    
    :param start_time_field: Name of the start time field
    :param message: Error message to display
    """
    
    def __init__(self, start_time_field, message=None):
        self.start_time_field = start_time_field
        self.message = message or "End time must be after start time"
        
    def __call__(self, form, field):
        if field.data is None:
            return
            
        start_time = getattr(form, self.start_time_field).data
        
        if start_time is None:
            # If start time is not set, we can't validate
            return
            
        if field.data <= start_time:
            raise ValidationError(self.message)


class AppointmentDateTimeValidator(object):
    """
    Combined validator for appointment date and time
    
    Validates that:
    1. The date is not in the past
    2. If the date is today, the time is in the future
    
    :param date_field: Name of the date field
    :param time_field: Name of the time field
    :param message: Error message to display
    """
    
    def __init__(self, date_field, time_field, message=None):
        self.date_field = date_field
        self.time_field = time_field
        self.message = message or "Appointment time must be in the future"
        
    def __call__(self, form, field):
        # This validator can be attached to either the date or time field
        # We just need one of them to trigger the validation
        
        date_field = getattr(form, self.date_field)
        time_field = getattr(form, self.time_field)
        
        if date_field.data is None or time_field.data is None:
            return
            
        today = date.today()
        now = datetime.now().time()
        
        # Convert date_field.data to date object if it's a string
        appointment_date = date_field.data
        if isinstance(appointment_date, str):
            try:
                appointment_date = datetime.strptime(appointment_date, '%Y-%m-%d').date()
            except ValueError:
                raise ValidationError("Invalid date format. Use YYYY-MM-DD.")
        
        # If the date is in the past, no need to check time
        if appointment_date < today:
            raise ValidationError("Appointment date cannot be in the past")
            
        # If the date is today, check that the time is in the future
        appointment_time = time_field.data
        if isinstance(appointment_time, str):
            try:
                appointment_time = datetime.strptime(appointment_time, '%H:%M').time()
            except ValueError:
                raise ValidationError("Invalid time format. Use HH:MM.")
                
        if appointment_date == today and appointment_time <= now:
            raise ValidationError("Appointment time must be in the future")