"""
Appointment routes for the Rafad Clinic System
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify, abort, current_app
from flask_login import login_required, current_user
from app import db
from app.models.appointment import Appointment
from app.models.schedule import Schedule
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.forms.appointment import AppointmentForm, AppointmentStatusForm, AppointmentSearchForm
from datetime import datetime, timedelta
from sqlalchemy import or_, and_
from sqlalchemy.exc import SQLAlchemyError
from app.utils.decorators import role_required
from app.utils.error_handler import ErrorHandler

# Create a blueprint for appointment routes
appointment_bp = Blueprint('appointment', __name__, url_prefix='/appointment')


@appointment_bp.route('/')
@appointment_bp.route('/list')
@login_required
def list():
    """Display a list of appointments with pagination and filtering"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search_term = request.args.get('search', '')
    
    # Build the query based on the user's role
    if current_user.role == 'admin' or current_user.role == 'receptionist':
        # Admin and receptionist can see all appointments
        query = Appointment.query
    elif current_user.role == 'doctor':
        # Doctors can see only their own appointments
        query = Appointment.query.filter(Appointment.doctor_id == current_user.doctor.id)
    elif current_user.role == 'patient':
        # Patients can see only their own appointments
        query = Appointment.query.filter(Appointment.patient_id == current_user.patient.id)
    else:
        abort(403)  # Forbidden
    
    # Apply search term if provided
    if search_term:
        # Search in patient and doctor names
        query = query.join(Patient).join(Doctor).filter(
            or_(
                Patient.first_name.ilike(f'%{search_term}%'),
                Patient.last_name.ilike(f'%{search_term}%'),
                Doctor.first_name.ilike(f'%{search_term}%'),
                Doctor.last_name.ilike(f'%{search_term}%'),
                Appointment.reason.ilike(f'%{search_term}%')
            )
        )
    
    # Apply filters
    doctor_id = request.args.get('doctor_id', type=int)
    status = request.args.get('status')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    if doctor_id:
        query = query.filter(Appointment.doctor_id == doctor_id)
    
    if status:
        query = query.filter(Appointment.status == status)
    
    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d').date()
            query = query.filter(Appointment.appointment_date >= date_from)
        except ValueError:
            flash('Invalid date format for date_from', 'error')
    
    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d').date()
            query = query.filter(Appointment.appointment_date <= date_to)
        except ValueError:
            flash('Invalid date format for date_to', 'error')
    
    # Order by most recent first
    query = query.order_by(Appointment.appointment_date.desc(), Appointment.start_time)
    
    # Paginate the results
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    appointments = pagination.items
    total = pagination.total
    
    # Get doctors for filter dropdown
    doctors = Doctor.query.join(Doctor.user).filter_by(is_active=True).all()
    
    return render_template(
        'appointment/list.html',
        appointments=appointments,
        pagination=pagination,
        total=total,
        doctors=doctors,
        search_term=search_term
    )


