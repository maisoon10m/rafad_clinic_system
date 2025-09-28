"""
Patient forms for Rafad Clinic System
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, SelectField, SubmitField, TelField
from wtforms.validators import DataRequired, Length, Optional, ValidationError
from datetime import date


class PatientProfileForm(FlaskForm):
    """Form for patient profile management"""
    first_name = StringField('First Name', validators=[
        DataRequired(), 
        Length(1, 64)
    ])
    last_name = StringField('Last Name', validators=[
        DataRequired(), 
        Length(1, 64)
    ])
    phone = TelField('Phone Number', validators=[
        DataRequired()
    ])
    date_of_birth = DateField('Date of Birth', validators=[
        DataRequired()
    ])
    gender = SelectField('Gender', choices=[
        ('male', 'Male'), 
        ('female', 'Female'), 
        ('other', 'Other')
    ])
    address = TextAreaField('Address', validators=[
        Optional(), 
        Length(0, 256)
    ])
    medical_history = TextAreaField('Medical History', validators=[
        Optional()
    ])
    submit = SubmitField('Update Profile')
    
    def validate_date_of_birth(self, field):
        """Validate date of birth is in the past"""
        if field.data > date.today():
            raise ValidationError('Date of birth must be in the past.')