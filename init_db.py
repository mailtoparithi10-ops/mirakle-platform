"""
Initialize database with proper schema
"""

import sqlite3
import os

# Database path
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'mirakle.db')

# Create instance directory if it doesn't exist
os.makedirs(os.path.dirname(db_path), exist_ok=True)

print(f"Database path: {db_path}\n")

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check existing tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("Existing tables:")
if tables:
    for table in tables:
        print(f"  - {table[0]}")
else:
    print("  No tables found")

print("\nCreating user table if it doesn't exist...")

# Create user table
cursor.execute("""
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,
    full_name VARCHAR(200),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    corporate_name VARCHAR(200),
    phone_number VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
print("✓ User table created successfully")

# Verify table was created
cursor.execute("PRAGMA table_info(user)")
columns = cursor.fetchall()

print("\nUser table schema:")
for col in columns:
    print(f"  - {col[1]} ({col[2]})")

conn.close()

print("\n" + "=" * 80)
print("Database initialized successfully!")
print("=" * 80)
print("\nNext steps:")
print("1. Run: python create_test_users.py  (to create test accounts)")
print("2. Run: python view_users.py  (to view all users)")
print("3. Start the app: python app.py")
