"""
Doctor routes for Rafad Clinic System
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app.decorators import doctor_required
from app.models import db, Doctor
from app.forms.doctor import DoctorProfileForm

# Create blueprint
doctor_bp = Blueprint('doctor', __name__)


@doctor_bp.route('/dashboard')
@login_required
@doctor_required
def dashboard():
    """Doctor dashboard route"""
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    if not doctor:
        flash('Doctor profile not found.', 'danger')
        return redirect(url_for('doctor.profile'))
    
    # Get today's appointments
    from datetime import date, datetime
    today = date.today()
    todays_appointments = doctor.appointments.filter_by(
        appointment_date=today, status='booked'
    ).order_by('start_time').all()
    
    # Get upcoming appointments (not today)
    upcoming_appointments = doctor.appointments.filter(
        doctor.appointments.appointment_date > today,
        doctor.appointments.status == 'booked'
    ).order_by('appointment_date', 'start_time').all()
    
    # Get all schedules for this doctor
    schedules = doctor.schedules.order_by('day_of_week', 'start_time').all()
    
    return render_template('doctor/dashboard.html',
                          doctor=doctor,
                          todays_appointments=todays_appointments,
                          upcoming_appointments=upcoming_appointments,
                          schedules=schedules)


@doctor_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@doctor_required
def profile():
    """Doctor profile route"""
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    if not doctor:
        flash('Doctor profile not found.', 'danger')
        return redirect(url_for('main.index'))
    
    form = DoctorProfileForm(obj=doctor)
    if form.validate_on_submit():
        form.populate_obj(doctor)
        db.session.commit()
        flash('Your profile has been updated.', 'success')
        return redirect(url_for('doctor.profile'))
    
    return render_template('doctor/profile.html', form=form)