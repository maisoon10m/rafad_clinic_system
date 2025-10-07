"""
Forms for authentication in Rafad Clinic System
"""
from datetime import date, datetime
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
from app.models import User, db


class LoginForm(FlaskForm):
    """Login form for user authentication"""
    email = StringField('Email', validators=[
        DataRequired(message="Email is required"), 
        Email(message="Please enter a valid email address"),
        Length(1, 120, message="Email must be between 1 and 120 characters")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Password is required")
    ])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    """Registration form with role selection"""
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
    username = StringField('Username', validators=[
        DataRequired(message="Username is required"),
        Length(3, 64, message="Username must be between 3 and 64 characters"),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Username must start with a letter and can only contain '
               'letters, numbers, dots or underscores')
    ])
    email = StringField('Email', validators=[
        DataRequired(), 
        Email(),
        Length(1, 120)
    ])
    role = SelectField('Register as', choices=[
        ('patient', 'Patient'), 
        ('doctor', 'Doctor')
    ])
    phone = TelField('Phone Number', validators=[
        DataRequired()
    ])
    date_of_birth = DateField('Date of Birth', validators=[
        DataRequired()
    ])
    gender = SelectField('Gender', choices=[
        ('male', 'Male'), 
        ('female', 'Female')
    ])
    # Doctor-specific fields
    specialization = StringField('Specialization (For Doctors Only)', validators=[
        Optional(),
        Length(0, 100)
    ])
    qualification = StringField('Qualification (For Doctors Only)', validators=[
        Optional(),
        Length(0, 100)
    ])
    experience_years = StringField('Years of Experience (For Doctors Only)', validators=[
        Optional(),
        Regexp('^[0-9]*$', message='Must be a number')
    ])
    bio = TextAreaField('Bio (For Doctors Only)', validators=[
        Optional(),
        Length(0, 500)
    ])
    # Patient fields
    address = TextAreaField('Address', validators=[
        Optional(), 
        Length(0, 256)
    ])
    medical_history = TextAreaField('Medical History (Optional)', validators=[
        Optional(),
        Length(0, 1000)
    ])
    # Common fields
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
            
    def validate_role(self, field):
        """Validate role selection"""
        if field.data not in ['patient', 'doctor']:
            raise ValidationError('Invalid role selected.')
            
        # If doctor role is selected, ensure doctor-specific fields are provided
        if field.data == 'doctor' and not self.specialization.data:
            raise ValidationError('Specialization is required for doctors.')


class PasswordResetRequestForm(FlaskForm):
    """Form for requesting password reset"""
    email = StringField('Email', validators=[
        DataRequired(message="Email is required"), 
        Email(message="Please enter a valid email address"),
        Length(5, 120, message="Email must be between 5 and 120 characters")
    ])
    submit = SubmitField('Reset Password')
    
    def validate_email(self, field):
        """Validate email exists in the system"""
        user = User.query.filter_by(email=field.data).first()
        if not user:
            raise ValidationError('No account found with that email address.')


class PasswordResetForm(FlaskForm):
    """Form for resetting password with token"""
    password = PasswordField('New Password', validators=[
        DataRequired(message="New password is required"),
        Length(8, 128, message="Password must be at least 8 characters long"),
        Regexp('^(?=.*[A-Za-z])(?=.*\\d)(?=.*[@$!%*#?&])[A-Za-z\\d@$!%*#?&]{8,}$',
               message='Password must contain at least one letter, one number, and one special character')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message="Please confirm your new password"),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Reset Password')