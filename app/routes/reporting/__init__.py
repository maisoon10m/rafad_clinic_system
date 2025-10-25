"""
Reporting and Analytics routes for Rafad Clinic System
"""
from flask import Blueprint, render_template, jsonify, request, Response
from flask_login import login_required, current_user
from app.decorators import admin_required
from app.models import db, User, Patient, Doctor, Appointment, Schedule
from sqlalchemy import func
from datetime import datetime, timedelta
import csv
from io import StringIO

# Create blueprint
reporting_bp = Blueprint('reporting', __name__)


@reporting_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    """Main reporting dashboard"""
    # Calculate real statistics for a 30-day window (past and future)
    today = datetime.now().date()
    start_date = today - timedelta(days=30)
    end_date = today + timedelta(days=30)
    
    # Total appointments in the 30-day window (past 30 days + next 30 days)
    total_appointments = Appointment.query.filter(
        Appointment.appointment_date >= start_date,
        Appointment.appointment_date <= end_date
    ).count()
    
    # New patients - count all patients
    new_patients = Patient.query.count()
    
    # Doctor utilization (average appointments per doctor in the window)
    doctor_count = Doctor.query.count()
    avg_utilization = round(total_appointments / doctor_count, 1) if doctor_count > 0 else 0
    
    # Growth rate (compare current 30-day window to previous 30-day window)
    previous_start = start_date - timedelta(days=30)
    previous_end = start_date
    previous_appointments = Appointment.query.filter(
        Appointment.appointment_date >= previous_start,
        Appointment.appointment_date < previous_end
    ).count()
    
    if previous_appointments > 0:
        growth_rate = round(((total_appointments - previous_appointments) / previous_appointments) * 100, 1)
    else:
        growth_rate = 0 if total_appointments == 0 else 100
    
    return render_template('reporting/dashboard.html',
                         total_appointments=total_appointments,
                         new_patients=new_patients,
                         avg_utilization=avg_utilization,
                         growth_rate=growth_rate)


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
    """Get appointment count by day for a 60-day window (30 days past + 30 days future)"""
    today = datetime.now().date()
    start_date = today - timedelta(days=30)
    end_date = today + timedelta(days=30)
    
    # Query to get count of appointments by date
    results = db.session.query(
        Appointment.appointment_date,
        func.count(Appointment.id).label('count')
    ).filter(
        Appointment.appointment_date >= start_date,
        Appointment.appointment_date <= end_date
    ).group_by(
        Appointment.appointment_date
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
        Appointment.appointment_date >= start_date,
        Appointment.appointment_date <= end_date
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


@reporting_bp.route('/export/csv')
@login_required
@admin_required
def export_csv():
    """Export appointments data to CSV"""
    # Get all appointments with related data
    appointments = Appointment.query.all()
    
    # Create CSV in memory
    output = StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        'Appointment ID',
        'Date',
        'Start Time',
        'End Time',
        'Patient Name',
        'Patient Email',
        'Doctor Name',
        'Doctor Specialization',
        'Status',
        'Reason',
        'Notes',
        'Created At'
    ])
    
    # Write data rows
    for apt in appointments:
        # Get patient info
        patient = Patient.query.get(apt.patient_id)
        patient_user = User.query.get(patient.user_id) if patient else None
        patient_name = f"{patient.first_name} {patient.last_name}" if patient else "N/A"
        patient_email = patient_user.email if patient_user else "N/A"
        
        # Get doctor info
        doctor = Doctor.query.get(apt.doctor_id)
        doctor_user = User.query.get(doctor.user_id) if doctor else None
        doctor_name = f"{doctor_user.username}" if doctor_user else "N/A"
        doctor_spec = doctor.specialization if doctor else "N/A"
        
        writer.writerow([
            apt.id,
            apt.appointment_date.strftime('%Y-%m-%d') if apt.appointment_date else 'N/A',
            apt.start_time.strftime('%H:%M') if apt.start_time else 'N/A',
            apt.end_time.strftime('%H:%M') if apt.end_time else 'N/A',
            patient_name,
            patient_email,
            doctor_name,
            doctor_spec,
            apt.status,
            apt.reason or '',
            apt.notes or '',
            apt.created_at.strftime('%Y-%m-%d %H:%M:%S') if apt.created_at else 'N/A'
        ])
    
    # Prepare the response
    output.seek(0)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'rafad_clinic_appointments_{timestamp}.csv'
    
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )


@reporting_bp.route('/api/appointments/by-specialization')
@login_required
@admin_required
def api_appointments_by_specialization():
    """Get appointment count grouped by doctor specialization"""
    # Query appointments grouped by doctor specialization
    results = db.session.query(
        Doctor.specialization,
        func.count(Appointment.id).label('count')
    ).join(
        Appointment, Appointment.doctor_id == Doctor.id
    ).group_by(Doctor.specialization).all()
    
    # Format the results
    data = {
        'labels': [],
        'datasets': [{
            'label': 'Appointments',
            'data': [],
            'backgroundColor': [
                'rgba(122, 174, 159, 0.6)',  # green
                'rgba(248, 155, 147, 0.6)',  # coral
                'rgba(74, 137, 220, 0.6)',   # blue
                'rgba(255, 206, 84, 0.6)',   # yellow
                'rgba(172, 146, 236, 0.6)',  # purple
                'rgba(237, 85, 101, 0.6)',   # red
            ],
        }]
    }
    
    # Convert query results to chart data
    for specialization, count in results:
        data['labels'].append(specialization or 'General')
        data['datasets'][0]['data'].append(count)
    
    return jsonify(data)