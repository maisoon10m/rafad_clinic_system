# Rafad (رفد) Clinic Appointment Management System

A comprehensive web-based appointment management system for medical clinics.

## Project Overview

Rafad Clinic System is designed to streamline the operations of medical clinics and enhance the patient experience through an efficient appointment management platform. The system provides distinct interfaces for patients, doctors, and administrators, facilitating a smooth workflow for appointment scheduling and clinic management.

## Features

- **User Authentication**: Secure login system with role-based access (patient, doctor, admin)
- **Patient Portal**: Book appointments, view appointment history, manage personal information
- **Doctor Portal**: Manage schedule, view appointments, access patient information
- **Admin Dashboard**: User management, doctor management, system oversight
- **Appointment Management**: Book, cancel, and view appointments with status tracking

## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript with Bootstrap
- **Authentication**: Flask-Login
- **ORM**: SQLAlchemy with Flask-SQLAlchemy
- **Forms**: Flask-WTF and WTForms

## Project Structure

```
rafad_clinic_system/
├── app/
│   ├── static/           # CSS, JavaScript, and images
│   ├── templates/        # HTML templates
│   ├── models/           # Database models
│   ├── routes/           # Flask route definitions
│   ├── utils/            # Helper functions and utilities
│   └── __init__.py       # Flask application factory
├── migrations/           # Database migrations
├── tests/                # Unit and integration tests
├── config.py             # Configuration settings
├── requirements.txt      # Python dependencies
└── run.py               # Application entry point
```

## Setup and Installation

### Prerequisites
- Python 3.8+
- Git

### Installation Steps

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/rafad-clinic-system.git
   cd rafad-clinic-system
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the application:
   ```
   python run.py
   ```

5. Access the application at http://localhost:5000

## Development

### Running Tests
```
pytest
```

### Database Migrations
```
flask db init    # Initialize migrations (first time only)
flask db migrate # Generate migration script
flask db upgrade # Apply migration
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgements

Developed as part of a project for Rafad Clinic.