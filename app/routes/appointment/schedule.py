"""
Schedule routes for the Rafad Clinic System
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, abort
from flask_login import login_required, current_user
from app import db
from app.models.schedule import Schedule
from app.models.doctor import Doctor
from app.forms.appointment import ScheduleForm, ScheduleSearchForm
from datetime import datetime, time
from sqlalchemy import or_, and_
from app.utils.decorators import role_required

# Create a blueprint for schedule routes
schedule_bp = Blueprint('schedule', __name__, url_prefix='/schedule')


@schedule_bp.route('/')
@schedule_bp.route('/list')
@login_required
@role_required(['admin', 'doctor', 'receptionist'])
def list():
    """Display a list of doctor schedules"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Build the query based on the user's role
    if current_user.role == 'admin' or current_user.role == 'receptionist':
        # Admin and receptionist can see all schedules
        query = Schedule.query
    elif current_user.role == 'doctor':
        # Doctors can see only their own schedules
        query = Schedule.query.filter(Schedule.doctor_id == current_user.doctor.id)
    else:
        abort(403)  # Forbidden
    
    # Apply filters
    doctor_id = request.args.get('doctor_id', type=int)
    day = request.args.get('day', type=int)
    status = request.args.get('status')
    
    if doctor_id:
        query = query.filter(Schedule.doctor_id == doctor_id)
    
    if day is not None:  # Using 'is not None' because 0 is a valid value for day
        query = query.filter(Schedule.day_of_week == day)
    
    if status:
        is_active = status == 'active'
        query = query.filter(Schedule.is_active == is_active)
    
    # Order by doctor name, day of week, and start time
    query = query.join(Doctor).order_by(
        Doctor.last_name, 
        Doctor.first_name, 
        Schedule.day_of_week, 
        Schedule.start_time
    )
    
    # Paginate the results
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    schedules = pagination.items
    total = pagination.total
    
    # Get doctors for filter dropdown
    doctors = Doctor.query.join(Doctor.user).filter_by(is_active=True).all()
    
    return render_template(
        'schedule/list.html',
        schedules=schedules,
        pagination=pagination,
        total=total,
        doctors=doctors
    )


@schedule_bp.route('/create', methods=['GET', 'POST'])
@login_required
@role_required(['admin', 'receptionist'])
def create():
    """Create a new doctor schedule"""
    form = ScheduleForm()
    
    if form.validate_on_submit():
        # Check for overlapping schedules for the same doctor on the same day
        existing_schedule = Schedule.query.filter(
            Schedule.doctor_id == form.doctor_id.data.id,
            Schedule.day_of_week == form.day_of_week.data,
            Schedule.is_active == True,
            or_(
                # Check for overlapping time ranges
                and_(
                    Schedule.start_time <= form.start_time.data,
                    Schedule.end_time > form.start_time.data
                ),
                and_(
                    Schedule.start_time < form.end_time.data,
                    Schedule.end_time >= form.end_time.data
                ),
                and_(
                    Schedule.start_time >= form.start_time.data,
                    Schedule.end_time <= form.end_time.data
                )
            )
        ).first()
        
        if existing_schedule:
            flash('This schedule overlaps with an existing schedule for this doctor on the same day.', 'error')
            return render_template('schedule/create.html', form=form)
        
        # Create a new schedule
        schedule = Schedule(
            doctor_id=form.doctor_id.data.id,
            day_of_week=form.day_of_week.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            appointment_duration=form.appointment_duration.data,
            break_duration=form.break_duration.data,
            is_active=form.is_active.data,
            notes=form.notes.data
        )
        
        db.session.add(schedule)
        db.session.commit()
        
        flash('Schedule created successfully!', 'success')
        return redirect(url_for('schedule.list'))
    
    # If doctor_id is provided in query params, pre-select it
    doctor_id = request.args.get('doctor_id', type=int)
    if doctor_id:
        for doctor in form.doctor_id.iter_choices():
            if doctor[0].id == doctor_id:
                form.doctor_id.data = doctor[0]
                break
    
    return render_template('schedule/create.html', form=form)


