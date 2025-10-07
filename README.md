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

## Project Structure (current)

```
rafad_clinic_system/
├── app/                   # Main Flask application package
│   ├── decorators/        # Role-based access control decorators
│   ├── forms/             # Flask-WTF forms (appointment/, doctor/, patient/, schedule/)
│   ├── models/            # SQLAlchemy model definitions
│   ├── routes/            # Blueprints organized by domain (admin/, api/, appointment/, auth/, doctor/, patient/, reporting/, schedule/)
│   ├── static/            # CSS / JS / images / uploads
│   ├── templates/         # Jinja2 templates
│   ├── utils/             # Helper utilities and validators
│   └── __init__.py        # Application factory + extension init
├── docs/                  # Project documentation (moved reports)
├── migrations/            # Alembic/Flask-Migrate scripts
│   └── versions/
├── scripts/               # Utility scripts for DB/schema tasks
├── tests/                 # Tests organized into subpackages (forms/, models/, routes/, utils/)
├── config.py              # Configuration classes (development/testing/production)
├── requirements.txt       # Python dependencies
├── run.py                 # Application entry point (Flask app runner + CLI commands)
├── manage.py              # Management CLI (db create/drop/seed, legacy script)
├── rafad_dev.sqlite       # Development SQLite database (local)
├── rafad_test.sqlite      # Testing SQLite database (used by pytest)
└── README.md              # This file
```

Notes:
- Two SQLite files are present intentionally: `rafad_dev.sqlite` (development) and `rafad_test.sqlite` (testing). This keeps tests isolated from development data.
- If you prefer not to track the database files in git, add them to `.gitignore` and remove them from the repository history.
- Tests were reorganized under `tests/` into logical subpackages to mirror the app structure.


## Project Organization Principles

The project follows these key organization principles:

1. **Modular Structure**: Code is organized into logical modules by functionality.
2. **Blueprint-Based Routing**: Flask blueprints are used to organize routes by domain.
3. **Database Abstraction**: SQLAlchemy ORM provides a clean abstraction over the database.
4. **Separation of Concerns**: Models, views (routes), and forms are kept separate.
5. **Test Organization**: Tests mirror the main project structure for clarity.
6. **Utility Scripts**: Database management scripts are organized in the scripts folder.
7. **Documentation**: Project documentation is centralized in the docs folder.

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