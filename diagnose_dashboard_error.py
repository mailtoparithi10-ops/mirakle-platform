#!/usr/bin/env python3
"""
Diagnose specific dashboard errors
"""

from app import create_app
from models import User, Startup
import traceback

def diagnose_dashboard():
    app = create_app()
    
    with app.test_client() as client:
        with app.app_context():
            print("🔍 Diagnosing dashboard errors...")
            
            # Test 1: Check if routes are registered
            print("\n1️⃣ Checking route registration...")
            startup_routes = [rule for rule in app.url_map.iter_rules() if 'startup' in rule.rule]
            print(f"   Found {len(startup_routes)} startup-related routes")
            
            # Test 2: Check template exists
            print("\n2️⃣ Checking template...")
            try:
                import os
                template_path = os.path.join('templates', 'startup_dashboard.html')
                if os.path.exists(template_path):
                    size = os.path.getsize(template_path)
                    print(f"   ✅ Template exists ({size} bytes)")
                else:
                    print("   ❌ Template not found")
            except Exception as e:
                print(f"   ❌ Template check error: {e}")
            
            # Test 3: Check user authentication
            print("\n3️⃣ Testing authentication...")
            user = User.query.filter_by(role='founder').first()
            if user:
                print(f"   👤 Test user: {user.name}")
                
                # Simulate login
                with client.session_transaction() as sess:
                    sess['_user_id'] = str(user.id)
                    sess['_fresh'] = True
                
                # Test dashboard access
                try:
                    response = client.get('/startup/dashboard')
                    print(f"   📊 Dashboard response: {response.status_code}")
                    
                    if response.status_code == 200:
                        print("   ✅ Dashboard loads successfully")
                        
                        # Check response content
                        html = response.data.decode()
                        if 'Welcome back' in html:
                            print("   ✅ Dashboard content looks correct")
                        else:
                            print("   ⚠️  Dashboard content might be incomplete")
                            
                    elif response.status_code == 302:
                        print(f"   🔄 Redirected to: {response.location}")
                        
                        # Follow redirect
                        response2 = client.get(response.location)
                        print(f"   📊 After redirect: {response2.status_code}")
                        
                    else:
                        print(f"   ❌ Unexpected status: {response.status_code}")
                        
                except Exception as e:
                    print(f"   ❌ Dashboard access error: {e}")
                    traceback.print_exc()
            
            # Test 4: Check startup data
            print("\n4️⃣ Checking startup data...")
            startup = Startup.query.filter_by(founder_id=user.id).first() if user else None
            if startup:
                print(f"   📊 Startup: {startup.name}")
                print(f"   📊 Status: {startup.application_status}")
                print(f"   📊 Created: {startup.created_at}")
            else:
                print("   ⚠️  No startup found for user")
            
            # Test 5: Check for common issues
            print("\n5️⃣ Checking for common issues...")
            
            # Check if CSS files exist
            css_files = [
                'static/css/startup.css',
                'static/css/global.css',
                'static/css/index.css'
            ]
            
            for css_file in css_files:
                if os.path.exists(css_file):
                    print(f"   ✅ {css_file} exists")
                else:
                    print(f"   ⚠️  {css_file} missing")
            
            # Check if JavaScript files exist
            js_files = [
                'static/js/startup.js',
                'static/js/main.js'
            ]
            
            for js_file in js_files:
                if os.path.exists(js_file):
                    print(f"   ✅ {js_file} exists")
                else:
                    print(f"   ⚠️  {js_file} missing (might be optional)")
            
            print("\n✅ Diagnosis complete!")

if __name__ == "__main__":
    diagnose_dashboard()