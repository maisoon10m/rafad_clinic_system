"""
Check database schema to verify medical records tables have been removed
"""
import sqlite3
import os

def check_database_tables():
    """Check if there are any medical record related tables in the database"""
    # Connect to the SQLite database
    db_path = os.path.join(os.getcwd(), 'rafad_dev.sqlite')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Query to find all tables in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print("All tables in database:")
    for table in tables:
        print(f" - {table[0]}")
    
    # Check for tables with 'medical' in the name
    print("\nChecking for medical record related tables...")
    medical_tables = []
    for table in tables:
        if 'medical' in table[0].lower():
            medical_tables.append(table[0])
    
    if medical_tables:
        print("WARNING: Found medical record related tables:")
        for table in medical_tables:
            print(f" - {table}")
    else:
        print("SUCCESS: No medical record tables found in database")
    
    # Check for references to medical records in other tables
    print("\nChecking for columns referencing medical records in other tables...")
    for table in tables:
        cursor.execute(f"PRAGMA table_info({table[0]})")
        columns = cursor.fetchall()
        medical_columns = []
        
        for col in columns:
            col_name = col[1]
            if 'medical_record' in col_name.lower():
                medical_columns.append(col_name)
        
        if medical_columns:
            print(f"WARNING: Found medical record related columns in table {table[0]}:")
            for col in medical_columns:
                print(f" - {col}")
    
    # Close connection
    conn.close()

if __name__ == "__main__":
    check_database_tables()