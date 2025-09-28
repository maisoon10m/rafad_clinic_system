"""
Patient routes for Rafad Clinic System
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy import text
from app.decorators import patient_required
from app.models import db, Patient
from app.forms.patient import PatientProfileForm

# Create blueprint
patient_bp = Blueprint('patient', __name__)


@patient_bp.route('/dashboard')
@login_required
@patient_required
def dashboard():
    """Patient dashboard route"""
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        flash('Patient profile not found.', 'danger')
        return redirect(url_for('patient.profile'))
    
    # Get upcoming appointments
    upcoming_appointments = patient.appointments.filter_by(status='booked').order_by(
        text('appointment_date'), text('appointment_time')).all()
    
    # Get past appointments
    past_appointments = patient.appointments.filter(
        patient.appointments.status.in_(['completed', 'cancelled'])
    ).order_by(text('appointment_date'), text('appointment_time')).all()
    
    return render_template('patient/dashboard.html', 
                           patient=patient,
                           upcoming_appointments=upcoming_appointments,
                           past_appointments=past_appointments)


@patient_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@patient_required
def profile():
    """Patient profile route"""
    patient = Patient.query.filter_by(user_id=current_user.id).first()
    if not patient:
        flash('Patient profile not found.', 'danger')
        return redirect(url_for('main.index'))
    
    form = PatientProfileForm(obj=patient)
    if form.validate_on_submit():
        form.populate_obj(patient)
        db.session.commit()
        flash('Your profile has been updated.', 'success')
        return redirect(url_for('patient.profile'))
    
    return render_template('patient/profile.html', form=form)