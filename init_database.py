"""
Initialize database with all required tables from models.py
"""
import os
from app import create_app
from extensions import db
from models import User, Startup, Opportunity, Application, Referral, Meeting, MeetingParticipant, ContactMessage
from passlib.hash import bcrypt
from datetime import datetime

print("Initializing database...")
print("=" * 80)

app = create_app()

with app.app_context():
    try:
        # Create all tables
        print("Creating all database tables...")
        db.create_all()
        print("✓ Tables created successfully\n")
        
        # Check if admin user exists
        admin = User.query.filter_by(email='admin@test.com').first()
        
        if not admin:
            print("Creating test users...")
            
            # Create test users
            test_users = [
                User(
                    name='Admin User',
                    email='admin@test.com',
                    password_hash=bcrypt.hash('admin123'),
                    role='admin',
                    company='InnoBridge',
                    is_active=True
                ),
                User(
                    name='John Startup',
                    email='startup@test.com',
                    password_hash=bcrypt.hash('startup123'),
                    role='startup',
                    company='Test Startup Inc.',
                    is_active=True
                ),
                User(
                    name='Jane Corporate',
                    email='corporate@test.com',
                    password_hash=bcrypt.hash('corporate123'),
                    role='corporate',
                    company='Test Corporation',
                    is_active=True
                ),
                User(
                    name='Bob Connector',
                    email='connector@test.com',
                    password_hash=bcrypt.hash('connector123'),
                    role='connector',
                    company='Connector Network',
                    is_active=True
                )
            ]
            
            for user in test_users:
                db.session.add(user)
                print(f"  ✓ Created {user.role}: {user.email}")
            
            db.session.commit()
            print("\n✓ All test users created successfully!")
        else:
            print("Test users already exist")
        
        # Display all users
        all_users = User.query.all()
        print("\n" + "=" * 80)
        print("ALL USERS IN DATABASE:")
        print("=" * 80)
        for user in all_users:
            print(f"ID: {user.id} | Name: {user.name} | Email: {user.email} | Role: {user.role}")

        print("\n" + "=" * 80)
        print("DATABASE INITIALIZED SUCCESSFULLY!")
        print("=" * 80)
        
        # Only show test credentials in development
        if not os.environ.get('DATABASE_URL'):
            print("\nTest Credentials:")
            print("  Admin:     admin@test.com / admin123")
            print("  Startup:   startup@test.com / startup123")
            print("  Corporate: corporate@test.com / corporate123")
            print("  Connector: connector@test.com / connector123")
            print("\nLogin at: http://localhost:5000/login.html")
        else:
            print("\nProduction database initialized successfully!")
        
        print("=" * 80)
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise
