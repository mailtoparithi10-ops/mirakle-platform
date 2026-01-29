#!/usr/bin/env python3
"""
Script to create test users for startup and corporate roles
"""

from extensions import db
from models import User
from app import create_app

def create_test_users():
    app = create_app()
    with app.app_context():
        users_to_create = [
            {
                "name": "Startup User",
                "email": "startup@test.com",
                "password": "startup123",
                "role": "startup",
                "company": "Test Startup Inc",
                "country": "USA"
            },
            {
                "name": "Corporate User", 
                "email": "corporate@test.com",
                "password": "corporate123",
                "role": "corporate",
                "company": "Test Corporation",
                "country": "USA"
            }
        ]
        
        created_count = 0
        
        for user_data in users_to_create:
            # Check if user already exists
            existing_user = User.query.filter_by(email=user_data["email"]).first()
            if existing_user:
                print(f"User with email '{user_data['email']}' already exists!")
                print(f"  Name: {existing_user.name}")
                print(f"  Role: {existing_user.role}")
                # Update password
                existing_user.set_password(user_data["password"])
                db.session.commit()
                print(f"  ✅ Updated password to: {user_data['password']}")
                print()
            else:
                # Create new user
                new_user = User(
                    name=user_data["name"],
                    email=user_data["email"],
                    role=user_data["role"],
                    company=user_data["company"],
                    country=user_data["country"],
                    is_active=True
                )
                new_user.set_password(user_data["password"])
                
                db.session.add(new_user)
                created_count += 1
                print(f"✅ Created new user: {user_data['email']}")
                print(f"  Name: {user_data['name']}")
                print(f"  Role: {user_data['role']}")
                print(f"  Password: {user_data['password']}")
                print()
        
        if created_count > 0:
            db.session.commit()
            print(f"Successfully created {created_count} new users!")
        
        print("\n=== LOGIN CREDENTIALS ===")
        print("Startup User:")
        print("  Email: startup@test.com")
        print("  Password: startup123")
        print()
        print("Corporate User:")
        print("  Email: corporate@test.com") 
        print("  Password: corporate123")

if __name__ == "__main__":
    create_test_users()