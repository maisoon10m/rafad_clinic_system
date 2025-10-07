"""
Script to drop medical record tables from the database
"""
import sqlite3
import os

def drop_medical_tables():
    """Drop all medical record related tables"""
    # Connect to the SQLite database
    db_path = os.path.join(os.getcwd(), 'rafad_dev.sqlite')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Tables to drop in order to avoid foreign key constraint issues
    tables = ['test_results', 'treatments', 'prescriptions', 'diagnoses', 'medical_records']
    
    print("Dropping medical record related tables...")
    
    # Disable foreign key constraints temporarily
    cursor.execute("PRAGMA foreign_keys = OFF")
    
    # Drop tables
    for table in tables:
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
            print(f"Dropped table: {table}")
        except Exception as e:
            print(f"Error dropping table {table}: {e}")
    
    # Re-enable foreign key constraints
    cursor.execute("PRAGMA foreign_keys = ON")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print("Completed dropping medical record tables")

if __name__ == "__main__":
    drop_medical_tables()