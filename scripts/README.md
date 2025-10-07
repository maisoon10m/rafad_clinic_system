# Utility Scripts

This directory contains utility scripts for database management and schema operations.

## Scripts Overview

- `add_last_login.py`: Adds the last_login column to the users table
- `check_medical_tables.py`: Checks if medical tables exist in the database
- `check_schema.py`: Displays the schema of specified tables
- `drop_medical_tables.py`: Removes medical tables that are no longer needed

## Usage

These scripts should be run from the project root directory:

```bash
python scripts/script_name.py
```

For example, to check the database schema:

```bash
python scripts/check_schema.py
```