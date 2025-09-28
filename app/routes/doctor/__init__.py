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
    # Will be implemented in Phase 4
    return render_template('doctor/dashboard.html')


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