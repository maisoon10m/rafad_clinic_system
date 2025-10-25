"""
API endpoints for retrieving doctor schedules
"""
from flask import Blueprint, jsonify, request
from flask_login import login_required
from app.models.schedule import Schedule
from app.models.doctor import Doctor

# Create a blueprint for schedule API routes
schedule_api_bp = Blueprint('schedule_api', __name__, url_prefix='/api')

@schedule_api_bp.route('/doctor-schedule/<int:doctor_id>')
@login_required
def get_doctor_schedule(doctor_id):
    """API endpoint to get a doctor's schedule for the weekly view"""
    doctor = Doctor.query.get_or_404(doctor_id)
    
    schedules = Schedule.query.filter_by(
        doctor_id=doctor_id,
        is_active=True
    ).all()
    
    # Format schedules for response
    formatted_schedules = []
    for schedule in schedules:
        formatted_schedules.append({
            'id': schedule.id,
            'day_of_week': schedule.day_of_week,
            'day_name': schedule.day_name,
            'start_time': schedule.start_time.strftime('%H:%M'),
            'end_time': schedule.end_time.strftime('%H:%M'),
            'appointment_duration': schedule.appointment_duration,
            'break_duration': schedule.break_duration,
            'notes': schedule.notes
        })
    
    return jsonify({
        'doctor': {
            'id': doctor.id,
            'name': doctor.full_name,
            'specialization': doctor.specialization
        },
        'schedules': formatted_schedules
    })