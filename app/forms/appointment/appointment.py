"""
Form classes for appointment management in Rafad Clinic System
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, TimeField, HiddenField
from wtforms.validators import DataRequired, Optional, Length, ValidationError
from wtforms_sqlalchemy.fields import QuerySelectField
from datetime import datetime, date, time
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.forms.validators import DateInFuture, TimeInBusinessHours, EndTimeAfterStartTime, AppointmentDateTimeValidator


def get_doctors():
    """Return a query of active doctors"""
    return Doctor.query.join(Doctor.user).filter_by(is_active=True).all()


def get_patients():
    """Return a query of active patients"""
    return Patient.query.join(Patient.user).filter_by(is_active=True).all()


class AppointmentForm(FlaskForm):
    """Form for creating and editing appointments"""
    patient_id = QuerySelectField(
        'Patient',
        query_factory=get_patients,
        get_label='full_name',
        get_pk=lambda p: p.id,
        allow_blank=False,
        validators=[DataRequired()]
    )
    
    doctor_id = QuerySelectField(
        'Doctor',
        query_factory=get_doctors,
        get_label=lambda d: f"{d.full_name} ({d.specialization if d.specialization else 'No Specialization'})",
        get_pk=lambda d: d.id,
        allow_blank=False,
        validators=[DataRequired()]
    )
    
    appointment_date = DateField(
        'Date', 
        format='%Y-%m-%d', 
        validators=[
            DataRequired(message="Appointment date is required"),
            DateInFuture(allow_today=True, message="Appointment date must be today or in the future"),
            AppointmentDateTimeValidator('appointment_date', 'appointment_time')
        ]
    )
    
    appointment_time = TimeField(
        'Time', 
        format='%H:%M', 
        validators=[
            DataRequired(message="Appointment time is required"),
            TimeInBusinessHours(start_hour=8, end_hour=17, message="Appointment time must be between 8:00 AM and 5:00 PM"),
            AppointmentDateTimeValidator('appointment_date', 'appointment_time')
        ]
    )
    
    # End time field with validation
    end_time = TimeField(
        'End Time', 
        format='%H:%M', 
        validators=[
            Optional(),
            TimeInBusinessHours(start_hour=8, end_hour=17, message="End time must be between 8:00 AM and 5:00 PM"),
            EndTimeAfterStartTime('appointment_time', message="End time must be after the appointment start time")
        ]
    )
    
    reason = StringField(
        'Reason for Visit', 
        validators=[
            DataRequired(message="Reason for visit is required"), 
            Length(min=3, max=100, message="Reason must be between 3 and 100 characters")
        ]
    )
    
    status = SelectField(
        'Status',
        choices=[
            ('scheduled', 'Scheduled'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
            ('no_show', 'No Show')
        ],
        default='scheduled'
    )
    
    notes = TextAreaField(
        'Notes', 
        validators=[
            Optional(), 
            Length(max=500, message="Notes cannot exceed 500 characters")
        ]
    )


class AppointmentStatusForm(FlaskForm):
    """Form for updating appointment status only"""
    status = SelectField(
        'Status',
        choices=[
            ('scheduled', 'Scheduled'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
            ('no_show', 'No Show')
        ],
        validators=[DataRequired(message="Status selection is required")]
    )
    
    
class AppointmentSearchForm(FlaskForm):
    """Form for searching and filtering appointments"""
    patient_name = StringField(
        'Patient Name', 
        validators=[
            Optional(),
            Length(max=128, message="Patient name search must be less than 128 characters")
        ]
    )
    doctor_id = SelectField('Doctor', coerce=int, validators=[Optional()])
    date_from = DateField(
        'From Date', 
        format='%Y-%m-%d', 
        validators=[Optional()]
    )
    date_to = DateField(
        'To Date', 
        format='%Y-%m-%d', 
        validators=[Optional()]
    )
    status = SelectField(
        'Status',
        choices=[
            ('', 'All Statuses'),
            ('scheduled', 'Scheduled'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
            ('no_show', 'No Show')
        ],
        default='',
        validators=[Optional()]
    )
    
    def validate_date_to(self, field):
        """Validate date_to is after date_from"""
        if field.data and self.date_from.data and field.data < self.date_from.data:
            raise ValidationError('To date must be after or equal to From date')