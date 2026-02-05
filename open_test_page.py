#!/usr/bin/env python3
"""
Open the test page directly in browser
"""

import webbrowser
import time
import requests

def open_test_page():
    print("🚀 OPENING GOOGLE OAUTH TEST PAGES")
    print("=" * 40)
    
    # Check if server is running
    try:
        response = requests.get("http://localhost:5002", timeout=3)
        print("✅ Server is running")
    except:
        print("❌ Server is not running. Please run: python show_google_oauth.py")
        return
    
    print("\n📱 Opening test pages in your browser...")
    
    # Open the minimal test page first
    print("1. Opening minimal test page...")
    webbrowser.open("http://localhost:5002/test")
    time.sleep(2)
    
    # Open signup page
    print("2. Opening signup page...")
    webbrowser.open("http://localhost:5002/signup")
    time.sleep(2)
    
    # Open login page
    print("3. Opening login page...")
    webbrowser.open("http://localhost:5002/login")
    
    print("\n🎯 WHAT YOU SHOULD SEE:")
    print("=" * 40)
    print("📄 Test Page (http://localhost:5002/test):")
    print("   → Clean, simple page with a prominent Google button")
    print("   → Button should have Google logo and 'Continue with Google' text")
    print("   → Clicking it shows an alert")
    print()
    print("📄 Signup Page (http://localhost:5002/signup):")
    print("   → Google button at the top of the form")
    print("   → 'or' divider below the Google button")
    print("   → Regular signup form below")
    print()
    print("📄 Login Page (http://localhost:5002/login):")
    print("   → Google button at the top of the form")
    print("   → 'or' divider below the Google button")
    print("   → Regular login form below")
    print()
    print("🔍 IF YOU DON'T SEE THE BUTTONS:")
    print("   1. Check browser console (F12) for errors")
    print("   2. Try refreshing the page (Ctrl+F5)")
    print("   3. Try a different browser or incognito mode")
    print("   4. Check if any ad blockers are interfering")

if __name__ == "__main__":
    open_test_page()