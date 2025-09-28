"""
Patient routes for Rafad Clinic System
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
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
    # Will be implemented in Phase 4
    return render_template('patient/dashboard.html')


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