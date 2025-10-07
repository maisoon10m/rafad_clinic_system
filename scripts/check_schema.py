"""
Script to check database schema
"""
import sqlite3
import sys

def print_schema(table_name):
    """Print the schema for a table"""
    try:
        conn = sqlite3.connect('rafad_dev.sqlite')
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        schema = cursor.fetchall()
        
        print(f"\nSchema for table '{table_name}':")
        print("-" * 80)
        print(f"{'ID':<5} {'Name':<20} {'Type':<15} {'NotNull':<10} {'DefaultVal':<20} {'PK':<5}")
        print("-" * 80)
        
        for col in schema:
            print(f"{col[0]:<5} {col[1]:<20} {col[2]:<15} {col[3]:<10} {str(col[4]):<20} {col[5]:<5}")
        
        conn.close()
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    except Exception as e:
        print(f"Error: {e}")

def list_tables():
    """List all tables in the database"""
    try:
        conn = sqlite3.connect('rafad_dev.sqlite')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("\nAvailable tables in database:")
        print("-" * 40)
        for table in tables:
            print(table[0])
        
        conn.close()
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        list_tables()
    else:
        print_schema(sys.argv[1])