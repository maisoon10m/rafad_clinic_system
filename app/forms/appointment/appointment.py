"""
Form classes for appointment management in Rafad Clinic System
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, TimeField, HiddenField
from wtforms.validators import DataRequired, Optional, Length
from wtforms_sqlalchemy.fields import QuerySelectField
from app.models.doctor import Doctor
from app.models.patient import Patient


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
        get_label=lambda d: f"{d.full_name} ({d.department.name if d.department else 'No Department'})",
        get_pk=lambda d: d.id,
        allow_blank=False,
        validators=[DataRequired()]
    )
    
    appointment_date = DateField('Date', format='%Y-%m-%d', validators=[DataRequired()])
    appointment_time = TimeField('Time', format='%H:%M', validators=[DataRequired()])
    
    reason = StringField('Reason for Visit', validators=[DataRequired(), Length(min=3, max=100)])
    
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
    
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=500)])


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
        validators=[DataRequired()]
    )
    
    
class AppointmentSearchForm(FlaskForm):
    """Form for searching and filtering appointments"""
    patient_name = StringField('Patient Name', validators=[Optional()])
    doctor_id = SelectField('Doctor', coerce=int, validators=[Optional()])
    date_from = DateField('From Date', format='%Y-%m-%d', validators=[Optional()])
    date_to = DateField('To Date', format='%Y-%m-%d', validators=[Optional()])
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