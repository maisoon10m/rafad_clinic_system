"""
API endpoint for validating appointments
"""
from flask import Blueprint, jsonify, request
from flask_login import login_required
from app.utils.appointment_validator import validate_appointment_request
from datetime import datetime

validate_bp = Blueprint('validate_appointment', __name__, url_prefix='/api')

@validate_bp.route('/validate-appointment')
@login_required
def validate_appointment():
    """Validate if an appointment request is valid (no conflicts)"""
    doctor_id = request.args.get('doctor_id', type=int)
    date_str = request.args.get('date')
    time_str = request.args.get('time')
    appointment_id = request.args.get('appointment_id', type=int)
    
    # Validate required parameters
    if not doctor_id or not date_str or not time_str:
        return jsonify({
            'valid': False,
            'message': 'Missing required parameters'
        }), 400
    
    try:
        # Parse date and time
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        time_obj = datetime.strptime(time_str, '%H:%M').time()
        
        # Validate appointment
        is_valid, message = validate_appointment_request(
            doctor_id, 
            date_obj, 
            time_obj, 
            exclude_appointment_id=appointment_id
        )
        
        return jsonify({
            'valid': is_valid,
            'message': message if not is_valid else 'Appointment is valid'
        })
        
    except ValueError as e:
        return jsonify({
            'valid': False,
            'message': f'Invalid date or time format: {str(e)}'
        }), 400
    except Exception as e:
        return jsonify({
            'valid': False,
            'message': f'Error validating appointment: {str(e)}'
        }), 500