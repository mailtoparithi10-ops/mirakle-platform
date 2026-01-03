
from app import create_app
from extensions import db
from models import User

app = create_app()

EMAIL = "corporate@test.com"
PASSWORD = "test123"
ROLE = "corporate"

with app.app_context():
    # Check if user already exists
    user = User.query.filter_by(email=EMAIL).first()
    
    if user:
        print(f"\n[INFO] User {EMAIL} already exists.")
        if user.role != ROLE:
            user.role = ROLE
            db.session.commit()
            print(f"[INFO] Updated role to {ROLE}.")
        user.set_password(PASSWORD)
        db.session.commit()
        print(f"[SUCCESS] Password reset to: {PASSWORD}")
    else:
        new_user = User(email=EMAIL, role=ROLE, is_active=True)
        new_user.set_password(PASSWORD)
        db.session.add(new_user)
        db.session.commit()
        print(f"\n[SUCCESS] Created new user:")
        print(f"  Email: {EMAIL}")
        print(f"  Password: {PASSWORD}")
        print(f"  Role: {ROLE}")

    print(f"\nYou can now login at: http://127.0.0.1:5001/login\n")
