"""
Open Admin Dashboard in Browser
This will open the admin dashboard so you can test it manually
"""

import webbrowser
import time

print("=" * 70)
print("OPENING ADMIN DASHBOARD")
print("=" * 70)

print("\n📋 TESTING CHECKLIST:")
print("\n1. BEFORE OPENING:")
print("   - Make sure server is running (python app.py)")
print("   - Have admin credentials ready")
print("   - Prepare to do a HARD REFRESH")

print("\n2. WHEN PAGE OPENS:")
print("   - Login with admin credentials")
print("   - Press Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)")
print("   - This will force browser to reload CSS and JS")

print("\n3. WHAT TO CHECK:")
print("   ✓ Dashboard section visible immediately")
print("   ✓ Stats cards showing")
print("   ✓ Navigation buttons work")
print("   ✓ Smooth transitions when clicking nav")
print("   ✓ No blank/invisible sections")

print("\n4. IF STILL NOT WORKING:")
print("   - Open browser console (F12)")
print("   - Check for JavaScript errors")
print("   - Look for CSS loading errors")
print("   - Try incognito/private mode")

print("\n5. BROWSER CACHE CLEARING:")
print("   Chrome: Ctrl+Shift+Delete → Clear browsing data")
print("   Firefox: Ctrl+Shift+Delete → Clear recent history")
print("   Edge: Ctrl+Shift+Delete → Clear browsing data")

print("\n" + "=" * 70)
print("Opening admin login in 3 seconds...")
print("=" * 70)

time.sleep(3)

# Open admin login page
url = "http://localhost:5001/admin/login"
webbrowser.open(url)

print("\n✅ Browser opened!")
print("\nREMEMBER:")
print("1. Login as admin")
print("2. HARD REFRESH: Ctrl+Shift+R or Cmd+Shift+R")
print("3. Check if dashboard displays correctly")
print("\nIf you see issues, check browser console (F12) for errors")
print("=" * 70)
