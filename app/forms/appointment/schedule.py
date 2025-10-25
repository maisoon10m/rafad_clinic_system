"""
Form classes for schedule management in Rafad Clinic System
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, IntegerField, TimeField, BooleanField
from wtforms.validators import DataRequired, Optional, Length, NumberRange
from wtforms_sqlalchemy.fields import QuerySelectField
from app.models.doctor import Doctor
from app.forms.validators import TimeInBusinessHours, EndTimeAfterStartTime


def get_doctors():
    """Return a query of active doctors"""
    return Doctor.query.join(Doctor.user).filter_by(is_active=True).all()


class ScheduleForm(FlaskForm):
    """Form for creating and editing doctor schedules"""
    doctor_id = QuerySelectField(
        'Doctor',
        query_factory=get_doctors,
        get_label=lambda d: f"{d.full_name} ({d.specialization if d.specialization else 'No Specialization'})",
        get_pk=lambda d: d.id,
        allow_blank=False,
        validators=[DataRequired()]
    )
    
    day_of_week = SelectField(
        'Day of Week',
        choices=[
            (0, 'Monday'),
            (1, 'Tuesday'),
            (2, 'Wednesday'),
            (3, 'Thursday'),
            (4, 'Friday'),
            (5, 'Saturday'),
            (6, 'Sunday')
        ],
        coerce=int,
        validators=[DataRequired()]
    )
    
    start_time = TimeField(
        'Start Time', 
        format='%H:%M', 
        validators=[
            DataRequired(message="Start time is required"),
            TimeInBusinessHours(start_hour=8, end_hour=17, message="Start time must be between 8:00 AM and 5:00 PM")
        ]
    )
    end_time = TimeField(
        'End Time', 
        format='%H:%M', 
        validators=[
            DataRequired(message="End time is required"),
            TimeInBusinessHours(start_hour=8, end_hour=17, message="End time must be between 8:00 AM and 5:00 PM"),
            EndTimeAfterStartTime('start_time', message="End time must be after start time")
        ]
    )
    
    appointment_duration = IntegerField(
        'Appointment Duration (minutes)', 
        validators=[
            DataRequired(message="Appointment duration is required"),
            NumberRange(min=5, max=240, message="Appointment duration must be between 5 and 240 minutes")
        ],
        default=30
    )
    
    break_duration = IntegerField(
        'Break Duration (minutes)', 
        validators=[
            Optional(),
            NumberRange(min=0, max=60, message="Break duration must be between 0 and 60 minutes")
        ],
        default=0
    )
    
    is_active = BooleanField('Active Schedule', default=True)
    
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=500)])
    
    
class ScheduleSearchForm(FlaskForm):
    """Form for searching and filtering schedules"""
    doctor_id = SelectField('Doctor', coerce=int, validators=[
        Optional(strip_whitespace=True)
    ])
    day_of_week = SelectField(
        'Day of Week',
        choices=[
            ('', 'All Days'),
            ('0', 'Monday'),
            ('1', 'Tuesday'),
            ('2', 'Wednesday'),
            ('3', 'Thursday'),
            ('4', 'Friday'),
            ('5', 'Saturday'),
            ('6', 'Sunday')
        ],
        validators=[
            Optional(strip_whitespace=True)
        ]
    )
    status = SelectField(
        'Status',
        choices=[
            ('', 'All Statuses'),
            ('active', 'Active'),
            ('inactive', 'Inactive')
        ],
        validators=[
            Optional(strip_whitespace=True)
        ]
    )