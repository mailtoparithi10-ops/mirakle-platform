"""
Fix database schema and create test users matching the actual User model
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash
from datetime import datetime

# Database path
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'mirakle.db')

if not os.path.exists(db_path):
    db_path = 'mirakle.db'

print(f"Database path: {db_path}\n")

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if 'users' table exists (correct table name from models.py)
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
if not cursor.fetchone():
    print("Creating 'users' table...")
    cursor.execute("""
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(140) NOT NULL,
        email VARCHAR(180) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        role VARCHAR(40) DEFAULT 'founder',
        country VARCHAR(120),
        region VARCHAR(120),
        company VARCHAR(200),
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    print("✓ Users table created\n")

# Test users matching the actual model
test_users = [
    {
        'name': 'Admin User',
        'email': 'admin@test.com',
        'password': 'admin123',
        'role': 'admin',
        'company': 'InnoBridge'
    },
    {
        'name': 'John Startup',
        'email': 'startup@test.com',
        'password': 'startup123',
        'role': 'startup',
        'company': 'Test Startup Inc.'
    },
    {
        'name': 'Jane Corporate',
        'email': 'corporate@test.com',
        'password': 'corporate123',
        'role': 'corporate',
        'company': 'Test Corporation'
    },
    {
        'name': 'Bob Connector',
        'email': 'connector@test.com',
        'password': 'connector123',
        'role': 'connector',
        'company': 'Connector Network'
    }
]

print("Creating test users...")
print("=" * 80)

for user_data in test_users:
    # Check if user already exists
    cursor.execute("SELECT id FROM users WHERE email = ?", (user_data['email'],))
    existing = cursor.fetchone()
    
    if existing:
        print(f"✗ User {user_data['email']} already exists (ID: {existing[0]})")
        continue
    
    # Hash password using werkzeug (same as models.py)
    password_hash = generate_password_hash(user_data['password'])
    
    # Insert user
    cursor.execute("""
        INSERT INTO users (name, email, password_hash, role, company, is_active, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        user_data['name'],
        user_data['email'],
        password_hash,
        user_data['role'],
        user_data.get('company'),
        True,
        datetime.utcnow()
    ))
    
    print(f"✓ Created {user_data['role']} user: {user_data['email']}")

conn.commit()

# Show all users
cursor.execute("SELECT id, name, email, role FROM users")
users = cursor.fetchall()

print("\n" + "=" * 80)
print("ALL USERS IN DATABASE:")
print("=" * 80)
for user in users:
    print(f"ID: {user[0]} | Name: {user[1]} | Email: {user[2]} | Role: {user[3]}")

conn.close()

print("\n" + "=" * 80)
print("TEST CREDENTIALS:")
print("=" * 80)
print("\nAdmin:")
print("  Email: admin@test.com")
print("  Password: admin123")
print("\nStartup:")
print("  Email: startup@test.com")
print("  Password: startup123")
print("\nCorporate:")
print("  Email: corporate@test.com")
print("  Password: corporate123")
print("\nConnector:")
print("  Email: connector@test.com")
print("  Password: connector123")
print("\n" + "=" * 80)
print("\nLogin at: http://localhost:5000/login.html")
print("Admin login at: http://localhost:5000/admin/login")
