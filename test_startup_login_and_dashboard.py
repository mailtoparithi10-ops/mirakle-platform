#!/usr/bin/env python3
"""
Test script to verify startup login and dashboard access
"""

import requests
import json

def test_startup_access():
    """Test startup user login and dashboard access"""
    base_url = "http://localhost:5001"
    
    # Create a session to maintain cookies
    session = requests.Session()
    
    print("🔍 Testing Startup Dashboard Access")
    print("="*50)
    
    # Step 1: Try to access startup dashboard (should redirect to login)
    print("\n1. Testing dashboard access without login...")
    response = session.get(f"{base_url}/startup")
    print(f"   Status: {response.status_code}")
    if response.status_code == 302 or "login" in response.url.lower():
        print("   ✅ Correctly redirects to login when not authenticated")
    else:
        print("   ❌ Should redirect to login")
    
    # Step 2: Try to login with test startup user
    print("\n2. Testing login with startup credentials...")
    login_data = {
        'email': 'startup@test.com',
        'password': 'password123'
    }
    
    response = session.post(f"{base_url}/auth/login", data=login_data)
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        try:
            json_response = response.json()
            if json_response.get('success'):
                print("   ✅ Login successful (JSON response)")
            else:
                print("   ❌ Login failed (JSON error)")
                print(f"   Response: {response.text[:200]}...")
                return False
        except:
            if "dashboard" in response.text.lower():
                print("   ✅ Login successful (HTML redirect)")
            else:
                print("   ❌ Login failed (unexpected response)")
                return False
    elif response.status_code == 302:
        print("   ✅ Login successful (redirect)")
    else:
        print("   ❌ Login failed")
        print(f"   Response: {response.text[:200]}...")
        return False
    
    # Step 3: Try to access startup dashboard after login
    print("\n3. Testing dashboard access after login...")
    response = session.get(f"{base_url}/startup")
    print(f"   Status: {response.status_code}")
    
    if response.status_code == 200:
        print("   ✅ Dashboard accessible after login")
        
        # Check if the page contains expected elements
        if "Startup Dashboard" in response.text:
            print("   ✅ Dashboard title found")
        if "loadPrograms" in response.text:
            print("   ✅ JavaScript loadPrograms function found")
        if "api/opportunities" in response.text:
            print("   ✅ API endpoint reference found")
            
        return True
    else:
        print("   ❌ Dashboard not accessible")
        return False

def main():
    success = test_startup_access()
    
    print("\n" + "="*50)
    print("🎯 DIAGNOSIS")
    print("="*50)
    
    if success:
        print("✅ Startup dashboard should be working!")
        print("\nIf you're still seeing issues:")
        print("1. Clear browser cache and cookies")
        print("2. Check browser console for JavaScript errors")
        print("3. Ensure you're logged in as a startup user")
        print("4. Try accessing: http://localhost:5001/startup")
    else:
        print("❌ There are authentication or access issues")
        print("\nTo fix:")
        print("1. Ensure test startup user exists")
        print("2. Check login credentials")
        print("3. Verify user role is 'founder' or 'startup'")

if __name__ == "__main__":
    main()