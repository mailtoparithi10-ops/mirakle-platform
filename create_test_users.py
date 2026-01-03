"""
Script to create test users for testing the platform
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash
from datetime import datetime

# Database path
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'mirakle.db')

if not os.path.exists(db_path):
    db_path = 'mirakle.db'
    if not os.path.exists(db_path):
        print("Database file not found!")
        exit(1)

print(f"Connecting to database: {db_path}\n")

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Test users to create
test_users = [
    {
        'username': 'admin_test',
        'email': 'admin@test.com',
        'password': 'admin123',
        'role': 'admin',
        'full_name': 'Admin User'
    },
    {
        'username': 'startup_test',
        'email': 'startup@test.com',
        'password': 'startup123',
        'role': 'startup',
        'first_name': 'John',
        'last_name': 'Startup'
    },
    {
        'username': 'corporate_test',
        'email': 'corporate@test.com',
        'password': 'corporate123',
        'role': 'corporate',
        'full_name': 'Jane Corporate',
        'corporate_name': 'Test Corporation Inc.'
    },
    {
        'username': 'connector_test',
        'email': 'connector@test.com',
        'password': 'connector123',
        'role': 'connector',
        'full_name': 'Bob Connector'
    }
]

print("Creating test users...")
print("=" * 80)

for user_data in test_users:
    # Check if user already exists
    cursor.execute("SELECT id FROM user WHERE email = ?", (user_data['email'],))
    existing = cursor.fetchone()
    
    if existing:
        print(f"✗ User {user_data['email']} already exists (ID: {existing[0]})")
        continue
    
    # Hash password
    password_hash = generate_password_hash(user_data['password'])
    
    # Insert user
    cursor.execute("""
        INSERT INTO user (username, email, password_hash, role, full_name, first_name, last_name, corporate_name, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_data['username'],
        user_data['email'],
        password_hash,
        user_data['role'],
        user_data.get('full_name'),
        user_data.get('first_name'),
        user_data.get('last_name'),
        user_data.get('corporate_name'),
        datetime.utcnow().isoformat()
    ))
    
    print(f"✓ Created {user_data['role']} user: {user_data['email']}")

conn.commit()
conn.close()

print("\n" + "=" * 80)
print("TEST USER CREDENTIALS:")
print("=" * 80)
print("\nAdmin User:")
print("  Email: admin@test.com")
print("  Password: admin123")
print("\nStartup User:")
print("  Email: startup@test.com")
print("  Password: startup123")
print("\nCorporate User:")
print("  Email: corporate@test.com")
print("  Password: corporate123")
print("\nConnector User:")
print("  Email: connector@test.com")
print("  Password: connector123")
print("\n" + "=" * 80)
print("\nYou can now login with these credentials at:")
print("  http://localhost:5000/login.html")
print("\nAdmin dashboard:")
print("  http://localhost:5000/admin_login.html")
