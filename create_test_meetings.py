#!/usr/bin/env python3
"""
Create test meetings for different user types
"""

from app import create_app
from models import Meeting, MeetingParticipant, User
from extensions import db
from datetime import datetime, timedelta
import string, random

def create_test_meetings():
    """Create test meetings for all user types"""
    
    app = create_app()
    with app.app_context():
        admin = User.query.filter_by(role='admin').first()
        if not admin:
            print('❌ No admin found')
            return
        
        # Create meetings for different access types
        meetings_to_create = [
            {
                'title': 'All Users Weekly Sync',
                'description': 'Weekly sync meeting for all platform users',
                'access_type': 'all_users',
                'hours_from_now': 1
            },
            {
                'title': 'Corporate Strategy Meeting',
                'description': 'Quarterly strategy discussion for corporate partners',
                'access_type': 'corporate_only',
                'hours_from_now': 3
            },
            {
                'title': 'Connector Network Meetup',
                'description': 'Monthly networking event for connectors and enablers',
                'access_type': 'connector_only',
                'hours_from_now': 5
            },
            {
                'title': 'Startup Pitch Session',
                'description': 'Weekly pitch session for startup founders',
                'access_type': 'startup_only',
                'hours_from_now': 7
            }
        ]
        
        for meeting_data in meetings_to_create:
            # Check if meeting already exists
            existing = Meeting.query.filter_by(title=meeting_data['title']).first()
            if existing:
                print(f'⚠️  Meeting already exists: {meeting_data["title"]}')
                continue
                
            room_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            
            meeting = Meeting(
                created_by_id=admin.id,
                title=meeting_data['title'],
                description=meeting_data['description'],
                scheduled_at=datetime.utcnow() + timedelta(hours=meeting_data['hours_from_now']),
                duration_minutes=60,
                access_type=meeting_data['access_type'],
                meeting_room_id=room_id,
                meeting_password=''.join(random.choices(string.ascii_letters + string.digits, k=8)),
                meeting_url=f'/meeting/join/{room_id}'
            )
            
            db.session.add(meeting)
            db.session.flush()
            
            # Add participants based on access type
            if meeting_data['access_type'] == 'all_users':
                users = User.query.filter_by(is_active=True).all()
            elif meeting_data['access_type'] == 'startup_only':
                users = User.query.filter(User.role.in_(['startup', 'founder']), User.is_active == True).all()
            elif meeting_data['access_type'] == 'corporate_only':
                users = User.query.filter_by(role='corporate', is_active=True).all()
            elif meeting_data['access_type'] == 'connector_only':
                users = User.query.filter(User.role.in_(['connector', 'enabler']), User.is_active == True).all()
            else:
                users = []
            
            for user in users:
                participant = MeetingParticipant(
                    meeting_id=meeting.id,
                    user_id=user.id,
                    is_moderator=(user.id == admin.id)
                )
                db.session.add(participant)
            
            print(f'✅ Created meeting: {meeting.title} for {len(users)} users')
        
        db.session.commit()
        print('🎉 All meetings created successfully!')

if __name__ == "__main__":
    create_test_meetings()