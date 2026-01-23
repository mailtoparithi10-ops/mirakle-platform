#!/usr/bin/env python3
"""
Test script to verify admin meeting inbox functionality
"""
import requests
import json
from datetime import datetime

def test_admin_meeting_access():
    print("🧪 Testing Admin Meeting Inbox Access")
    print("=" * 50)
    
    base_url = "http://localhost:5001"
    
    # Test admin login
    login_data = {
        "email": "admin@test.com",
        "password": "admin123"
    }
    
    session = requests.Session()
    
    print("1. Testing admin login...")
    login_response = session.post(f"{base_url}/auth/login", data=login_data)
    
    if login_response.status_code == 200:
        print("✅ Admin login successful")
    else:
        print("❌ Admin login failed")
        return
    
    # Test meeting access
    print("\n2. Testing admin meeting access...")
    meetings_response = session.get(f"{base_url}/api/meetings/my-meetings")
    
    if meetings_response.status_code == 200:
        print("✅ Admin can access meetings API")
        
        meetings_data = meetings_response.json()
        if meetings_data.get('success'):
            upcoming = meetings_data.get('upcoming_meetings', [])
            past = meetings_data.get('past_meetings', [])
            
            print(f"📊 Admin Meeting Stats:")
            print(f"   - Upcoming meetings: {len(upcoming)}")
            print(f"   - Past meetings: {len(past)}")
            
            if upcoming:
                print(f"\n📅 Upcoming Meetings for Admin:")
                for meeting in upcoming[:3]:
                    scheduled = datetime.fromisoformat(meeting['scheduled_at'].replace('Z', '+00:00'))
                    print(f"   • {meeting['title']}")
                    print(f"     Time: {scheduled.strftime('%Y-%m-%d %H:%M')}")
                    print(f"     Access: {meeting['access_type']}")
                    print(f"     Participants: {meeting['participant_count']}")
                    print()
            else:
                print("📭 No upcoming meetings found for admin")
        else:
            print("❌ Meeting API returned error:", meetings_data.get('error'))
    else:
        print("❌ Admin cannot access meetings API")
        print(f"Status: {meetings_response.status_code}")
        print(f"Response: {meetings_response.text}")
    
    # Test admin dashboard access
    print("\n3. Testing admin dashboard access...")
    dashboard_response = session.get(f"{base_url}/admin")
    
    if dashboard_response.status_code == 200:
        print("✅ Admin dashboard accessible")
        
        # Check if meeting inbox is in the HTML
        if 'meetingInbox' in dashboard_response.text:
            print("✅ Meeting inbox widget found in admin dashboard")
        else:
            print("❌ Meeting inbox widget NOT found in admin dashboard")
            
        if 'meetings.js' in dashboard_response.text:
            print("✅ meetings.js script included in admin dashboard")
        else:
            print("❌ meetings.js script NOT included in admin dashboard")
    else:
        print("❌ Admin dashboard not accessible")
    
    print("\n" + "=" * 50)
    print("🎯 Admin Meeting Inbox Test Complete!")

if __name__ == "__main__":
    test_admin_meeting_access()