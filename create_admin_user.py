#!/usr/bin/env python3
"""
Script to create an admin user
"""

from extensions import db
from models import User
from app import create_app

def create_admin():
    app = create_app()
    with app.app_context():
        # Check if admin user already exists
        existing_admin = User.query.filter_by(email="admin@test.com").first()
        if existing_admin:
            print(f"Admin user with email 'admin@test.com' already exists!")
            print(f"Name: {existing_admin.name}")
            print(f"Role: {existing_admin.role}")
            return
        
        # Create new admin user
        admin_user = User(
            name="Admin User",
            email="admin@test.com",
            role="admin",
            company="InnoBridge Platform",
            country="Global",
            is_active=True
        )
        admin_user.set_password("admin123")
        
        db.session.add(admin_user)
        db.session.commit()
        
        print("✅ Successfully created admin user!")
        print(f"Email: admin@test.com")
        print(f"Password: admin123")
        print(f"Role: admin")
        print(f"Name: Admin User")

if __name__ == "__main__":
    create_admin()