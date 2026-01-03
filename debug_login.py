"""
Debug script to test login functionality directly
"""
from app import create_app
from models import User
from extensions import db

app = create_app()

with app.app_context():
    # Test if users exist
    print("=" * 80)
    print("TESTING LOGIN FUNCTIONALITY")
    print("=" * 80)
    print()
    
    # Check all users
    users = User.query.all()
    print(f"Total users in database: {len(users)}\n")
    
    for user in users:
        print(f"User: {user.email}")
        print(f"  ID: {user.id}")
        print(f"  Name: {user.name}")
        print(f"  Role: {user.role}")
        print(f"  Active: {user.is_active}")
        print()
    
    # Test login for admin
    print("=" * 80)
    print("TESTING PASSWORD VERIFICATION")
    print("=" * 80)
    print()
    
    test_email = 'admin@test.com'
    test_password = 'admin123'
    
    user = User.query.filter_by(email=test_email).first()
    
    if user:
        print(f"Found user: {user.email}")
        print(f"  Role: {user.role}")
        print(f"  Active: {user.is_active}")
        
        # Test password
        password_valid = user.check_password(test_password)
        print(f"  Password '{test_password}' is valid: {password_valid}")
        
        if password_valid:
            print("\n✓ Login should work!")
            print(f"  User should be redirected to: /admin")
        else:
            print("\n✗ Password check failed!")
            print("  This is why login is not working.")
    else:
        print(f"✗ User {test_email} not found in database!")
        print("  Run: python init_database.py")
    
    print("\n" + "=" * 80)
