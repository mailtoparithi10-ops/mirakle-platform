#!/usr/bin/env python3
"""
Create enabler test user in production database - Render Compatible
This script works with both local and Render production environments
"""

import os
import sys

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_enabler_user():
    """Create or update enabler test user for production"""
    try:
        from app import create_app
        from extensions import db
        from models import User
        
        app = create_app()
        
        with app.app_context():
            print("=" * 80)
            print("CREATING ENABLER TEST USER FOR PRODUCTION")
            print("=" * 80)
            
            email = "enabler@test.com"
            password = "enabler123"
            
            # Check if user exists
            user = User.query.filter_by(email=email).first()
            
            if user:
                print(f"\n✓ User exists: {email}")
                print(f"  Current role: {user.role}")
                print(f"  Updating password and ensuring active status...")
                
                # Update user
                user.set_password(password)
                user.role = "enabler"
                user.is_active = True
                if not user.name:
                    user.name = "Test Enabler"
                
                db.session.commit()
                print(f"  ✓ Updated successfully")
            else:
                print(f"\n+ Creating new user: {email}")
                
                # Create new user
                new_user = User(
                    email=email,
                    role="enabler",
                    name="Test Enabler",
                    is_active=True
                )
                new_user.set_password(password)
                
                db.session.add(new_user)
                db.session.commit()
                print(f"  ✓ Created successfully")
            
            # Verify user
            user = User.query.filter_by(email=email).first()
            
            print("\n" + "=" * 80)
            print("USER VERIFICATION")
            print("=" * 80)
            print(f"\nEmail: {user.email}")
            print(f"Role: {user.role}")
            print(f"Name: {user.name}")
            print(f"Active: {user.is_active}")
            print(f"ID: {user.id}")
            
            # Test password
            if user.check_password(password):
                print(f"\n✅ Password verification: SUCCESS")
            else:
                print(f"\n❌ Password verification: FAILED")
            
            print("\n" + "=" * 80)
            print("LOGIN CREDENTIALS")
            print("=" * 80)
            print(f"\nEmail: {email}")
            print(f"Password: {password}")
            print(f"Login URL: /enabler/login")
            print(f"Dashboard: /enabler/dashboard")
            print("\n" + "=" * 80)
            print("✅ ENABLER USER READY FOR PRODUCTION")
            print("=" * 80)
            
            return True
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_enabler_user()
    sys.exit(0 if success else 1)
