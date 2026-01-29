#!/usr/bin/env python3
"""
Check users in the database
"""

from app import app
from extensions import db
from models import User

def main():
    with app.app_context():
        users = User.query.all()
        print("Users in database:")
        print("="*50)
        
        if not users:
            print("No users found!")
            return
            
        for user in users:
            print(f"Email: {user.email}")
            print(f"Role: {user.role}")
            print(f"Name: {user.name}")
            print(f"Active: {user.is_active}")
            print("-" * 30)

if __name__ == "__main__":
    main()