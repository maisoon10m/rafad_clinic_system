"""
Entry point for Rafad Clinic System
"""
import os
from flask_migrate import Migrate
from app import create_app, db

# Create Flask application instance
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

# Setup Flask-Migrate
migrate = Migrate(app, db)

# Import models to be included in migrations
from app.models.user import User
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.schedule import Schedule
from app.models.appointment import Appointment
from app.models.setting import Setting

@app.cli.command('init_db')
def init_db():
    """Initialize the database with tables"""
    db.create_all()
    print('Database initialized with tables!')

@app.cli.command('seed_db')
def seed_db():
    """Seed the database with initial data"""
    # Create admin user
    admin = User(
        username='admin',
        email='admin@rafadclinic.com',
        role='admin'
    )
    admin.password = 'Admin@123'
    db.session.add(admin)
    
    # Create default settings
    settings = [
        Setting(
            setting_name='clinic_name',
            setting_value='Rafad Clinic',
            setting_type='string',
            description='Name of the clinic',
            is_public=True
        ),
        Setting(
            setting_name='appointment_duration',
            setting_value='30',
            setting_type='integer',
            description='Default appointment duration in minutes',
            is_public=True
        ),
        Setting(
            setting_name='clinic_open_time',
            setting_value='09:00',
            setting_type='string',
            description='Clinic opening time',
            is_public=True
        ),
        Setting(
            setting_name='clinic_close_time',
            setting_value='18:00',
            setting_type='string',
            description='Clinic closing time',
            is_public=True
        ),
        Setting(
            setting_name='maintenance_mode',
            setting_value='false',
            setting_type='boolean',
            description='Whether the system is in maintenance mode',
            is_public=False
        ),
    ]
    
    for setting in settings:
        db.session.add(setting)
    
    db.session.commit()
    print('Database seeded with initial data!')

if __name__ == '__main__':
    app.run(debug=True)