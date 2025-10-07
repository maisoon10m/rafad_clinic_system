"""
Routes for managing medical records
"""
import os
from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask import current_app, abort, send_from_directory
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from sqlalchemy import desc

from app.models.medical_record import (
    MedicalRecord, Diagnosis, Prescription, 
    Treatment, TestResult, MedicalNote,
    DiagnosisRecord, PrescriptionRecord, 
    TreatmentRecord, TestResultRecord
)
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.appointment import Appointment
from app.forms.medical_records.forms import (
    DiagnosisForm, PrescriptionForm, 
    TreatmentForm, TestResultForm, MedicalNoteForm
)
from app.utils.decorators import doctor_required, patient_or_doctor_required
from .. import db
from . import medical_records


def allowed_file(filename, allowed_extensions=None):
    """Check if the uploaded file has an allowed extension"""
    if allowed_extensions is None:
        allowed_extensions = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def save_file(file, directory):
    """Save an uploaded file to the specified directory"""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        
        # Create directory if it doesn't exist
        if not os.path.exists(directory):
            os.makedirs(directory)
            
        file_path = os.path.join(directory, unique_filename)
        file.save(file_path)
        return unique_filename
    return None


@medical_records.route('/patient/<int:patient_id>/view')
@login_required
@patient_or_doctor_required
def view(patient_id):
    """View a patient's medical records"""
    patient = Patient.query.get_or_404(patient_id)
    
    # Verify permissions:
    # 1. Patient can only view their own records
    # 2. Doctors can view records of their patients
    if current_user.is_patient() and current_user.patient.id != patient_id:
        abort(403)  # Forbidden
    
    # Get all medical records for the patient, ordered by record date (newest first)
    records = MedicalRecord.query.filter_by(
        patient_id=patient_id, is_active=True
    ).order_by(desc(MedicalRecord.record_date)).all()
    
    # Get doctors for filtering
    doctors = Doctor.query.all()
    
    return render_template(
        'medical_records/view.html',
        patient=patient,
        records=records,
        doctors=doctors,
        now=datetime.now()
    )


@medical_records.route('/patient/<int:patient_id>/add', methods=['GET', 'POST'])
@login_required
@doctor_required
def add(patient_id):
    """Add a medical record for a patient"""
    patient = Patient.query.get_or_404(patient_id)
    
    # Get appointment_id from query param if it exists
    appointment_id = request.args.get('appointment_id', None)
    appointment = None
    if appointment_id:
        appointment = Appointment.query.get_or_404(appointment_id)
        if appointment.patient_id != patient_id or appointment.doctor_id != current_user.doctor.id:
            abort(403)  # Forbidden
    
    return render_template(
        'medical_records/add.html',
        patient=patient,
        appointment=appointment,
        now=datetime.now()
    )


@medical_records.route('/patient/<int:patient_id>/add/diagnosis', methods=['POST'])
@login_required
@doctor_required
def add_diagnosis(patient_id):
    """Add a diagnosis record for a patient"""
    form = DiagnosisForm()
    
    if form.validate_on_submit():
        # Create the diagnosis record
        diagnosis_record = DiagnosisRecord(
            patient_id=patient_id,
            doctor_id=current_user.doctor.id,
            appointment_id=form.appointment_id.data or None,
            record_date=form.record_date.data,
            title=form.title.data,
            description=form.description.data,
            is_confidential=form.is_confidential.data
        )
        
        # Add to database to get the record ID
        db.session.add(diagnosis_record)
        db.session.flush()  # Flush to get the ID without committing
        
        # Create the diagnosis details
        diagnosis = Diagnosis(
            medical_record_id=diagnosis_record.id,
            diagnosis_code=form.diagnosis_code.data,
            diagnosis_name=form.diagnosis_name.data,
            description=form.description.data,
            severity=form.severity.data,
            notes=form.notes.data,
            is_primary=form.is_primary.data
        )
        
        db.session.add(diagnosis)
        db.session.commit()
        
        flash('Diagnosis added successfully.', 'success')
        return redirect(url_for('medical_records.view', patient_id=patient_id))
    
    # If form validation fails
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"Error in {getattr(form, field).label.text}: {error}", 'danger')
    
    return redirect(url_for('medical_records.add', patient_id=patient_id))


@medical_records.route('/patient/<int:patient_id>/add/prescription', methods=['POST'])
@login_required
@doctor_required
def add_prescription(patient_id):
    """Add a prescription record for a patient"""
    form = PrescriptionForm()
    
    if form.validate_on_submit():
        # Create the prescription record
        prescription_record = PrescriptionRecord(
            patient_id=patient_id,
            doctor_id=current_user.doctor.id,
            appointment_id=form.appointment_id.data or None,
            record_date=form.record_date.data,
            title=form.title.data,
            description=form.description.data,
            is_confidential=form.is_confidential.data
        )
        
        # Add to database to get the record ID
        db.session.add(prescription_record)
        db.session.flush()  # Flush to get the ID without committing
        
        # Create the prescription details
        prescription = Prescription(
            medical_record_id=prescription_record.id,
            medication_name=form.medication_name.data,
            dosage=form.dosage.data,
            frequency=form.frequency.data,
            duration=form.duration.data,
            instructions=form.instructions.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            refill_count=form.refill_count.data
        )
        
        db.session.add(prescription)
        db.session.commit()
        
        flash('Prescription added successfully.', 'success')
        return redirect(url_for('medical_records.view', patient_id=patient_id))
    
    # If form validation fails
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"Error in {getattr(form, field).label.text}: {error}", 'danger')
    
    return redirect(url_for('medical_records.add', patient_id=patient_id))


