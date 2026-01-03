"""
Script to view all users in the database
Run this to see all registered users and their details
"""

import sqlite3
import os

# Database path
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'mirakle.db')

# Check if database exists
if not os.path.exists(db_path):
    print(f"Database not found at: {db_path}")
    print("Trying alternative path...")
    db_path = 'mirakle.db'
    if not os.path.exists(db_path):
        print("Database file not found!")
        exit(1)

print(f"Connecting to database: {db_path}\n")

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all users
cursor.execute("SELECT * FROM user")
users = cursor.fetchall()

# Get column names
cursor.execute("PRAGMA table_info(user)")
columns = [col[1] for col in cursor.fetchall()]

print("=" * 100)
print("ALL REGISTERED USERS")
print("=" * 100)
print()

if not users:
    print("No users found in the database.")
    print("\nYou can create test users by:")
    print("1. Going to http://localhost:5000/signup.html")
    print("2. Registering with different roles (startup, corporate, connector)")
else:
    print(f"Total users: {len(users)}\n")
    
    for user in users:
        user_dict = dict(zip(columns, user))
        print("-" * 100)
        print(f"User ID: {user_dict.get('id')}")
        print(f"Username: {user_dict.get('username')}")
        print(f"Email: {user_dict.get('email')}")
        print(f"Role: {user_dict.get('role')}")
        print(f"Full Name: {user_dict.get('full_name') or user_dict.get('first_name', 'N/A')}")
        if user_dict.get('corporate_name'):
            print(f"Company: {user_dict.get('corporate_name')}")
        print(f"Created: {user_dict.get('created_at')}")
        print()

print("=" * 100)
print("\nTEST CREDENTIALS:")
print("=" * 100)
print("\nTo test the platform, you can:")
print("1. Create new users via signup page")
print("2. Use existing user credentials shown above")
print("3. Admin login: Check if there's an admin user above")
print("\nTo create a test admin user, you can run:")
print("  python create_admin.py")

conn.close()
