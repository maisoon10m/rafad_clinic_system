"""
Utility decorators for Rafad Clinic System
"""
from functools import wraps
from flask import abort
from flask_login import current_user

def role_required(*roles):
    """Decorator to restrict routes to specific user roles"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return abort(401)
            if roles and current_user.role not in roles:
                return abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Decorator to restrict routes to admin users"""
    return role_required('admin')(f)

def doctor_required(f):
    """Decorator to restrict routes to doctor users"""
    return role_required('doctor')(f)

def patient_required(f):
    """Decorator to restrict routes to patient users"""
    return role_required('patient')(f)

def patient_or_doctor_required(f):
    """Decorator to restrict routes to patient or doctor users"""
    return role_required('patient', 'doctor')(f)