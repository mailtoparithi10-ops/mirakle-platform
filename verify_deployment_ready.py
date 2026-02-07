#!/usr/bin/env python3
"""
Final verification script to ensure the project is ready for Render deployment
"""

import os
import sys
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a required file exists"""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} - MISSING!")
        return False

def check_file_content(filepath, required_content, description):
    """Check if file contains required content"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            if required_content in content:
                print(f"✅ {description}")
                return True
            else:
                print(f"❌ {description} - Content missing!")
                return False
    except Exception as e:
        print(f"❌ {description} - Error reading file: {e}")
        return False

def verify_deployment_ready():
    """Main verification function"""
    print("RENDER DEPLOYMENT VERIFICATION")
    print("=" * 50)
    
    all_checks_passed = True
    
    # Check required files
    print("\nREQUIRED FILES:")
    required_files = [
        ("requirements.txt", "Python dependencies"),
        ("Procfile", "Process configuration"),
        ("render.yaml", "Render configuration"),
        ("runtime.txt", "Python version"),
        ("wsgi.py", "WSGI entry point"),
        (".gitignore", "Git ignore rules"),
        ("app.py", "Main Flask application"),
        ("models.py", "Database models"),
        ("init_database.py", "Database initialization"),
        ("deploy_to_render.py", "Production data seeding")
    ]
    
    for filepath, description in required_files:
        if not check_file_exists(filepath, description):
            all_checks_passed = False
    
    # Check critical content
    print("\nCONFIGURATION CONTENT:")
    content_checks = [
        ("requirements.txt", "Flask==", "Flask dependency"),
        ("requirements.txt", "gunicorn", "Gunicorn server"),
        ("requirements.txt", "psycopg2-binary", "PostgreSQL adapter"),
        ("Procfile", "gunicorn", "Gunicorn process"),
        ("render.yaml", "buildCommand", "Build command"),
        ("render.yaml", "startCommand", "Start command"),
        ("runtime.txt", "python-3.12", "Python version"),
        ("wsgi.py", "from app import create_app", "WSGI import")
    ]
    
    for filepath, content, description in content_checks:
        if not check_file_content(filepath, content, description):
            all_checks_passed = False
    
    # Check static files
    print("\nSTATIC FILES:")
    static_files = [
        ("static/css/index.css", "Main stylesheet"),
        ("static/css/globe-3d.css", "Globe 3D styles"),
        ("static/js/globe-3d.js", "Globe 3D functionality"),
        ("static/js/referral-links.js", "Referral system"),
        ("static/css/floating-elements.css", "Floating animations")
    ]
    
    for filepath, description in static_files:
        if not check_file_exists(filepath, description):
            all_checks_passed = False
    
    # Check templates
    print("\nTEMPLATES:")
    template_files = [
        ("templates/index.html", "Homepage"),
        ("templates/about.html", "About page"),
        ("templates/products.html", "Products page"),
        ("templates/corporate.html", "Corporate page"),
        ("templates/opportunities.html", "Opportunities page"),
        ("templates/login.html", "Login page"),
        ("templates/signup.html", "Signup page")
    ]
    
    for filepath, description in template_files:
        if not check_file_exists(filepath, description):
            all_checks_passed = False
    
    # Check routes
    print("\nROUTES:")
    route_files = [
        ("routes/admin.py", "Admin routes"),
        ("routes/meetings.py", "Meeting routes"),
        ("routes/referrals.py", "Referral routes"),
        ("routes/webrtc.py", "WebRTC routes")
    ]
    
    for filepath, description in route_files:
        if not check_file_exists(filepath, description):
            all_checks_passed = False
    
    # Final summary
    print("\n" + "=" * 50)
    if all_checks_passed:
        print("ALL CHECKS PASSED! Project is ready for Render deployment.")
        print("\nNext Steps:")
        print("1. Go to https://dashboard.render.com")
        print("2. Create new Web Service")
        print("3. Connect GitHub repository: mailtoparithi10-ops/mirakle-platform")
        print("4. Use render.yaml for automatic configuration")
        print("5. Create PostgreSQL database and link it")
        print("6. Deploy and monitor logs")
        return True
    else:
        print("SOME CHECKS FAILED! Please fix the issues above before deploying.")
        return False

if __name__ == "__main__":
    success = verify_deployment_ready()
    sys.exit(0 if success else 1)