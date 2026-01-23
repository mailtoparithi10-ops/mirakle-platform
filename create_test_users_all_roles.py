#!/usr/bin/env python3
"""
Create test users for all roles to test meeting inbox
"""

from app import create_app
from extensions import db
from models import User

def create_test_users():
    """Create test users for all roles"""
    
    app = create_app()
    
    with app.app_context():
        test_users = [
            {
                'name': 'Test Corporate User',
                'email': 'test@corporate.com',
                'role': 'corporate',
                'company': 'Test Corp Inc',
                'country': 'USA'
            },
            {
                'name': 'Test Connector User',
                'email': 'test@connector.com',
                'role': 'connector',
                'company': 'Test Connector LLC',
                'country': 'UK'
            },
            {
                'name': 'Test Enabler User',
                'email': 'test@enabler.com',
                'role': 'enabler',
                'company': 'Test Enabler Co',
                'country': 'Canada'
            }
        ]
        
        for user_data in test_users:
            # Check if user already exists
            existing = User.query.filter_by(email=user_data['email']).first()
            if existing:
                print(f'⚠️  User already exists: {user_data["email"]}')
                continue
            
            # Create test user
            test_user = User(
                name=user_data['name'],
                email=user_data['email'],
                role=user_data['role'],
                company=user_data['company'],
                country=user_data['country']
            )
            test_user.set_password('password123')
            
            db.session.add(test_user)
            print(f'✅ Created user: {user_data["name"]} ({user_data["role"]})')
        
        db.session.commit()
        print('🎉 All test users created successfully!')
        
        print('\n📋 Test Credentials:')
        print('Startup: test@startup.com / password123')
        print('Corporate: test@corporate.com / password123')
        print('Connector: test@connector.com / password123')
        print('Enabler: test@enabler.com / password123')

if __name__ == "__main__":
    create_test_users()