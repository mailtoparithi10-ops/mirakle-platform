#!/usr/bin/env python3
"""
Simple database viewer
"""

from app import create_app
from extensions import db
from models import User, Startup

def view_db():
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*60)
        print("DATABASE CONTENTS")
        print("="*60)
        
        # Users
        print("\nUSERS:")
        users = User.query.all()
        for u in users:
            print(f"  [{u.id}] {u.name} ({u.email}) - Role: {u.role}")
        print(f"Total: {len(users)} users")
        
        # Startups
        print("\nSTARTUPS:")
        startups = Startup.query.all()
        for s in startups:
            print(f"  [{s.id}] {s.name} - Founder ID: {s.founder_id} - Status: {s.application_status}")
        print(f"Total: {len(startups)} startups")
        
        print("\n" + "="*60)

if __name__ == "__main__":
    view_db()
