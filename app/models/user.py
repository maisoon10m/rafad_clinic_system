"""
User model for Rafad Clinic System
"""
from datetime import datetime
import secrets
from time import time
import jwt
from flask import current_app
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from . import db


class User(db.Model, UserMixin):
    """User model for authentication and role management"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True, nullable=False)
    email = db.Column(db.String(120), unique=True, index=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='patient')  # 'patient', 'doctor', 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    patient = db.relationship('Patient', backref='user', uselist=False, cascade='all, delete-orphan')
    doctor = db.relationship('Doctor', backref='user', uselist=False, cascade='all, delete-orphan')
    
    @property
    def password(self):
        """Prevent password from being accessed"""
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        """Set password to a hashed password"""
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """Check if password matches the hashed password"""
        return check_password_hash(self.password_hash, password)
    
    def generate_reset_token(self, expires_sec=1800):
        """Generate a token for password reset
        
        Args:
            expires_sec (int): Expiration time in seconds, defaults to 30 minutes
            
        Returns:
            str: Token string
        """
        reset_token = secrets.token_urlsafe(32)
        # In a real application, you would use JWT or another token mechanism
        # and store it in a secure way
        # Here's an example with JWT, commented out as it requires a SECRET_KEY
        # payload = {
        #     'reset_password': self.id,
        #     'exp': time() + expires_sec
        # }
        # return jwt.encode(
        #     payload, 
        #     current_app.config['SECRET_KEY'],
        #     algorithm='HS256'
        # )
        return reset_token
    
    def verify_reset_token(self, token, expires_sec=1800):
        """Verify a password reset token
        
        Args:
            token (str): The token to verify
            expires_sec (int): Expiration time in seconds, defaults to 30 minutes
            
        Returns:
            User: The user object if valid, None otherwise
        """
        # In a real application, you would verify JWT or another token mechanism
        # Here's an example with JWT, commented out as it requires a SECRET_KEY
        # try:
        #     data = jwt.decode(
        #         token,
        #         current_app.config['SECRET_KEY'],
        #         algorithms=['HS256']
        #     )
        #     user_id = data.get('reset_password')
        # except:
        #     return None
        # return User.query.get(user_id)
        
        # For demo purposes, just return self
        return self
    
    def update_last_login(self):
        """Update the last login timestamp"""
        self.last_login = datetime.utcnow()
        db.session.commit()
    
    def __repr__(self):
        return f'<User {self.username}>'