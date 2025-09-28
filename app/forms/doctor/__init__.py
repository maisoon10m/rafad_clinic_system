"""
Doctor forms for Rafad Clinic System
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SubmitField, TelField
from wtforms.validators import DataRequired, Length, Optional, NumberRange


class DoctorProfileForm(FlaskForm):
    """Form for doctor profile management"""
    first_name = StringField('First Name', validators=[
        DataRequired(), 
        Length(1, 64)
    ])
    last_name = StringField('Last Name', validators=[
        DataRequired(), 
        Length(1, 64)
    ])
    specialization = StringField('Specialization', validators=[
        DataRequired(), 
        Length(1, 64)
    ])
    bio = TextAreaField('Biography', validators=[
        Optional()
    ])
    phone = TelField('Phone Number', validators=[
        DataRequired()
    ])
    qualification = StringField('Qualifications', validators=[
        Optional(), 
        Length(0, 128)
    ])
    experience_years = IntegerField('Years of Experience', validators=[
        Optional(),
        NumberRange(min=0, max=100)
    ])
    submit = SubmitField('Update Profile')