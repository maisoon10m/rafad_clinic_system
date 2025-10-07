"""
Patient forms for Rafad Clinic System
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, SelectField, SubmitField, TelField
from wtforms.validators import DataRequired, Length, Optional, ValidationError, Regexp
from datetime import date, datetime


class PatientProfileForm(FlaskForm):
    """Form for patient profile management"""
    first_name = StringField('First Name', validators=[
        DataRequired(message="First name is required"), 
        Length(1, 64, message="First name must be between 1 and 64 characters"),
        Regexp('^[A-Za-z\s\-]+$', message="First name should contain only letters, spaces, and hyphens")
    ])
    last_name = StringField('Last Name', validators=[
        DataRequired(message="Last name is required"), 
        Length(1, 64, message="Last name must be between 1 and 64 characters"),
        Regexp('^[A-Za-z\s\-]+$', message="Last name should contain only letters, spaces, and hyphens")
    ])
    phone = TelField('Phone Number', validators=[
        DataRequired(message="Phone number is required"),
        Regexp('^[0-9+\-\s()]{8,20}$', message="Please enter a valid phone number")
    ])
    date_of_birth = DateField('Date of Birth', validators=[
        DataRequired(message="Date of birth is required")
    ])
    gender = SelectField('Gender', choices=[
        ('male', 'Male'), 
        ('female', 'Female'),
        ('other', 'Other'),
        ('prefer_not_to_say', 'Prefer not to say')
    ], validators=[
        DataRequired(message="Please select a gender")
    ])
    address = TextAreaField('Address', validators=[
        Optional(), 
        Length(0, 256, message="Address must be less than 256 characters")
    ])
    medical_history = TextAreaField('Medical History', validators=[
        Optional(),
        Length(0, 1000, message="Medical history must be less than 1000 characters")
    ])
    submit = SubmitField('Update Profile')
    
    def validate_date_of_birth(self, field):
        """Validate date of birth is in the past"""
        # Handle both string and date object
        if isinstance(field.data, str):
            try:
                # Try to parse the date string
                date_value = datetime.strptime(field.data, '%Y-%m-%d').date()
            except ValueError:
                raise ValidationError('Invalid date format. Use YYYY-MM-DD.')
        else:
            date_value = field.data
            
        if date_value > date.today():
            raise ValidationError('Date of birth must be in the past.')