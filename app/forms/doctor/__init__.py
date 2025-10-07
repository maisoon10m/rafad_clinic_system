"""
Doctor forms for Rafad Clinic System
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SubmitField, TelField
from wtforms.validators import DataRequired, Length, Optional, NumberRange, Regexp


class DoctorProfileForm(FlaskForm):
    """Form for doctor profile management"""
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
    specialization = StringField('Specialization', validators=[
        DataRequired(message="Specialization is required"), 
        Length(1, 100, message="Specialization must be between 1 and 100 characters"),
        Regexp('^[A-Za-z\s\-&,]+$', message="Specialization should contain only letters, spaces, hyphens, commas, and ampersands")
    ])
    bio = TextAreaField('Biography', validators=[
        Optional(),
        Length(0, 500, message="Bio must be less than 500 characters")
    ])
    phone = TelField('Phone Number', validators=[
        DataRequired(message="Phone number is required"),
        Regexp('^[0-9+\-\s()]{8,20}$', message="Please enter a valid phone number")
    ])
    qualification = StringField('Qualifications', validators=[
        Optional(), 
        Length(0, 128, message="Qualifications must be less than 128 characters")
    ])
    experience_years = IntegerField('Years of Experience', validators=[
        Optional(),
        NumberRange(min=0, max=100, message="Experience must be between 0 and 100 years")
    ])
    submit = SubmitField('Update Profile')