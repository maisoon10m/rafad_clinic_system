"""
API endpoints for the appointment system in Rafad Clinic System
"""
from flask import Blueprint, jsonify, request, abort, current_app
from flask_login import login_required, current_user
from app import db
from app.models.appointment import Appointment
from app.models.doctor import Doctor
from app.models.patient import Patient
from app.models.schedule import Schedule
from datetime import datetime, date, timedelta
from sqlalchemy.exc import SQLAlchemyError
from app.utils.decorators import role_required
from app.utils.error_handler import ErrorHandler

# Create a blueprint for API routes
api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/appointments')
@login_required
def get_appointments():
    """API endpoint to get appointments for the calendar view"""
    try:
        # Required parameters
        start_date = request.args.get('start')
        end_date = request.args.get('end')
        doctor_id = request.args.get('doctor_id', type=int)
        
        # Validate parameters
        if not start_date or not end_date:
            return jsonify({
                'status': 'error',
                'message': 'Missing required parameters',
                'details': 'Both start and end dates are required'
            }), 400
        
        try:
            start_date = datetime.fromisoformat(start_date.split('T')[0]).date()
            end_date = datetime.fromisoformat(end_date.split('T')[0]).date()
        except ValueError as e:
            error_response, status_code = ErrorHandler.api_error_response(
                e, 
                status_code=400, 
                user_message='Invalid date format. Use ISO format (YYYY-MM-DD).',
                context={'start_date': start_date, 'end_date': end_date}
            )
            return jsonify(error_response), status_code
            
        # Validate date range
        date_difference = (end_date - start_date).days
        if date_difference < 0:
            return jsonify({
                'status': 'error',
                'message': 'Invalid date range',
                'details': 'End date must be after start date'
            }), 400
            
        if date_difference > 90:  # Limit to 3 months of data
            return jsonify({
                'status': 'error',
                'message': 'Date range too large',
                'details': 'Maximum range is 90 days'
            }), 400
    
    except Exception as e:
        error_response, status_code = ErrorHandler.api_error_response(
            e, 
            user_message='An error occurred while processing date parameters'
        )
        return jsonify(error_response), status_code
    
    # Build query based on user role
    if current_user.role == 'patient':
        # Patients can see only their own appointments
        query = Appointment.query.filter(
            Appointment.patient_id == current_user.patient.id,
            Appointment.appointment_date >= start_date,
            Appointment.appointment_date <= end_date
        )
    elif current_user.role == 'doctor':
        # Doctors can see only their own appointments
        query = Appointment.query.filter(
            Appointment.doctor_id == current_user.doctor.id,
            Appointment.appointment_date >= start_date,
            Appointment.appointment_date <= end_date
        )
    elif current_user.role in ['admin', 'receptionist']:
        # Admin and receptionists can see all appointments
        query = Appointment.query.filter(
            Appointment.appointment_date >= start_date,
            Appointment.appointment_date <= end_date
        )
        
        # Filter by doctor if specified
        if doctor_id:
            query = query.filter(Appointment.doctor_id == doctor_id)
    else:
        return jsonify({'error': 'Unauthorized'}), 403
    
    appointments = query.all()
    
    # Format appointments for the calendar
    formatted_appointments = []
    for appointment in appointments:
        patient = appointment.patient
        doctor = appointment.doctor
        
        formatted_appointments.append({
            'id': appointment.id,
            'patient_id': patient.id,
            'patient_name': patient.full_name,
            'doctor_id': doctor.id,
            'doctor_name': doctor.full_name,
            'appointment_date': appointment.appointment_date.isoformat(),
            'appointment_time': appointment.appointment_time.strftime('%H:%M'),
            'status': appointment.status,
            'reason': appointment.reason
        })
    
    return jsonify({'appointments': formatted_appointments})


@api_bp.route('/appointment/<int:id>')
@login_required
def get_appointment(id):
    """API endpoint to get details of a specific appointment"""
    appointment = Appointment.query.get_or_404(id)
    
    # Check permissions
    if current_user.role == 'patient' and current_user.patient.id != appointment.patient_id:
        return jsonify({'error': 'Unauthorized'}), 403
    elif current_user.role == 'doctor' and current_user.doctor.id != appointment.doctor_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Format appointment for response
    patient = appointment.patient
    doctor = appointment.doctor
    
    formatted_appointment = {
        'id': appointment.id,
        'patient_id': patient.id,
        'patient_name': patient.full_name,
        'doctor_id': doctor.id,
        'doctor_name': doctor.full_name,
        'appointment_date': appointment.appointment_date.isoformat(),
        'formatted_date': appointment.formatted_date,
        'appointment_time': appointment.appointment_time.strftime('%H:%M'),
        'formatted_time': appointment.formatted_time,
        'status': appointment.status,
        'reason': appointment.reason,
        'notes': appointment.notes,
        'created_at': appointment.created_at.isoformat() if appointment.created_at else None,
        'updated_at': appointment.updated_at.isoformat() if appointment.updated_at else None
    }
    
    return jsonify({'appointment': formatted_appointment})


@api_bp.route('/available-slots')
@login_required
def get_available_slots():
    """API endpoint to get available time slots for a doctor on a specific date"""
    doctor_id = request.args.get('doctor_id', type=int)
    date_str = request.args.get('date')
    exclude_appointment_id = request.args.get('exclude_appointment_id', type=int)
    
    if not doctor_id or not date_str:
        return jsonify({'error': 'Missing required parameters'}), 400
    
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400
    
    # Get available slots from the Schedule model
    slots = Schedule.get_available_slots(doctor_id, date_obj, exclude_appointment_id)
    
    return jsonify({'slots': slots})


@api_bp.route('/doctors-by-department/<int:department_id>')
@login_required
def get_doctors_by_department(department_id):
    """API endpoint to get doctors filtered by department"""
    doctors = Doctor.query.filter_by(
        department_id=department_id,
        is_active=True
    ).all()
    
    formatted_doctors = [
        {
            'id': doctor.id,
            'full_name': doctor.full_name,
            'specialization': doctor.specialization
        }
        for doctor in doctors
    ]
    
    return jsonify({'doctors': formatted_doctors})