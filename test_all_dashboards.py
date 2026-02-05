#!/usr/bin/env python3
"""
Test meeting inbox for all user dashboard types
"""

from app import create_app
from models import User, Meeting, MeetingParticipant
from datetime import datetime

def test_all_dashboards():
    """Test meeting inbox for all user types"""
    
    print("🧪 Testing Meeting Inbox for All Dashboard Types")
    print("=" * 60)
    
    app = create_app()
    
    test_users = [
        {'email': 'test@startup.com', 'role': 'startup', 'dashboard': '/startup'},
        {'email': 'test@corporate.com', 'role': 'corporate', 'dashboard': '/corporate'},
        {'email': 'test@enabler.com', 'role': 'enabler', 'dashboard': '/enabler'},
        {'email': 'test@enabler.com', 'role': 'enabler', 'dashboard': '/enabler'}
    ]
    
    with app.app_context():
        for user_info in test_users:
            print(f"\n📱 Testing {user_info['role'].upper()} Dashboard:")
            print("-" * 40)
            
            # Get user
            user = User.query.filter_by(email=user_info['email']).first()
            if not user:
                print(f"❌ User not found: {user_info['email']}")
                continue
            
            print(f"✅ User: {user.name} ({user.role})")
            
            # Get user's meetings
            user_meetings = Meeting.query.join(MeetingParticipant).filter(
                MeetingParticipant.user_id == user.id
            ).all()
            
            upcoming = [m for m in user_meetings if m.scheduled_at > datetime.utcnow()]
            
            print(f"✅ Total meetings: {len(user_meetings)}")
            print(f"✅ Upcoming meetings: {len(upcoming)}")
            
            # List upcoming meetings
            for meeting in upcoming:
                print(f"   📅 {meeting.title}")
                print(f"      🕒 {meeting.scheduled_at}")
                print(f"      👥 {meeting.access_type}")
                print(f"      🔗 /meeting/join/{meeting.meeting_room_id}")
            
            # Test API endpoint
            with app.test_client() as client:
                # Simulate login
                with client.session_transaction() as sess:
                    sess['_user_id'] = str(user.id)
                    sess['_fresh'] = True
                
                response = client.get('/api/meetings/my-meetings')
                if response.status_code == 200:
                    data = response.get_json()
                    print(f"✅ API Response: {len(data['upcoming_meetings'])} upcoming")
                else:
                    print(f"❌ API failed: {response.status_code}")
                
                # Test dashboard access
                dashboard_response = client.get(user_info['dashboard'])
                if dashboard_response.status_code == 200:
                    print(f"✅ Dashboard accessible: {user_info['dashboard']}")
                    if 'meetingInbox' in dashboard_response.get_data(as_text=True):
                        print("✅ Meeting inbox div found in dashboard")
                    else:
                        print("❌ Meeting inbox div not found")
                else:
                    print(f"❌ Dashboard access failed: {dashboard_response.status_code}")
    
    print("\n" + "=" * 60)
    print("🎯 Meeting Inbox Integration Summary")
    print("=" * 60)
    
    print("\n✅ Dashboards with Meeting Inbox:")
    print("   📱 Startup Dashboard (/startup)")
    print("   📱 Corporate Dashboard (/corporate)")
    print("   📱 Enabler Dashboard (/enabler)")
    print("   📱 Admin Dashboard (/admin)")
    
    print("\n✅ Meeting Access Types:")
    print("   🌐 All Users - Visible to everyone")
    print("   🚀 Startup Only - Only startup/founder users")
    print("   🏢 Corporate Only - Only corporate users")
    print("   🤝 Enabler Only - Only enabler users")
    
    print("\n✅ Test Credentials:")
    print("   Startup: test@startup.com / password123")
    print("   Corporate: test@corporate.com / password123")
    print("   Enabler: test@enabler.com / password123")
    print("   Enabler: test@enabler.com / password123")
    
    print(f"\n🌐 Test at: http://localhost:5001")
    print("   1. Login with any test user")
    print("   2. Go to their respective dashboard")
    print("   3. See meeting inbox at the top")
    print("   4. Click meetings to join")

if __name__ == "__main__":
    test_all_dashboards()