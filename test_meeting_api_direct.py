#!/usr/bin/env python3
"""
Test meeting API directly using Flask test client
"""

from app import create_app
from models import User

def test_meeting_api():
    """Test meeting API using Flask test client"""
    
    print("🧪 Testing Meeting API Directly")
    print("=" * 50)
    
    app = create_app()
    
    with app.test_client() as client:
        with app.app_context():
            # Get test user
            user = User.query.filter_by(email='test@startup.com').first()
            if not user:
                print("❌ Test user not found")
                return
            
            print(f"✅ Found test user: {user.name} ({user.role})")
            
            # Simulate login by setting session
            with client.session_transaction() as sess:
                sess['_user_id'] = str(user.id)
                sess['_fresh'] = True
            
            # Test meeting API
            print("\n🔍 Testing /api/meetings/my-meetings...")
            response = client.get('/api/meetings/my-meetings')
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.get_json()
                print("✅ API Response successful")
                print(f"   Success: {data.get('success')}")
                print(f"   Upcoming meetings: {len(data.get('upcoming_meetings', []))}")
                print(f"   Past meetings: {len(data.get('past_meetings', []))}")
                
                # Print meeting details
                for meeting in data.get('upcoming_meetings', []):
                    print(f"   - {meeting['title']} ({meeting['access_type']}) at {meeting['scheduled_at']}")
                    
            else:
                print(f"❌ API failed with status {response.status_code}")
                print(f"   Response: {response.get_data(as_text=True)}")

if __name__ == "__main__":
    test_meeting_api()