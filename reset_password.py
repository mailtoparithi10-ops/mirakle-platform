"""
Reset password for a user - useful for testing
"""
from app import create_app
from extensions import db
from models import User

app = create_app()

# Change these values
EMAIL = "admin@mirakle.local"
NEW_PASSWORD = "admin123"

with app.app_context():
    user = User.query.filter_by(email=EMAIL).first()
    
    if user:
        user.set_password(NEW_PASSWORD)
        db.session.commit()
        print("\n[SUCCESS] Password reset successful!")
        print(f"  Email: {EMAIL}")
        print(f"  New Password: {NEW_PASSWORD}")
        print(f"\nYou can now login at: http://127.0.0.1:5000/auth/login\n")
    else:
        print(f"\n[ERROR] User not found: {EMAIL}\n")
