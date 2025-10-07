from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, DateField, DateTimeField
from wtforms import BooleanField, IntegerField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Optional, Length

class MedicalRecordBaseForm(FlaskForm):
    """Base form for all medical records"""
    title = StringField('Title', validators=[DataRequired(), Length(max=128)])
    description = TextAreaField('Description', validators=[Optional()])
    record_date = DateField('Record Date', validators=[DataRequired()])
    is_confidential = BooleanField('Mark as confidential')
    appointment_id = HiddenField('Appointment ID')
    
class DiagnosisForm(MedicalRecordBaseForm):
    """Form for creating a diagnosis record"""
    diagnosis_code = StringField('Diagnosis Code (ICD-10)', validators=[Optional(), Length(max=20)])
    diagnosis_name = StringField('Diagnosis Name', validators=[DataRequired(), Length(max=128)])
    severity = SelectField('Severity', choices=[
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe')
    ], default='mild')
    notes = TextAreaField('Additional Notes', validators=[Optional()])
    is_primary = BooleanField('This is the primary diagnosis', default=True)
    submit = SubmitField('Save Diagnosis')
    
class PrescriptionForm(MedicalRecordBaseForm):
    """Form for creating a prescription record"""
    medication_name = StringField('Medication Name', validators=[DataRequired(), Length(max=128)])
    dosage = StringField('Dosage', validators=[DataRequired(), Length(max=64)])
    frequency = StringField('Frequency', validators=[DataRequired(), Length(max=64)])
    duration = StringField('Duration', validators=[Optional(), Length(max=64)])
    instructions = TextAreaField('Special Instructions', validators=[Optional()])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[Optional()])
    refill_count = IntegerField('Refill Count', validators=[Optional()], default=0)
    submit = SubmitField('Save Prescription')
    
class TreatmentForm(MedicalRecordBaseForm):
    """Form for creating a treatment record"""
    treatment_name = StringField('Treatment Name', validators=[DataRequired(), Length(max=128)])
    treatment_type = SelectField('Treatment Type', choices=[
        ('surgical', 'Surgical'),
        ('therapy', 'Therapy'),
        ('procedure', 'Procedure'),
        ('medication', 'Medication'),
        ('other', 'Other')
    ], default='procedure')
    start_date = DateTimeField('Start Date', validators=[DataRequired()], format='%Y-%m-%dT%H:%M')
    end_date = DateTimeField('End Date', validators=[Optional()], format='%Y-%m-%dT%H:%M')
    outcome = SelectField('Outcome', choices=[
        ('pending', 'Pending'),
        ('successful', 'Successful'),
        ('ongoing', 'Ongoing'),
        ('inconclusive', 'Inconclusive'),
        ('failed', 'Failed')
    ], default='pending')
    notes = TextAreaField('Additional Notes', validators=[Optional()])
    submit = SubmitField('Save Treatment')
    
class TestResultForm(MedicalRecordBaseForm):
    """Form for creating a test result record"""
    test_name = StringField('Test Name', validators=[DataRequired(), Length(max=128)])
    test_category = SelectField('Category', choices=[
        ('blood', 'Blood Test'),
        ('imaging', 'Imaging'),
        ('pathology', 'Pathology'),
        ('urine', 'Urine Test'),
        ('other', 'Other')
    ], default='blood')
    test_date = DateField('Test Date', validators=[DataRequired()])
    result_value = StringField('Result Value', validators=[Optional(), Length(max=256)])
    result_unit = StringField('Unit', validators=[Optional(), Length(max=32)])
    reference_range = StringField('Reference Range', validators=[Optional(), Length(max=64)])
    is_abnormal = BooleanField('Result is abnormal')
    notes = TextAreaField('Notes', validators=[Optional()])
    test_file = FileField('Upload Test Result File', validators=[
        Optional(),
        FileAllowed(['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'], 'Only PDF, images, and documents are allowed!')
    ])
    submit = SubmitField('Save Test Result')
    
class MedicalNoteForm(MedicalRecordBaseForm):
    """Form for creating a medical note"""
    submit = SubmitField('Save Note')