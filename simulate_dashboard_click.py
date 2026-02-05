#!/usr/bin/env python3
"""
Simulate clicking the dashboard button from the homepage
"""

from app import create_app
from models import User, Startup

def simulate_dashboard_click():
    app = create_app()
    
    with app.test_client() as client:
        with app.app_context():
            print("🖱️  Simulating dashboard button click...")
            
            # Test with different types of users
            test_users = [
                'priya@startup.in',  # Has incomplete startup
                'flowtest@startup.com',  # Has complete startup
                'founder1@test.com'  # No startup at all
            ]
            
            for email in test_users:
                user = User.query.filter_by(email=email).first()
                if not user:
                    print(f"❌ User {email} not found")
                    continue
                
                startup = Startup.query.filter_by(founder_id=user.id).first()
                
                print(f"\n👤 Testing: {user.name} ({email})")
                print(f"📊 Startup: {'Yes' if startup else 'No'}")
                
                if startup:
                    print(f"   Name: {startup.name}")
                    print(f"   Status: {startup.application_status}")
                    complete = bool(startup.description and startup.location)
                    print(f"   Complete: {complete}")
                
                # Login simulation
                with client.session_transaction() as sess:
                    sess['_user_id'] = str(user.id)
                    sess['_fresh'] = True
                
                # Step 1: Visit homepage (where dashboard button is)
                response = client.get('/')
                print(f"🏠 Homepage: {response.status_code}")
                
                # Step 2: Click dashboard button (simulated)
                # The dashboard button points to /startup
                response = client.get('/startup')
                print(f"🖱️  Click DASHBOARD button (/startup): {response.status_code}")
                
                if response.status_code == 302:
                    print(f"   🔄 Redirected to: {response.location}")
                    
                    # Follow the redirect
                    response2 = client.get(response.location)
                    print(f"   📄 Final page: {response2.status_code}")
                    
                    if 'apply' in response.location:
                        print("   ❌ ISSUE: Redirected to application form!")
                    elif 'dashboard' in response.location:
                        print("   ✅ Correctly redirected to dashboard")
                    
                elif response.status_code == 200:
                    print("   ✅ Dashboard loaded directly")
                
                # Also test the direct dashboard URL
                response = client.get('/startup/dashboard')
                print(f"📊 Direct dashboard: {response.status_code}")
                
                if response.status_code == 302:
                    print(f"   🔄 Redirected to: {response.location}")
                    if 'apply' in response.location:
                        print("   ❌ ISSUE: Dashboard redirects to application!")

if __name__ == "__main__":
    simulate_dashboard_click()