#!/usr/bin/env python3
"""
Test login and meeting API access
"""

import requests
import json

# Base URL for the Flask app
BASE_URL = "http://localhost:5001"

def test_login_and_meetings():
    """Test login and meeting access"""
    
    print("🔐 Testing Login and Meeting Access")
    print("=" * 50)
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    # Test 1: Login with test user
    print("\n1. Testing login...")
    login_data = {
        "email": "test@startup.com",
        "password": "password123"
    }
    
    try:
        response = session.post(f"{BASE_URL}/auth/login", data=login_data)
        if response.status_code == 200 and "dashboard" in response.url:
            print("✅ Login successful")
        else:
            print(f"❌ Login failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False
    
    # Test 2: Access meeting API after login
    print("\n2. Testing meeting API access...")
    try:
        response = session.get(f"{BASE_URL}/api/meetings/my-meetings")
        if response.status_code == 200:
            data = response.json()
            print("✅ Meeting API accessible")
            print(f"   Upcoming meetings: {len(data.get('upcoming_meetings', []))}")
            print(f"   Past meetings: {len(data.get('past_meetings', []))}")
            
            # Print meeting details
            for meeting in data.get('upcoming_meetings', []):
                print(f"   - {meeting['title']} ({meeting['access_type']})")
                
        else:
            print(f"❌ Meeting API failed: {response.status_code}")
            print(f"   Response: {response.text[:200]}")
    except Exception as e:
        print(f"❌ Meeting API error: {e}")
    
    # Test 3: Access startup dashboard
    print("\n3. Testing startup dashboard access...")
    try:
        response = session.get(f"{BASE_URL}/startup")
        if response.status_code == 200:
            print("✅ Startup dashboard accessible")
            if "meetingInbox" in response.text:
                print("✅ Meeting inbox div found in dashboard")
            else:
                print("❌ Meeting inbox div not found in dashboard")
        else:
            print(f"❌ Dashboard access failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Test Results Summary")
    print("=" * 50)

if __name__ == "__main__":
    test_login_and_meetings()