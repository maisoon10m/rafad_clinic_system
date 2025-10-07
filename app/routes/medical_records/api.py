"""
API routes for medical records
"""
from datetime import datetime, timedelta
from flask import jsonify, request
from flask_login import login_required, current_user
from sqlalchemy import desc, or_, and_

from app.models.medical_record import MedicalRecord
from app.models.patient import Patient
from app.utils.decorators import patient_or_doctor_required
from . import medical_records


@medical_records.route('/api/patient/<int:patient_id>/records', methods=['GET'])
@login_required
@patient_or_doctor_required
def api_get_records(patient_id):
    """API to get filtered medical records for a patient"""
    # Verify permissions
    if current_user.is_patient() and current_user.patient.id != patient_id:
        return jsonify({'error': 'Unauthorized access'}), 403
    
    patient = Patient.query.get_or_404(patient_id)
    
    # Get filter parameters
    record_types = request.args.getlist('record_type')
    date_range = request.args.get('date_range', 'all')
    doctor_id = request.args.get('doctor_id', 'all')
    search_query = request.args.get('query', '')
    
    # Build the query
    query = MedicalRecord.query.filter_by(
        patient_id=patient_id,
        is_active=True
    )
    
    # Apply record type filter
    if record_types and 'all' not in record_types:
        query = query.filter(MedicalRecord.record_type.in_(record_types))
    
    # Apply date range filter
    if date_range != 'all':
        days = int(date_range)
        date_from = datetime.now() - timedelta(days=days)
        query = query.filter(MedicalRecord.record_date >= date_from)
    
    # Apply doctor filter
    if doctor_id != 'all':
        query = query.filter(MedicalRecord.doctor_id == int(doctor_id))
    
    # Apply search query
    if search_query:
        search_terms = f"%{search_query}%"
        query = query.filter(
            or_(
                MedicalRecord.title.ilike(search_terms),
                MedicalRecord.description.ilike(search_terms)
            )
        )
    
    # Get the records, ordered by record date (newest first)
    records = query.order_by(desc(MedicalRecord.record_date)).all()
    
    # Format the records
    result = []
    for record in records:
        doctor_name = f"Dr. {record.doctor.user.first_name} {record.doctor.user.last_name}"
        
        # Base record data
        record_data = {
            'id': record.id,
            'type': record.record_type,
            'title': record.title,
            'description': record.description,
            'record_date': record.record_date.strftime('%Y-%m-%d'),
            'doctor_name': doctor_name,
            'doctor_id': record.doctor_id,
            'is_confidential': record.is_confidential
        }
        
        # Add specific data based on record type
        if record.record_type == 'diagnosis' and record.diagnoses.first():
            diagnosis = record.diagnoses.first()
            record_data.update({
                'diagnosis_code': diagnosis.diagnosis_code,
                'diagnosis_name': diagnosis.diagnosis_name,
                'severity': diagnosis.severity,
                'notes': diagnosis.notes
            })
        elif record.record_type == 'prescription' and record.prescriptions.first():
            prescription = record.prescriptions.first()
            record_data.update({
                'medication_name': prescription.medication_name,
                'dosage': prescription.dosage,
                'frequency': prescription.frequency,
                'duration': prescription.duration,
                'instructions': prescription.instructions
            })
        elif record.record_type == 'treatment' and record.treatments.first():
            treatment = record.treatments.first()
            record_data.update({
                'treatment_name': treatment.treatment_name,
                'treatment_type': treatment.treatment_type,
                'outcome': treatment.outcome,
                'start_date': treatment.start_date.strftime('%Y-%m-%d %H:%M') if treatment.start_date else None,
                'end_date': treatment.end_date.strftime('%Y-%m-%d %H:%M') if treatment.end_date else None
            })
        elif record.record_type == 'test' and record.test_results.first():
            test = record.test_results.first()
            record_data.update({
                'test_name': test.test_name,
                'test_category': test.test_category,
                'result_value': test.result_value,
                'result_unit': test.result_unit,
                'is_abnormal': test.is_abnormal,
                'file_path': test.file_path
            })
            
        result.append(record_data)
    
    return jsonify({
        'records': result,
        'total': len(result)
    })
    

@medical_records.route('/api/patient/<int:patient_id>/search', methods=['GET'])
@login_required
@patient_or_doctor_required
def api_search_records(patient_id):
    """API to search medical records for a patient"""
    # Verify permissions
    if current_user.is_patient() and current_user.patient.id != patient_id:
        return jsonify({'error': 'Unauthorized access'}), 403
        
    search_query = request.args.get('q', '')
    
    if not search_query or len(search_query) < 3:
        return jsonify({
            'records': [],
            'total': 0
        })
    
    # Search in medical records
    search_terms = f"%{search_query}%"
    records = MedicalRecord.query.filter(
        and_(
            MedicalRecord.patient_id == patient_id,
            MedicalRecord.is_active == True,
            or_(
                MedicalRecord.title.ilike(search_terms),
                MedicalRecord.description.ilike(search_terms)
            )
        )
    ).order_by(desc(MedicalRecord.record_date)).all()
    
    # Format the records (simplified for search results)
    result = []
    for record in records:
        record_data = {
            'id': record.id,
            'type': record.record_type,
            'title': record.title,
            'record_date': record.record_date.strftime('%Y-%m-%d'),
            'doctor_name': f"Dr. {record.doctor.user.first_name} {record.doctor.user.last_name}"
        }
        result.append(record_data)
    
    return jsonify({
        'records': result,
        'total': len(result)
    })