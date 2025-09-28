"""
Migration manager script for Rafad Clinic System
"""
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from app import create_app, db

app = create_app('development')
migrate = Migrate(app, db)

if __name__ == '__main__':
    from flask.cli import FlaskGroup
    cli = FlaskGroup(create_app=lambda: app)
    
    @cli.command('db_create')
    def db_create():
        """Create the database"""
        db.create_all()
        print('Database created!')
    
    @cli.command('db_drop')
    def db_drop():
        """Drop the database"""
        db.drop_all()
        print('Database dropped!')
    
    @cli.command('db_seed')
    def db_seed():
        """Seed the database with initial data"""
        from app.models import User, Setting
        
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
        print('Database seeded!')
    
    cli()