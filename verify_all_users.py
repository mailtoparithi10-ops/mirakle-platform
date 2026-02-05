
from app import create_app
from extensions import db
from models import User

app = create_app()

def verify_users():
    with app.app_context():
        print(f"\n========================================")
        print(f"            VERIFYING USERS             ")
        print(f"========================================")
        
        users = [
            ("startup@test.com", "test123", "startup"),
            ("corporate@test.com", "test123", "corporate"),
            ("enabler@test.com", "test123", "enabler"),
            ("admin@mirakle.local", "admin123", "admin")
        ]
        
        for email, password, expected_role in users:
            print(f"\n[CHECKING] {email}")
            user = User.query.filter_by(email=email).first()
            
            if not user:
                print(f"[FAIL] User NOT FOUND in database!")
                continue
                
            print(f"[FOUND] User ID: {user.id}")
            match_str = "MATCH" if user.role == expected_role else f"MISMATCH - Expected {expected_role}"
            print(f"   Role: {user.role} [{match_str}]")
            
            if user.check_password(password):
                print(f"[PASS] Password '{password}' is CORRECT")
            else:
                print(f"[FAIL] Password '{password}' is INCORRECT")
                # Reset it now
                user.set_password(password)
                db.session.commit()
                print(f"   [FIX] Reset password to '{password}'")
                
        print(f"\n========================================\n")

if __name__ == "__main__":
    verify_users()
