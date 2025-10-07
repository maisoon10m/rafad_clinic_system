"""
Add last_login column to users table
"""
import sqlite3
import os

def add_last_login_column():
    # Get the database file path from the config
    from app import create_app
    app = create_app('development')
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    
    # Ensure the database file exists
    if not os.path.exists(db_path):
        print(f"Database file not found: {db_path}")
        return False
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if the column already exists
    cursor.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in cursor.fetchall()]
    if 'last_login' in columns:
        print("Column 'last_login' already exists in the 'users' table.")
        conn.close()
        return True
    
    # Add the column
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN last_login TIMESTAMP")
        conn.commit()
        print("Column 'last_login' added to the 'users' table.")
        result = True
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Error adding column: {e}")
        result = False
    
    conn.close()
    return result

if __name__ == '__main__':
    add_last_login_column()