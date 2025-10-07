"""
Medical Records models for Rafad Clinic System
"""
from datetime import datetime
from . import db


class MedicalRecord(db.Model):
    """Base Medical Record model for storing patient medical records"""
    __tablename__ = 'medical_records'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'), nullable=True)
    record_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    record_type = db.Column(db.String(50), nullable=False)  # 'diagnosis', 'treatment', 'prescription', 'test', 'note'
    title = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_confidential = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    diagnoses = db.relationship('Diagnosis', backref='medical_record', lazy='dynamic',
                               cascade='all, delete-orphan')
    prescriptions = db.relationship('Prescription', backref='medical_record', lazy='dynamic',
                                   cascade='all, delete-orphan')
    treatments = db.relationship('Treatment', backref='medical_record', lazy='dynamic',
                                cascade='all, delete-orphan')
    test_results = db.relationship('TestResult', backref='medical_record', lazy='dynamic',
                                  cascade='all, delete-orphan')
    
    # Use single-table inheritance for medical record subtypes
    __mapper_args__ = {
        'polymorphic_on': record_type,
        'polymorphic_identity': 'record'
    }
    
    def __repr__(self):
        return f'<MedicalRecord {self.id} - {self.record_type}>'


class Diagnosis(db.Model):
    """Diagnosis model for storing patient diagnoses"""
    __tablename__ = 'diagnoses'

    id = db.Column(db.Integer, primary_key=True)
    medical_record_id = db.Column(db.Integer, db.ForeignKey('medical_records.id'), nullable=False)
    diagnosis_code = db.Column(db.String(20))  # ICD-10 or similar code
    diagnosis_name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    severity = db.Column(db.String(20))  # 'mild', 'moderate', 'severe'
    diagnosis_date = db.Column(db.DateTime, default=datetime.utcnow)
    notes = db.Column(db.Text)
    is_primary = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<Diagnosis {self.diagnosis_name}>'


class Prescription(db.Model):
    """Prescription model for storing medications prescribed to patients"""
    __tablename__ = 'prescriptions'

    id = db.Column(db.Integer, primary_key=True)
    medical_record_id = db.Column(db.Integer, db.ForeignKey('medical_records.id'), nullable=False)
    medication_name = db.Column(db.String(128), nullable=False)
    dosage = db.Column(db.String(64), nullable=False)
    frequency = db.Column(db.String(64), nullable=False)  # e.g., "3 times a day"
    duration = db.Column(db.String(64))  # e.g., "7 days"
    instructions = db.Column(db.Text)
    start_date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    end_date = db.Column(db.Date)
    refill_count = db.Column(db.Integer, default=0)
    
    def __repr__(self):
        return f'<Prescription {self.medication_name}>'


class Treatment(db.Model):
    """Treatment model for storing treatments provided to patients"""
    __tablename__ = 'treatments'

    id = db.Column(db.Integer, primary_key=True)
    medical_record_id = db.Column(db.Integer, db.ForeignKey('medical_records.id'), nullable=False)
    treatment_name = db.Column(db.String(128), nullable=False)
    treatment_type = db.Column(db.String(64))  # e.g., "surgical", "therapy", "procedure"
    description = db.Column(db.Text)
    notes = db.Column(db.Text)
    start_date = db.Column(db.DateTime, default=datetime.utcnow)
    end_date = db.Column(db.DateTime)
    outcome = db.Column(db.String(64))  # e.g., "successful", "ongoing", "inconclusive"
    
    def __repr__(self):
        return f'<Treatment {self.treatment_name}>'


class TestResult(db.Model):
    """Test Result model for storing patient test results"""
    __tablename__ = 'test_results'

    id = db.Column(db.Integer, primary_key=True)
    medical_record_id = db.Column(db.Integer, db.ForeignKey('medical_records.id'), nullable=False)
    test_name = db.Column(db.String(128), nullable=False)
    test_category = db.Column(db.String(64))  # e.g., "blood", "imaging", "pathology"
    test_date = db.Column(db.DateTime, default=datetime.utcnow)
    result_value = db.Column(db.String(256))
    result_unit = db.Column(db.String(32))
    reference_range = db.Column(db.String(64))
    is_abnormal = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text)
    file_path = db.Column(db.String(256))  # For storing file paths to test result documents
    
    def __repr__(self):
        return f'<TestResult {self.test_name}>'


class MedicalNote(MedicalRecord):
    """Medical Note model for general medical notes"""
    __mapper_args__ = {
        'polymorphic_identity': 'note',
    }
    
    def __repr__(self):
        return f'<MedicalNote {self.id}>'


class DiagnosisRecord(MedicalRecord):
    """Diagnosis Record for main diagnosis entries"""
    __mapper_args__ = {
        'polymorphic_identity': 'diagnosis',
    }
    
    def __repr__(self):
        return f'<DiagnosisRecord {self.id}>'


class PrescriptionRecord(MedicalRecord):
    """Prescription Record for prescriptions"""
    __mapper_args__ = {
        'polymorphic_identity': 'prescription',
    }
    
    def __repr__(self):
        return f'<PrescriptionRecord {self.id}>'


class TreatmentRecord(MedicalRecord):
    """Treatment Record for treatments"""
    __mapper_args__ = {
        'polymorphic_identity': 'treatment',
    }
    
    def __repr__(self):
        return f'<TreatmentRecord {self.id}>'


class TestResultRecord(MedicalRecord):
    """Test Result Record for test results"""
    __mapper_args__ = {
        'polymorphic_identity': 'test',
    }
    
    def __repr__(self):
        return f'<TestResultRecord {self.id}>'