"""
Form classes for schedule management in Rafad Clinic System
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, IntegerField, TimeField, BooleanField
from wtforms.validators import DataRequired, Optional, Length, NumberRange
from wtforms_sqlalchemy.fields import QuerySelectField
from app.models.doctor import Doctor


def get_doctors():
    """Return a query of active doctors"""
    return Doctor.query.join(Doctor.user).filter_by(is_active=True).all()


class ScheduleForm(FlaskForm):
    """Form for creating and editing doctor schedules"""
    doctor_id = QuerySelectField(
        'Doctor',
        query_factory=get_doctors,
        get_label=lambda d: f"{d.full_name} ({d.department.name if d.department else 'No Department'})",
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
    
    start_time = TimeField('Start Time', format='%H:%M', validators=[DataRequired()])
    end_time = TimeField('End Time', format='%H:%M', validators=[DataRequired()])
    
    appointment_duration = IntegerField(
        'Appointment Duration', 
        validators=[DataRequired(), NumberRange(min=5, max=240)],
        default=30
    )
    
    break_duration = IntegerField(
        'Break Duration', 
        validators=[Optional(), NumberRange(min=0, max=60)],
        default=0
    )
    
    is_active = BooleanField('Active Schedule', default=True)
    
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=500)])
    
    
class ScheduleSearchForm(FlaskForm):
    """Form for searching and filtering schedules"""
    doctor_id = SelectField('Doctor', coerce=int, validators=[Optional()])
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
        validators=[Optional()]
    )
    status = SelectField(
        'Status',
        choices=[
            ('', 'All Statuses'),
            ('active', 'Active'),
            ('inactive', 'Inactive')
        ],
        validators=[Optional()]
    )