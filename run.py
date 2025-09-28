"""
Entry point for Rafad Clinic System
"""
import os
from app import create_app

# Create Flask application instance
app = create_app(os.getenv('FLASK_CONFIG') or 'default')


if __name__ == '__main__':
    app.run(debug=True)