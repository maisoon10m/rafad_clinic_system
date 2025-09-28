"""
Migration script for Rafad Clinic System
"""
from flask_migrate import Migrate
from app import create_app, db

app = create_app('development')
migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run()