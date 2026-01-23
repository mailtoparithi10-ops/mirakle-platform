#!/usr/bin/env python3
"""
Create meeting tables in the database
"""

from app import create_app
from extensions import db
from models import Meeting, MeetingParticipant

def create_meeting_tables():
    """Create meeting-related tables"""
    app = create_app()
    
    with app.app_context():
        try:
            # Create tables
            db.create_all()
            print("✅ Meeting tables created successfully!")
            
            # Verify tables exist
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            meeting_tables = ['meetings', 'meeting_participants']
            for table in meeting_tables:
                if table in tables:
                    print(f"✅ Table '{table}' exists")
                else:
                    print(f"❌ Table '{table}' not found")
            
        except Exception as e:
            print(f"❌ Error creating meeting tables: {e}")
            return False
    
    return True

if __name__ == "__main__":
    create_meeting_tables()