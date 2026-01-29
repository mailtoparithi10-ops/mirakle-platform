#!/usr/bin/env python3
"""
Reset password for startup test user
"""

from app import app
from extensions import db
from models import User

def main():
    with app.app_context():
        # Find startup test user
        user = User.query.filter_by(email='startup@test.com').first()
        
        if user:
            print(f"Found user: {user.name} ({user.email}) - Role: {user.role}")
            user.set_password('password123')
            db.session.commit()
            print("✅ Password reset to 'password123'")
        else:
            print("❌ User not found")

if __name__ == "__main__":
    main()