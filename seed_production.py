"""
Seed Production Database
Creates essential test users for production environment
"""
from app import app, db
from models import User
from werkzeug.security import generate_password_hash
from datetime import datetime

def seed_users():
    """Create essential test users"""
    print("🌱 Starting database seeding...")
    
    with app.app_context():
        # Ensure tables exist
        db.create_all()
        print("✅ Database tables created/verified")
        
        # Define test users
        users = [
            {
                'email': 'enabler@test.com',
                'password': 'enabler123',
                'name': 'Test Enabler',
                'role': 'enabler',
                'phone': '9876543210'
            },
            {
                'email': 'admin@test.com',
                'password': 'admin123',
                'name': 'Test Admin',
                'role': 'admin',
                'phone': '9876543211'
            },
            {
                'email': 'startup@test.com',
                'password': 'startup123',
                'name': 'Test Startup',
                'role': 'startup',
                'phone': '9876543212'
            },
            {
                'email': 'corporate@test.com',
                'password': 'corporate123',
                'name': 'Test Corporate',
                'role': 'corporate',
                'phone': '9876543213'
            }
        ]
        
        created_count = 0
        existing_count = 0
        
        for user_data in users:
            # Check if user already exists
            existing = User.query.filter_by(email=user_data['email']).first()
            
            if not existing:
                # Create new user
                user = User(
                    email=user_data['email'],
                    password_hash=generate_password_hash(user_data['password']),
                    name=user_data['name'],
                    role=user_data['role'],
                    phone=user_data.get('phone'),
                    is_active=True,
                    created_at=datetime.utcnow()
                )
                db.session.add(user)
                created_count += 1
                print(f"✅ Created: {user_data['email']} ({user_data['role']})")
            else:
                existing_count += 1
                print(f"⏭️  Exists: {user_data['email']} ({user_data['role']})")
        
        # Commit all changes
        try:
            db.session.commit()
            print(f"\n✅ Seeding complete!")
            print(f"   Created: {created_count} users")
            print(f"   Existing: {existing_count} users")
            print(f"   Total: {created_count + existing_count} users")
            
            # Display credentials
            print("\n" + "="*60)
            print("🔑 Test Credentials")
            print("="*60)
            for user_data in users:
                print(f"\n{user_data['role'].upper()}:")
                print(f"  Email: {user_data['email']}")
                print(f"  Password: {user_data['password']}")
            print("\n" + "="*60)
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error during seeding: {str(e)}")
            raise

if __name__ == '__main__':
    try:
        seed_users()
    except Exception as e:
        print(f"\n❌ Seeding failed: {str(e)}")
        exit(1)
