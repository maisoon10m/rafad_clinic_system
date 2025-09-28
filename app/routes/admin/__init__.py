"""
Admin routes for Rafad Clinic System
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.decorators import admin_required
from app.models import db, User, Patient, Doctor, Appointment

# Create blueprint
admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Admin dashboard route"""
    stats = {
        'total_patients': Patient.query.count(),
        'total_doctors': Doctor.query.count(),
        'total_appointments': Appointment.query.count(),
        'pending_appointments': Appointment.query.filter_by(status='pending').count()
    }
    return render_template('admin/dashboard.html', stats=stats)


@admin_bp.route('/users')
@login_required
@admin_required
def users():
    """List all users"""
    users = User.query.all()
    return render_template('admin/users.html', users=users)


@admin_bp.route('/doctors')
@login_required
@admin_required
def doctors():
    """List all doctors"""
    doctors = Doctor.query.all()
    return render_template('admin/doctors.html', doctors=doctors)


@admin_bp.route('/patients')
@login_required
@admin_required
def patients():
    """List all patients"""
    patients = Patient.query.all()
    return render_template('admin/patients.html', patients=patients)


@admin_bp.route('/appointments')
@login_required
@admin_required
def appointments():
    """List all appointments"""
    appointments = Appointment.query.all()
    return render_template('admin/appointments.html', appointments=appointments)


@admin_bp.route('/user/<int:user_id>/toggle-active')
@login_required
@admin_required
def toggle_user_active(user_id):
    """Toggle user active status"""
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    flash(f'User {user.username} {"activated" if user.is_active else "deactivated"} successfully.', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/profile')
@login_required
@admin_required
def profile():
    """Admin profile route"""
    # For now, just display the admin dashboard
    return redirect(url_for('admin.dashboard'))