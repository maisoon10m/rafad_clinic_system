"""
Schedule forms for Rafad Clinic System
"""
from flask_wtf import FlaskForm
from wtforms import SelectField, TimeField, BooleanField, SubmitField, HiddenField
from wtforms.validators import DataRequired, ValidationError
from datetime import time


class ScheduleForm(FlaskForm):
    """Form for managing doctor schedules"""
    day_of_week = SelectField('Day of Week', coerce=int, choices=[
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday')
    ])
    start_time = TimeField('Start Time', validators=[
        DataRequired(message="Start time is required")
    ])
    end_time = TimeField('End Time', validators=[
        DataRequired(message="End time is required")
    ])
    is_available = BooleanField('Available', default=True)
    break_start = TimeField('Break Start (Optional)')
    break_end = TimeField('Break End (Optional)')
    submit = SubmitField('Save Schedule')
    
    def validate_end_time(self, field):
        """Validate end time is after start time"""
        if self.start_time.data and field.data:
            if field.data <= self.start_time.data:
                raise ValidationError('End time must be after start time.')
    
    def validate_break_end(self, field):
        """Validate break end time is after break start time if both are provided"""
        if field.data and self.break_start.data:
            if field.data <= self.break_start.data:
                raise ValidationError('Break end time must be after break start time.')
            if self.start_time.data and field.data <= self.start_time.data:
                raise ValidationError('Break must be within working hours.')
            if self.end_time.data and field.data >= self.end_time.data:
                raise ValidationError('Break must be within working hours.')
    
    def validate_break_start(self, field):
        """Validate break start time is within working hours if provided"""
        if field.data:
            if not self.break_end.data:
                raise ValidationError('Break end time must be provided if break start time is set.')
            if self.start_time.data and field.data <= self.start_time.data:
                raise ValidationError('Break must be within working hours.')
            if self.end_time.data and field.data >= self.end_time.data:
                raise ValidationError('Break must be within working hours.')


class ScheduleDeleteForm(FlaskForm):
    """Form for deleting a schedule"""
    schedule_id = HiddenField(validators=[
        DataRequired(message="Schedule ID is required")
    ])
    submit = SubmitField('Delete Schedule')