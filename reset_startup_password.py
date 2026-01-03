"""
Reset password for startup@test.com
"""
from app import create_app
from extensions import db
from models import User

app = create_app()

EMAIL = "startup@test.com"
NEW_PASSWORD = "test123"

with app.app_context():
    user = User.query.filter_by(email=EMAIL).first()
    
    if user:
        user.set_password(NEW_PASSWORD)
        db.session.commit()
        print(f"\n[SUCCESS] Password reset successful!")
        print(f"  Email: {EMAIL}")
        print(f"  New Password: {NEW_PASSWORD}")
        print(f"\nYou can now login at: http://127.0.0.1:5000/login")
        print(f"Or debug page: http://127.0.0.1:5000/login-debug\n")
    else:
        print(f"\n[ERROR] User not found: {EMAIL}\n")
