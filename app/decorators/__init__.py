"""
Decorators for role-based access control in Rafad Clinic System
"""
from functools import wraps
from flask import abort, flash, redirect, url_for, request
from flask_login import current_user


def role_required(role):
    """Decorator for views that require a specific role
    
    Args:
        role (str or list): The required role(s) for access
    
    Returns:
        function: The decorated function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('auth.login', next=request.url))
            
            if isinstance(role, list):
                if current_user.role not in role:
                    abort(403)
            else:
                if current_user.role != role:
                    abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """Decorator for views that require admin access"""
    return role_required('admin')(f)


def doctor_required(f):
    """Decorator for views that require doctor access"""
    return role_required('doctor')(f)


def patient_required(f):
    """Decorator for views that require patient access"""
    return role_required('patient')(f)


def staff_required(f):
    """Decorator for views that require staff access (admin or doctor)"""
    return role_required(['admin', 'doctor'])(f)