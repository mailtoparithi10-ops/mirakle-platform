#!/usr/bin/env python3
"""
Initialize the database with all tables using SQLAlchemy models
"""

from app import create_app
from extensions import db
from models import User, Startup, Opportunity, Application, Referral, Lead, ContactMessage, Meeting, MeetingParticipant, Notification, ReferralClick

def init_database():
    app = create_app()
    
    with app.app_context():
        print("Creating all database tables...")
        
        # Drop all tables first (fresh start)
        db.drop_all()
        print("✓ Dropped existing tables")
        
        # Create all tables
        db.create_all()
        print("✓ Created all tables")
        
        # Create test users
        print("\nCreating test users...")
        
        # Admin user
        admin = User(
            name="Admin User",
            email="admin@test.com",
            role="admin",
            is_active=True
        )
        admin.set_password("admin123")
        db.session.add(admin)
        
        # Startup user
        startup_user = User(
            name="Startup Founder",
            email="startup@test.com",
            role="startup",
            is_active=True
        )
        startup_user.set_password("startup123")
        db.session.add(startup_user)
        
        # Corporate user
        corporate = User(
            name="Corporate User",
            email="corporate@test.com",
            role="corporate",
            company="Tech Corp",
            is_active=True
        )
        corporate.set_password("corporate123")
        db.session.add(corporate)
        
        # Enabler user
        enabler = User(
            name="Enabler User",
            email="enabler@test.com",
            role="enabler",
            is_active=True
        )
        enabler.set_password("enabler123")
        db.session.add(enabler)
        
        db.session.commit()
        print("✓ Created test users")
        
        print("\n" + "=" * 80)
        print("Database initialized successfully!")
        print("=" * 80)
        print("\nTest Credentials:")
        print("  Admin:     admin@test.com / admin123")
        print("  Startup:   startup@test.com / startup123")
        print("  Corporate: corporate@test.com / corporate123")
        print("  Enabler:   enabler@test.com / enabler123")
        print("\nYou can now run: python run_local.py")

if __name__ == "__main__":
    init_database()
