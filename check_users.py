"""
Quick script to check users and create a test admin user if needed
"""
from app import create_app
from extensions import db
from models import User

app = create_app()

with app.app_context():
    # Check existing users
    users = User.query.all()
    print(f"\n=== Found {len(users)} users in database ===")
    
    for user in users:
        print(f"- {user.email} (Role: {user.role}, Active: {user.is_active})")
    
    # Create test admin user if no users exist
    if len(users) == 0:
        print("\n=== Creating test admin user ===")
        admin = User(
            name="Admin User",
            email="admin@test.com",
            role="admin",
            company="Test Company"
        )
        admin.set_password("admin123")
        db.session.add(admin)
        db.session.commit()
        print("✓ Test admin created: admin@test.com / admin123")
    
    print("\n=== Login Instructions ===")
    print("1. Server is running at: http://127.0.0.1:5000")
    print("2. Go to: http://127.0.0.1:5000/auth/login")
    print("3. Use one of the credentials above to login")
    print()
