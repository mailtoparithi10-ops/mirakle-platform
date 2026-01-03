#!/usr/bin/env python3
"""
Simple setup script for InnoBridge
"""

import subprocess
import sys
import os

def install_packages():
    """Install required packages"""
    packages = ['Flask', 'Flask-CORS', 'Werkzeug']
    
    print("Installing packages...")
    try:
        subprocess.check_call([
            sys.executable, '-m', 'pip', 'install'
        ] + packages)
        print("✅ Packages installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install packages")
        return False
    return True

def run_server():
    """Run the Flask server"""
    print("🚀 Starting InnoBridge server...")
    print("📋 Open http://127.0.0.1:5000 in your browser")
    print("⚠️  Press Ctrl+C to stop")
    
    try:
        from app import app, init_db
        init_db()
        app.run(debug=True, host='0.0.0.0', port=5000)
    except ImportError:
        print("❌ app.py not found")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    if not install_packages():
        sys.exit(1)
    
    if not os.path.exists('app.py'):
        print("❌ app.py file not found")
        sys.exit(1)
    
    run_server()
    