
import sqlite3
import os

db_path = 'instance/mirakle.db'

def migrate():
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if column already exists
        cursor.execute("PRAGMA table_info(opportunities)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'banner_url' not in columns:
            print("Adding banner_url column to opportunities table...")
            cursor.execute("ALTER TABLE opportunities ADD COLUMN banner_url VARCHAR(500)")
            conn.commit()
            print("Column added successfully!")
        else:
            print("banner_url column already exists.")
            
    except Exception as e:
        print(f"Error during migration: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
