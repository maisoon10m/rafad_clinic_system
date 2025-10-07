"""
Reporting and Analytics routes for Rafad Clinic System
"""
from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from app.decorators import admin_required
from app.models import db, User, Patient, Doctor, Appointment, Schedule
from sqlalchemy import func
from datetime import datetime, timedelta

# Create blueprint
reporting_bp = Blueprint('reporting', __name__)


@reporting_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Main reporting dashboard"""
    return render_template('reporting/dashboard.html')


@reporting_bp.route('/appointment-stats')
@login_required
@admin_required
def appointment_stats():
    """Appointment statistics view"""
    return render_template('reporting/appointment_stats.html')


@reporting_bp.route('/doctor-utilization')
@login_required
@admin_required
def doctor_utilization():
    """Doctor utilization metrics view"""
    doctors = Doctor.query.all()
    return render_template('reporting/doctor_utilization.html', doctors=doctors)


@reporting_bp.route('/patient-analytics')
@login_required
@admin_required
def patient_analytics():
    """Patient analytics view"""
    return render_template('reporting/patient_analytics.html')


@reporting_bp.route('/api/appointments/daily')
@login_required
@admin_required
def api_appointments_daily():
    """Get appointment count by day for the past 30 days"""
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    # Query to get count of appointments by date
    results = db.session.query(
        func.date(Appointment.appointment_time).label('date'),
        func.count(Appointment.id).label('count')
    ).filter(
        func.date(Appointment.appointment_time) >= start_date,
        func.date(Appointment.appointment_time) <= end_date
    ).group_by(
        func.date(Appointment.appointment_time)
    ).all()
    
    # Format the results
    data = {
        'labels': [],
        'datasets': [{
            'label': 'Daily Appointments',
            'data': [],
            'backgroundColor': 'rgba(122, 174, 159, 0.6)',
            'borderColor': 'rgba(122, 174, 159, 1)',
        }]
    }
    
    # Convert query results to chart data
    for date, count in results:
        data['labels'].append(date.strftime('%Y-%m-%d'))
        data['datasets'][0]['data'].append(count)
    
    return jsonify(data)


@reporting_bp.route('/api/appointments/status')
@login_required
@admin_required
def api_appointments_status():
    """Get appointment count by status"""
    results = db.session.query(
        Appointment.status,
        func.count(Appointment.id).label('count')
    ).group_by(Appointment.status).all()
    
    # Format the results
    data = {
        'labels': [],
        'datasets': [{
            'data': [],
            'backgroundColor': [
                'rgba(122, 174, 159, 0.6)',  # completed - green
                'rgba(248, 155, 147, 0.6)',  # cancelled - coral
                'rgba(74, 137, 220, 0.6)',   # pending - blue
                'rgba(255, 206, 84, 0.6)',   # confirmed - yellow
            ],
        }]
    }
    
    # Convert query results to chart data
    status_colors = {
        'completed': 'rgba(122, 174, 159, 0.6)',
        'cancelled': 'rgba(248, 155, 147, 0.6)',
        'pending': 'rgba(74, 137, 220, 0.6)',
        'confirmed': 'rgba(255, 206, 84, 0.6)',
    }
    
    for status, count in results:
        data['labels'].append(status)
        data['datasets'][0]['data'].append(count)
    
    return jsonify(data)


@reporting_bp.route('/api/doctor/utilization')
@login_required
@admin_required
def api_doctor_utilization():
    """Get doctor utilization metrics"""
    doctor_id = request.args.get('doctor_id', type=int)
    period = request.args.get('period', 'week')
    
    if period == 'week':
        days = 7
    elif period == 'month':
        days = 30
    else:
        days = 90
    
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    
    # Base query for appointments
    query = db.session.query(
        Doctor.id,
        Doctor.specialization,
        func.count(Appointment.id).label('appointment_count')
    ).join(
        Appointment, Appointment.doctor_id == Doctor.id
    ).filter(
        func.date(Appointment.appointment_time) >= start_date,
        func.date(Appointment.appointment_time) <= end_date
    ).group_by(Doctor.id)
    
    # Apply doctor filter if specified
    if doctor_id:
        query = query.filter(Doctor.id == doctor_id)
    
    results = query.all()
    
    # Get doctor names from User model
    doctor_info = {}
    for doctor in Doctor.query.all():
        user = User.query.get(doctor.user_id)
        doctor_info[doctor.id] = {
            'name': f"{user.first_name} {user.last_name}" if (hasattr(user, 'first_name') and user.first_name) else user.username,
            'specialization': doctor.specialization
        }
    
    # Format the results
    data = {
        'labels': [],
        'datasets': [{
            'label': 'Appointments',
            'data': [],
            'backgroundColor': 'rgba(122, 174, 159, 0.6)',
            'borderColor': 'rgba(122, 174, 159, 1)',
        }]
    }
    
    # Convert query results to chart data
    for doctor_id, specialization, count in results:
        name = doctor_info.get(doctor_id, {}).get('name', f'Doctor {doctor_id}')
        data['labels'].append(name)
        data['datasets'][0]['data'].append(count)
    
    return jsonify(data)