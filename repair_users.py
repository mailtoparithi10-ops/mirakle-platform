
import sqlite3
import os
from werkzeug.security import generate_password_hash
from datetime import datetime

# Database path
db_path = os.path.join(os.path.dirname(__file__), 'instance', 'mirakle.db')

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

print(f"Connecting to database: {db_path}\n")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Test users to update
test_users = [
    {'email': 'admin@test.com', 'password': 'admin123'},
    {'email': 'startup@test.com', 'password': 'startup123'},
    {'email': 'corporate@test.com', 'password': 'corporate123'},
    {'email': 'connector@test.com', 'password': 'connector123'}
]

print("Updating user passwords to compatible format...")
print("=" * 80)

for user in test_users:
    # Generate compatible hash using werkzeug
    new_hash = generate_password_hash(user['password'])
    
    # Update user in 'users' table (using the plural table name as per models.py)
    cursor.execute("UPDATE users SET password_hash = ? WHERE email = ?", (new_hash, user['email']))
    
    if cursor.rowcount > 0:
        print(f"✓ Updated password for {user['email']}")
    else:
        print(f"⚠ User {user['email']} not found in 'users' table")

conn.commit()
conn.close()

print("\nDone. Please try logging in again.")
