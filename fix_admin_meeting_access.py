#!/usr/bin/env python3
"""
Fix admin meeting access by adding admin users to all existing meetings
"""

from app import create_app
from models import Meeting, MeetingParticipant, User
from extensions import db

def fix_admin_meeting_access():
    """Add admin users to all existing meetings"""
    
    print("🔧 Fixing Admin Meeting Access")
    print("=" * 40)
    
    app = create_app()
    
    with app.app_context():
        # Get all admin users
        admin_users = User.query.filter_by(role='admin', is_active=True).all()
        if not admin_users:
            print("❌ No admin users found")
            return
        
        print(f"✅ Found {len(admin_users)} admin users")
        for admin in admin_users:
            print(f"   - {admin.name} ({admin.email})")
        
        # Get all meetings
        meetings = Meeting.query.all()
        print(f"✅ Found {len(meetings)} meetings")
        
        added_count = 0
        
        for meeting in meetings:
            print(f"\n📅 Processing meeting: {meeting.title}")
            
            for admin in admin_users:
                # Check if admin is already a participant
                existing = MeetingParticipant.query.filter_by(
                    meeting_id=meeting.id,
                    user_id=admin.id
                ).first()
                
                if not existing:
                    # Add admin as participant with moderator privileges
                    participant = MeetingParticipant(
                        meeting_id=meeting.id,
                        user_id=admin.id,
                        is_moderator=True,
                        attendance_status='invited'
                    )
                    db.session.add(participant)
                    added_count += 1
                    print(f"   ✅ Added {admin.name} as moderator")
                else:
                    # Ensure admin has moderator privileges
                    if not existing.is_moderator:
                        existing.is_moderator = True
                        print(f"   🔧 Updated {admin.name} to moderator")
                    else:
                        print(f"   ✓ {admin.name} already has access")
        
        # Commit all changes
        try:
            db.session.commit()
            print(f"\n✅ Successfully added {added_count} admin participants")
            print("🎉 Admin users can now join any meeting!")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error updating database: {e}")

if __name__ == "__main__":
    fix_admin_meeting_access()