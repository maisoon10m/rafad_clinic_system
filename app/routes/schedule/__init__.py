"""
Schedule routes for Rafad Clinic System
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_required, current_user
from app.decorators import doctor_required, admin_required
from app.models import db, Schedule, Doctor, Appointment
from app.forms.schedule import ScheduleForm, ScheduleDeleteForm
from datetime import datetime, time

# Create blueprint
schedule_bp = Blueprint('schedule', __name__)


@schedule_bp.route('/manage')
@login_required
@doctor_required
def manage():
    """Manage schedules for the logged-in doctor"""
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    if not doctor:
        flash('Doctor profile not found.', 'danger')
        return redirect(url_for('doctor.profile'))
    
    schedules = Schedule.query.filter_by(doctor_id=doctor.id).order_by(Schedule.day_of_week, Schedule.start_time).all()
    
    return render_template('schedule/weekly_manage.html', schedules=schedules)


@schedule_bp.route('/add', methods=['GET', 'POST'])
@login_required
@doctor_required
def add():
    """Add a new schedule for the logged-in doctor"""
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    if not doctor:
        flash('Doctor profile not found.', 'danger')
        return redirect(url_for('doctor.profile'))
    
    form = ScheduleForm()
    
    # Pre-select day if provided in query parameter
    if request.method == 'GET':
        day = request.args.get('day', type=int)
        if day is not None and 0 <= day <= 6:
            form.day_of_week.data = day
    
    if form.validate_on_submit():
        # Check for overlapping schedules
        existing_schedule = Schedule.query.filter_by(
            doctor_id=doctor.id,
            day_of_week=form.day_of_week.data
        ).filter(
            (Schedule.start_time <= form.end_time.data) &
            (Schedule.end_time >= form.start_time.data)
        ).first()
        
        if existing_schedule:
            flash('This schedule overlaps with an existing schedule for the same day.', 'danger')
            return render_template('schedule/create.html', form=form)
        
        new_schedule = Schedule(
            doctor_id=doctor.id,
            day_of_week=form.day_of_week.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            is_active=form.is_available.data if hasattr(form, 'is_available') else True
        )
        
        db.session.add(new_schedule)
        db.session.commit()
        flash('Schedule added successfully.', 'success')
        return redirect(url_for('schedule.manage'))
    
    return render_template('schedule/create.html', form=form)


@schedule_bp.route('/edit/<int:schedule_id>', methods=['GET', 'POST'])
@login_required
@doctor_required
def edit(schedule_id):
    """Edit a schedule"""
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    if not doctor:
        flash('Doctor profile not found.', 'danger')
        return redirect(url_for('doctor.profile'))
    
    schedule = Schedule.query.get_or_404(schedule_id)
    
    # Ensure doctor can only edit their own schedule
    if schedule.doctor_id != doctor.id:
        abort(403)  # Forbidden
    
    form = ScheduleForm()
    
    # Manually populate form fields on GET request
    if request.method == 'GET':
        form.day_of_week.data = schedule.day_of_week
        form.start_time.data = schedule.start_time
        form.end_time.data = schedule.end_time
        if hasattr(form, 'is_available'):
            form.is_available.data = schedule.is_active
        if hasattr(form, 'break_start') and hasattr(schedule, 'break_start'):
            form.break_start.data = schedule.break_start
        if hasattr(form, 'break_end') and hasattr(schedule, 'break_end'):
            form.break_end.data = schedule.break_end
    
    if form.validate_on_submit():
        # Check for overlapping schedules
        overlapping = Schedule.query.filter_by(
            doctor_id=doctor.id,
            day_of_week=form.day_of_week.data
        ).filter(
            (Schedule.start_time <= form.end_time.data) &
            (Schedule.end_time >= form.start_time.data) &
            (Schedule.id != schedule_id)  # Exclude the current schedule
        ).first()
        
        if overlapping:
            flash('This schedule overlaps with another schedule for the same day.', 'danger')
            return render_template('schedule/edit.html', form=form, schedule=schedule)
        
        # Check for appointments affected by this schedule change
        affected_appointments = Appointment.query.filter_by(
            doctor_id=doctor.id,
            status='booked'
        ).filter(
            # Appointments on the scheduled day of week
            # Will need to check this in the template (can't filter by day of week directly)
        ).all()
        
        # For now just warn about potential conflicts
        if affected_appointments:
            flash('Warning: Changing this schedule may affect existing appointments.', 'warning')
        
        # Update schedule
        schedule.day_of_week = form.day_of_week.data
        schedule.start_time = form.start_time.data
        schedule.end_time = form.end_time.data
        if hasattr(form, 'is_available'):
            schedule.is_active = form.is_available.data
        
        db.session.commit()
        flash('Schedule updated successfully.', 'success')
        return redirect(url_for('schedule.manage'))
    
    return render_template('schedule/edit.html', form=form, schedule=schedule)


@schedule_bp.route('/delete/<int:schedule_id>', methods=['GET', 'POST'])
@login_required
@doctor_required
def delete(schedule_id):
    """Delete a schedule"""
    doctor = Doctor.query.filter_by(user_id=current_user.id).first()
    if not doctor:
        flash('Doctor profile not found.', 'danger')
        return redirect(url_for('doctor.profile'))
    
    schedule = Schedule.query.get_or_404(schedule_id)
    
    # Ensure doctor can only delete their own schedule
    if schedule.doctor_id != doctor.id:
        abort(403)  # Forbidden
    
    form = ScheduleDeleteForm()
    
    if form.validate_on_submit():
        # Check for appointments affected by this schedule deletion
        # Just warn for now about potential conflicts
        affected_appointments = Appointment.query.filter_by(
            doctor_id=doctor.id,
            status='booked'
        ).all()
        
        if affected_appointments:
            flash('Warning: Deleting this schedule may affect existing appointments.', 'warning')
        
        db.session.delete(schedule)
        db.session.commit()
        flash('Schedule deleted successfully.', 'success')
        return redirect(url_for('schedule.manage'))
    
    return render_template('schedule/delete.html', form=form, schedule=schedule)


@schedule_bp.route('/doctor/<int:doctor_id>')
@login_required
def doctor_schedule(doctor_id):
    """View a doctor's schedule (public view)"""
    doctor = Doctor.query.get_or_404(doctor_id)
    
    # Make sure the doctor's user account is active
    if not doctor.user.is_active:
        flash('This doctor is not currently available.', 'warning')
        return redirect(url_for('main.index'))
    
    schedules = Schedule.query.filter_by(doctor_id=doctor.id, is_available=True).order_by(Schedule.day_of_week, Schedule.start_time).all()
    
    return render_template('schedule/doctor_schedule.html', doctor=doctor, schedules=schedules)

@schedule_bp.route('/weekly')
@login_required
def weekly():
    """Weekly schedule view"""
    return render_template('schedule/weekly_view.html')

@schedule_bp.route('/list')
@login_required
@admin_required
def list():
    """Display a list of schedules - Admin only"""
    doctors = Doctor.query.join(Doctor.user).filter_by(is_active=True).all()
    schedules = Schedule.query.all()
    return render_template('schedule/list.html', doctors=doctors, schedules=schedules)