@appointment_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    """Create a new appointment"""
    # Doctors should not be able to create appointments
    if current_user.role == 'doctor':
        flash('Doctors cannot create appointments. Patients book appointments with you.', 'warning')
        return redirect(url_for('appointment.list'))
    
    form = AppointmentForm()
    
    # Check if the current user is a patient
    is_patient = current_user.role == 'patient'
    current_patient = None
    
    if is_patient:
        # Get the patient record for the current user
        current_patient = Patient.query.filter_by(user_id=current_user.id).first()
        if not current_patient:
            flash('Patient profile not found. Please contact support.', 'error')
            return redirect(url_for('main.index'))
        
        # For patients, add themselves to the choices and select it
        form.patient_id.choices = [(current_patient.id, current_patient.full_name)]
        form.patient_id.data = current_patient.id
    
    try:
        # Check if doctor_id and date are provided in query params
        # This happens when redirecting from the available slots page
        doctor_id = request.args.get('doctor_id', type=int)
        date = request.args.get('date')
        time = request.args.get('time')
        
        if request.method == 'GET' and doctor_id and date:
            try:
                # Pre-fill the form with the provided doctor ID
                form.doctor_id.data = doctor_id
                
                form.appointment_date.data = datetime.strptime(date, '%Y-%m-%d').date()
                
                if time:
                    form.appointment_time.data = datetime.strptime(time, '%H:%M').time()
            except ValueError as e:
                # Handle date/time parsing errors
                ErrorHandler.handle_error(
                    e, 
                    user_message="Invalid date or time format provided", 
                    context={"doctor_id": doctor_id, "date": date, "time": time}
                )
            except Exception as e:
                # Handle any other errors
                ErrorHandler.handle_error(
                    e, 
                    user_message="An error occurred while loading the form", 
                    context={"doctor_id": doctor_id, "date": date, "time": time}
                )
        
        # For patients, ensure their ID is in choices before validation
        if is_patient and request.method == 'POST':
            form.patient_id.choices = [(current_patient.id, current_patient.full_name)]
            form.patient_id.data = current_patient.id
        
        if form.validate_on_submit():
            try:
                # Calculate end_time (30 minutes after appointment_time if not provided)
                start_time = form.appointment_time.data
                end_time = form.end_time.data if form.end_time.data else (
                    datetime.combine(datetime.today(), start_time) + timedelta(minutes=30)
                ).time()
                
                # Determine patient_id based on user role
                if is_patient:
                    patient_id = current_patient.id
                else:
                    patient_id = form.patient_id.data
                
                # Create a new appointment
                appointment = Appointment(
                    patient_id=patient_id,
                    doctor_id=form.doctor_id.data,
                    appointment_date=form.appointment_date.data,
                    start_time=start_time,
                    end_time=end_time,
                    reason=form.reason.data,
                    status=form.status.data,
                    notes=form.notes.data
                )
                
                # Check if the appointment time is available
                is_available, reason = Appointment.check_availability(
                    doctor_id=appointment.doctor_id,
                    date=appointment.appointment_date,
                    time=appointment.start_time,
                    duration_minutes=30  # Default appointment duration
                )
                
                if not is_available:
                    flash(f'Cannot book this appointment: {reason}', 'error')
                    return render_template('appointment/create.html', form=form, is_patient=is_patient, current_patient=current_patient)
                
                db.session.add(appointment)
                db.session.commit()
                
                current_app.logger.info(f"Appointment created successfully: ID={appointment.id}, Patient={appointment.patient_id}, Doctor={appointment.doctor_id}")
                flash('Appointment created successfully!', 'success')
                return redirect(url_for('appointment.view', id=appointment.id))
            
            except SQLAlchemyError as e:
                db.session.rollback()
                ErrorHandler.handle_error(
                    e, 
                    user_message="An error occurred while saving the appointment. Please try again.", 
                    context={"form_data": request.form}
                )
            except Exception as e:
                db.session.rollback()
                ErrorHandler.handle_error(
                    e, 
                    user_message="An unexpected error occurred. Please try again later.",
                    context={"form_data": request.form}
                )
    
    except Exception as e:
        ErrorHandler.handle_error(
            e, 
            user_message="An error occurred while processing your request. Please try again."
        )
    
    return render_template(
        'appointment/create.html', 
        form=form, 
        is_patient=is_patient,
        current_patient=current_patient
    )


@appointment_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@role_required(['admin', 'receptionist'])
def edit(id):
    """Edit an existing appointment - Only admin and receptionist can edit"""
    appointment = Appointment.query.get_or_404(id)
    
    form = AppointmentForm()
    
    if request.method == 'GET':
        # Pre-populate form with appointment data
        form.patient_id.data = appointment.patient_id
        form.doctor_id.data = appointment.doctor_id
        form.appointment_date.data = appointment.appointment_date
        form.appointment_time.data = appointment.start_time
        form.end_time.data = appointment.end_time
        form.reason.data = appointment.reason
        form.status.data = appointment.status
        form.notes.data = appointment.notes
    
    if form.validate_on_submit():
        # Check if the appointment time is available if date, time, or doctor changed
        if (form.appointment_date.data != appointment.appointment_date or 
            form.appointment_time.data != appointment.start_time or
            form.doctor_id.data != appointment.doctor_id):
            
            is_available, reason = Appointment.check_availability(
                doctor_id=form.doctor_id.data,
                date=form.appointment_date.data,
                time=form.appointment_time.data,
                exclude_appointment_id=appointment.id,
                duration_minutes=30  # Default appointment duration
            )
            
            if not is_available:
                flash(f'Cannot update this appointment: {reason}', 'error')
                return render_template('appointment/edit.html', form=form, appointment=appointment)
        
        # Calculate end_time (30 minutes after appointment_time if not provided)
        start_time = form.appointment_time.data
        end_time = form.end_time.data if form.end_time.data else (
            datetime.combine(datetime.today(), start_time) + timedelta(minutes=30)
        ).time()
        
        # Update appointment fields
        appointment.patient_id = form.patient_id.data
        appointment.doctor_id = form.doctor_id.data
        appointment.appointment_date = form.appointment_date.data
        appointment.start_time = start_time
        appointment.end_time = end_time
        appointment.reason = form.reason.data
        appointment.status = form.status.data
        appointment.notes = form.notes.data
        
        db.session.commit()
        
        flash('Appointment updated successfully!', 'success')
        return redirect(url_for('appointment.view', id=appointment.id))
    
    # Pre-select the current doctor and patient
    for doctor in form.doctor_id.iter_choices():
        if doctor[0].id == appointment.doctor_id:
            form.doctor_id.data = doctor[0]
            break
            
    for patient in form.patient_id.iter_choices():
        if patient[0].id == appointment.patient_id:
            form.patient_id.data = patient[0]
            break
    
    return render_template('appointment/edit.html', form=form, appointment=appointment)


