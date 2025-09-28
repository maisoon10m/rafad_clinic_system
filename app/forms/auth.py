"""
Forms for authentication in Rafad Clinic System
"""
from flask_wtf import FlaskForm
from wtforms import (
    StringField, PasswordField, BooleanField, SubmitField,
    TextAreaField, SelectField, DateField, TelField
)
from wtforms.validators import (
    DataRequired, Length, Email, Regexp, EqualTo, 
    ValidationError, Optional
)
from datetime import date
from app.models import User


class LoginForm(FlaskForm):
    """Login form for user authentication"""
    email = StringField('Email', validators=[
        DataRequired(), 
        Email(),
        Length(1, 120)
    ])
    password = PasswordField('Password', validators=[
        DataRequired()
    ])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    """Registration form for new patients"""
    first_name = StringField('First Name', validators=[
        DataRequired(), 
        Length(1, 64)
    ])
    last_name = StringField('Last Name', validators=[
        DataRequired(), 
        Length(1, 64)
    ])
    username = StringField('Username', validators=[
        DataRequired(),
        Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Username must start with a letter and can only contain '
               'letters, numbers, dots or underscores')
    ])
    email = StringField('Email', validators=[
        DataRequired(), 
        Email(),
        Length(1, 120)
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
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(8, 128),
        Regexp('^(?=.*[A-Za-z])(?=.*\\d)(?=.*[@$!%*#?&])[A-Za-z\\d@$!%*#?&]{8,}$',
               message='Password must contain at least one letter, one number, and one special character')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Register')

    def validate_username(self, field):
        """Validate username is unique"""
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')

    def validate_email(self, field):
        """Validate email is unique"""
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')
            
    def validate_date_of_birth(self, field):
        """Validate date of birth is in the past"""
        if field.data > date.today():
            raise ValidationError('Date of birth must be in the past.')


class PasswordResetRequestForm(FlaskForm):
    """Form for requesting password reset"""
    email = StringField('Email', validators=[
        DataRequired(), 
        Email(),
        Length(1, 120)
    ])
    submit = SubmitField('Reset Password')


class PasswordResetForm(FlaskForm):
    """Form for resetting password with token"""
    password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(8, 128),
        Regexp('^(?=.*[A-Za-z])(?=.*\\d)(?=.*[@$!%*#?&])[A-Za-z\\d@$!%*#?&]{8,}$',
               message='Password must contain at least one letter, one number, and one special character')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Reset Password')