@schedule_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required(['admin', 'receptionist'])
def edit(id):
    """Edit an existing doctor schedule"""
    schedule = Schedule.query.get_or_404(id)
    form = ScheduleForm(obj=schedule)
    
    if form.validate_on_submit():
        # Check for overlapping schedules for the same doctor on the same day
        existing_schedule = Schedule.query.filter(
            Schedule.doctor_id == form.doctor_id.data.id,
            Schedule.day_of_week == form.day_of_week.data,
            Schedule.is_active == True,
            Schedule.id != schedule.id,
            or_(
                # Check for overlapping time ranges
                and_(
                    Schedule.start_time <= form.start_time.data,
                    Schedule.end_time > form.start_time.data
                ),
                and_(
                    Schedule.start_time < form.end_time.data,
                    Schedule.end_time >= form.end_time.data
                ),
                and_(
                    Schedule.start_time >= form.start_time.data,
                    Schedule.end_time <= form.end_time.data
                )
            )
        ).first()
        
        if existing_schedule:
            flash('This schedule overlaps with an existing schedule for this doctor on the same day.', 'error')
            return render_template('schedule/edit.html', form=form, schedule=schedule)
        
        # Update schedule fields
        schedule.doctor_id = form.doctor_id.data.id
        schedule.day_of_week = form.day_of_week.data
        schedule.start_time = form.start_time.data
        schedule.end_time = form.end_time.data
        schedule.appointment_duration = form.appointment_duration.data
        schedule.break_duration = form.break_duration.data
        schedule.is_active = form.is_active.data
        schedule.notes = form.notes.data
        
        db.session.commit()
        
        flash('Schedule updated successfully!', 'success')
        return redirect(url_for('schedule.list'))
    
    # Pre-select the current doctor
    for doctor in form.doctor_id.iter_choices():
        if doctor[0].id == schedule.doctor_id:
            form.doctor_id.data = doctor[0]
            break
    
    return render_template('schedule/edit.html', form=form, schedule=schedule)


@schedule_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
@role_required(['admin', 'receptionist'])
def delete(id):
    """Delete a doctor schedule"""
    schedule = Schedule.query.get_or_404(id)
    
    db.session.delete(schedule)
    db.session.commit()
    
    flash('Schedule deleted successfully!', 'success')
    return redirect(url_for('schedule.list'))


@schedule_bp.route('/weekly-view')
@login_required
def weekly_view():
    """Display a weekly view of all doctor schedules"""
    # Get filters
    department_id = request.args.get('department', type=int)
    doctor_id = request.args.get('doctor', type=int)
    
    # Query for schedules based on filters
    schedules_query = Schedule.query.filter_by(is_active=True)
    
    if doctor_id:
        schedules_query = schedules_query.filter_by(doctor_id=doctor_id)
    
    schedules = schedules_query.all()
    
    # Get all doctors for the filter dropdowns
    doctors = Doctor.query.join(Doctor.user).filter_by(is_active=True).all()
    
    # Organize schedules by doctor and day
    doctor_schedules = {}
    for schedule in schedules:
        doctor_id = schedule.doctor_id
        doctor = schedule.doctor
        
        if doctor_id not in doctor_schedules:
            doctor_schedules[doctor_id] = {
                'name': doctor.full_name,
                'department': doctor.specialization if doctor.specialization else "No Specialization",
                'days': {}
            }
        
        day_name = schedule.day_name_lower  # monday, tuesday, etc.
        
        if day_name not in doctor_schedules[doctor_id]['days']:
            doctor_schedules[doctor_id]['days'][day_name] = []
        
        doctor_schedules[doctor_id]['days'][day_name].append({
            'start_time': schedule.start_time.strftime('%H:%M'),
            'end_time': schedule.end_time.strftime('%H:%M'),
            'appointment_duration': schedule.appointment_duration,
            'is_active': schedule.is_active,
            'notes': schedule.notes
        })
    
    return render_template(
        'schedule/weekly_view.html',
        doctor_schedules=doctor_schedules,
        doctors=doctors
    )