@appointment_bp.route('/view/<int:id>')
@login_required
def view(id):
    """View appointment details"""
    appointment = Appointment.query.get_or_404(id)
    
    # Check permissions
    if current_user.role == 'patient' and current_user.patient.id != appointment.patient_id:
        abort(403)  # Forbidden
    elif current_user.role == 'doctor' and current_user.doctor.id != appointment.doctor_id:
        abort(403)  # Forbidden
    
    # Get previous appointments for the same patient
    previous_appointments = Appointment.query.filter_by(
        patient_id=appointment.patient_id
    ).order_by(
        Appointment.appointment_date.desc(), 
        Appointment.start_time.desc()
    ).limit(10).all()
    
    return render_template(
        'appointment/view.html',
        appointment=appointment,
        previous_appointments=previous_appointments
    )


@appointment_bp.route('/delete/<int:id>', methods=['POST'])
@login_required
@role_required(['admin', 'receptionist'])
def delete(id):
    """Delete an appointment"""
    appointment = Appointment.query.get_or_404(id)
    
    db.session.delete(appointment)
    db.session.commit()
    
    flash('Appointment deleted successfully!', 'success')
    return redirect(url_for('appointment.list'))


@appointment_bp.route('/update-status/<int:id>', methods=['POST'])
@login_required
def update_status(id):
    """Update the status of an appointment"""
    appointment = Appointment.query.get_or_404(id)
    
    status = request.form.get('status')
    
    # Check permissions based on role and status
    if current_user.role == 'patient':
        # Patients can only cancel their own appointments
        if current_user.patient.id != appointment.patient_id:
            abort(403)  # Not their appointment
        if status != 'cancelled':
            flash('Patients can only cancel appointments.', 'error')
            return redirect(url_for('appointment.view', id=appointment.id))
    elif current_user.role == 'doctor':
        # Doctors can only update status of their own appointments
        if current_user.doctor.id != appointment.doctor_id:
            abort(403)
    elif current_user.role not in ['admin', 'receptionist']:
        abort(403)  # Other roles not allowed
    
    if status in ['scheduled', 'completed', 'cancelled', 'no_show']:
        appointment.status = status
        db.session.commit()
        flash(f'Appointment status updated to {status}!', 'success')
    else:
        flash('Invalid status!', 'error')
    
    return redirect(url_for('appointment.view', id=appointment.id))


@appointment_bp.route('/calendar')
@login_required
def calendar():
    """Display appointments in a calendar view"""
    doctors = Doctor.query.join(Doctor.user).filter_by(is_active=True).all()
    
    return render_template('appointment/calendar.html', doctors=doctors)


@appointment_bp.route('/available-slots', methods=['GET'])
@login_required
def available_slots():
    """Display available appointment slots for a selected doctor and date"""
    # Doctors should not be able to book appointments
    if current_user.role == 'doctor':
        flash('Doctors cannot book appointments. Patients book appointments with you.', 'warning')
        return redirect(url_for('appointment.list'))
    
    doctor_id = request.args.get('doctor_id', type=int)
    date = request.args.get('date')
    
    slots = []
    doctor_name = ""
    doctor_department = ""
    doctor_schedule = None
    formatted_date = ""
    
    if doctor_id and date:
        try:
            # Convert date string to datetime object
            date_obj = datetime.strptime(date, '%Y-%m-%d').date()
            formatted_date = date_obj.strftime('%d/%m/%Y')
            
            # Get doctor information
            doctor = Doctor.query.get_or_404(doctor_id)
            doctor_name = doctor.full_name
            doctor_department = doctor.specialization if doctor.specialization else "No Specialization"
            
            # Get day of week (0=Monday, 6=Sunday)
            day_of_week = date_obj.weekday()
            
            # Find the doctor's schedule for this day
            doctor_schedule = Schedule.query.filter_by(
                doctor_id=doctor_id,
                day_of_week=day_of_week,
                is_active=True
            ).first()
            
            if doctor_schedule:
                # Get available slots
                slots = Schedule.get_available_slots(doctor_id, date_obj)
            
        except ValueError as e:
            flash('Invalid date format', 'error')
            current_app.logger.error(f"Date parsing error: {e}")
        except Exception as e:
            flash('An error occurred while fetching available slots', 'error')
            current_app.logger.error(f"Error in available_slots: {e}")
    
    today = datetime.now().strftime('%Y-%m-%d')
    doctors = Doctor.query.join(Doctor.user).filter_by(is_active=True).all()
    
    return render_template(
        'appointment/available_slots.html',
        slots=slots,
        doctor_name=doctor_name,
        doctor_department=doctor_department,
        doctor_schedule=doctor_schedule,
        formatted_date=formatted_date,
        today=today,
        doctors=doctors
    )