@medical_records.route('/patient/<int:patient_id>/add/treatment', methods=['POST'])
@login_required
@doctor_required
def add_treatment(patient_id):
    """Add a treatment record for a patient"""
    form = TreatmentForm()
    
    if form.validate_on_submit():
        # Create the treatment record
        treatment_record = TreatmentRecord(
            patient_id=patient_id,
            doctor_id=current_user.doctor.id,
            appointment_id=form.appointment_id.data or None,
            record_date=form.record_date.data,
            title=form.title.data,
            description=form.description.data,
            is_confidential=form.is_confidential.data
        )
        
        # Add to database to get the record ID
        db.session.add(treatment_record)
        db.session.flush()  # Flush to get the ID without committing
        
        # Create the treatment details
        treatment = Treatment(
            medical_record_id=treatment_record.id,
            treatment_name=form.treatment_name.data,
            treatment_type=form.treatment_type.data,
            description=form.description.data,
            notes=form.notes.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            outcome=form.outcome.data
        )
        
        db.session.add(treatment)
        db.session.commit()
        
        flash('Treatment added successfully.', 'success')
        return redirect(url_for('medical_records.view', patient_id=patient_id))
    
    # If form validation fails
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"Error in {getattr(form, field).label.text}: {error}", 'danger')
    
    return redirect(url_for('medical_records.add', patient_id=patient_id))


@medical_records.route('/patient/<int:patient_id>/add/test-result', methods=['POST'])
@login_required
@doctor_required
def add_test_result(patient_id):
    """Add a test result record for a patient"""
    form = TestResultForm()
    
    if form.validate_on_submit():
        # Create the test result record
        test_record = TestResultRecord(
            patient_id=patient_id,
            doctor_id=current_user.doctor.id,
            appointment_id=form.appointment_id.data or None,
            record_date=form.record_date.data,
            title=form.title.data,
            description=form.description.data,
            is_confidential=form.is_confidential.data
        )
        
        # Add to database to get the record ID
        db.session.add(test_record)
        db.session.flush()  # Flush to get the ID without committing
        
        # Handle file upload
        file_path = None
        if form.test_file.data:
            upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'test_results')
            filename = save_file(form.test_file.data, upload_dir)
            if filename:
                file_path = f'test_results/{filename}'
        
        # Create the test result details
        test_result = TestResult(
            medical_record_id=test_record.id,
            test_name=form.test_name.data,
            test_category=form.test_category.data,
            test_date=form.test_date.data,
            result_value=form.result_value.data,
            result_unit=form.result_unit.data,
            reference_range=form.reference_range.data,
            is_abnormal=form.is_abnormal.data,
            notes=form.notes.data,
            file_path=file_path
        )
        
        db.session.add(test_result)
        db.session.commit()
        
        flash('Test result added successfully.', 'success')
        return redirect(url_for('medical_records.view', patient_id=patient_id))
    
    # If form validation fails
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"Error in {getattr(form, field).label.text}: {error}", 'danger')
    
    return redirect(url_for('medical_records.add', patient_id=patient_id))


@medical_records.route('/patient/<int:patient_id>/add/note', methods=['POST'])
@login_required
@doctor_required
def add_note(patient_id):
    """Add a medical note for a patient"""
    form = MedicalNoteForm()
    
    if form.validate_on_submit():
        # Create the medical note
        note = MedicalNote(
            patient_id=patient_id,
            doctor_id=current_user.doctor.id,
            appointment_id=form.appointment_id.data or None,
            record_date=form.record_date.data,
            title=form.title.data,
            description=form.description.data,
            is_confidential=form.is_confidential.data
        )
        
        db.session.add(note)
        db.session.commit()
        
        flash('Medical note added successfully.', 'success')
        return redirect(url_for('medical_records.view', patient_id=patient_id))
    
    # If form validation fails
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"Error in {getattr(form, field).label.text}: {error}", 'danger')
    
    return redirect(url_for('medical_records.add', patient_id=patient_id))


@medical_records.route('/record/<int:record_id>/delete', methods=['POST'])
@login_required
@doctor_required
def delete_record(record_id):
    """Delete (soft delete) a medical record"""
    record = MedicalRecord.query.get_or_404(record_id)
    
    # Verify the doctor owns this record
    if record.doctor_id != current_user.doctor.id:
        abort(403)  # Forbidden
    
    # Soft delete by setting is_active to False
    record.is_active = False
    db.session.commit()
    
    flash('Medical record deleted successfully.', 'success')
    return redirect(url_for('medical_records.view', patient_id=record.patient_id))


@medical_records.route('/test-result/<path:filename>')
@login_required
def get_test_file(filename):
    """Serve test result files"""
    return send_from_directory(
        os.path.join(current_app.config['UPLOAD_FOLDER']), 
        filename
    )


@medical_records.route('/record/<int:record_id>')
@login_required
@patient_or_doctor_required
def view_record(record_id):
    """View a specific medical record"""
    record = MedicalRecord.query.get_or_404(record_id)
    
    # Verify permissions:
    # 1. Patient can only view their own records
    # 2. Doctors can view records of their patients
    if current_user.is_patient() and current_user.patient.id != record.patient_id:
        abort(403)  # Forbidden
    
    return render_template(
        'medical_records/record.html',
        record=record
    )


@medical_records.route('/patient/<int:patient_id>/export', methods=['POST'])
@login_required
@patient_or_doctor_required
def export_records(patient_id):
    """Export a patient's medical records"""
    # This would be implemented to generate PDF or CSV based on form data
    # For now, just redirect back with a message
    flash('Record export functionality coming soon.', 'info')
    return redirect(url_for('medical_records.view', patient_id=patient_id))