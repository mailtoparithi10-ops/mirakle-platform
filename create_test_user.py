#!/usr/bin/env python3
"""
Create a test user for testing the meeting system
"""

from app import create_app
from extensions import db
from models import User

def create_test_user():
    """Create a test startup user"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if test user already exists
            test_user = User.query.filter_by(email="test@startup.com").first()
            
            if test_user:
                print("✅ Test user already exists")
                print(f"   Email: test@startup.com")
                print(f"   Password: password123")
                print(f"   Role: {test_user.role}")
                return True
            
            # Create test user
            test_user = User(
                name="Test Startup User",
                email="test@startup.com",
                role="startup",
                company="Test Startup Inc",
                country="USA"
            )
            test_user.set_password("password123")
            
            db.session.add(test_user)
            db.session.commit()
            
            print("✅ Test user created successfully!")
            print(f"   Email: test@startup.com")
            print(f"   Password: password123")
            print(f"   Role: startup")
            
        except Exception as e:
            print(f"❌ Error creating test user: {e}")
            return False
    
    return True

if __name__ == "__main__":
    create_test_user()