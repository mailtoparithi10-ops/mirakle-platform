#!/usr/bin/env python3
"""
Production Cleanup Script - Remove All Mock Data
Prepares the application for production launch by removing test/mock data
"""

import os
import sys
from pathlib import Path

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def print_step(num, text):
    print(f"\n[{num}] {text}")
    print("-" * 50)

def remove_mock_data_from_corporate_dashboard():
    """Remove mock data fallback from corporate dashboard"""
    print("Removing mock data from corporate_dashboard.html...")
    
    file_path = "templates/corporate_dashboard.html"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove the mock data fallback section
    mock_section = """                // Mock data for corporate display
                if (!apps || !Array.isArray(apps) || apps.length === 0) {
                    apps = [
                        {
                            id: 9991,
                            startup_name: "GreenGrid AI",
                            opportunity_title: "Sustainable Supply Chain POC",
                            created_at: new Date(Date.now() - 86400000 * 1).toISOString(),
                            status: "Under Review"
                        },
                        {
                            id: 9992,
                            startup_name: "QuantumLedger",
                            opportunity_title: "AI Logistics Pilot",
                            created_at: new Date(Date.now() - 86400000 * 3).toISOString(),
                            status: "Shortlisted"
                        },
                        {
                            id: 9993,
                            startup_name: "BioNano Sync",
                            opportunity_title: "Sustainable Supply Chain POC",
                            created_at: new Date(Date.now() - 86400000 * 7).toISOString(),
                            status: "Pending"
                        }
                    ];
                }"""
    
    if mock_section in content:
        content = content.replace(mock_section, "")
        print("✓ Removed mock application data")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Updated {file_path}")

def remove_mock_data_console_log():
    """Remove mock data console log from startup dashboard"""
    print("Removing mock data console log from startup_dashboard.html...")
    
    file_path = "templates/startup_dashboard.html"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the console log
    old_log = 'console.log("InnoBridge Dashboard Initialized with Mock Data");'
    new_log = 'console.log("InnoBridge Dashboard Initialized");'
    
    if old_log in content:
        content = content.replace(old_log, new_log)
        print("✓ Updated console log message")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Updated {file_path}")

def remove_seed_mock_button():
    """Remove 'Seed Mock Data' button from admin dashboard"""
    print("Removing 'Seed Mock Data' button from admin_dashboard.html...")
    
    file_path = "templates/admin_dashboard.html"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove the seed mock data button
    button_html = '''            <button class="admin-btn" onclick="seedMockData()" style="background: #000; color: #fcb82e; border: none;">
                <i class="fas fa-database"></i> Seed Mock Data
            </button>'''
    
    if button_html in content:
        content = content.replace(button_html, "")
        print("✓ Removed 'Seed Mock Data' button")
    
    # Also remove the seedMockData function
    # Find and remove the function
    import re
    pattern = r'async function seedMockData\(\).*?}\s*}'
    content = re.sub(pattern, '', content, flags=re.DOTALL)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✓ Updated {file_path}")

def remove_test_files():
    """Remove test upload files"""
    print("Removing test upload files...")
    
    test_files = [
        "static/uploads/startups/25_Test_Startup_Inc_logo_logo.png",
        "static/uploads/startups/25_Test_Startup_Inc_pitch_pitch.pdf",
        "static/uploads/startups/26_Program_Test_Startup_logo_logo.png",
        "static/uploads/startups/26_Program_Test_Startup_pitch_pitch.pdf",
        "static/uploads/startups/27_Detail_Test_Startup_logo_logo.png",
        "static/uploads/startups/27_Detail_Test_Startup_pitch_pitch.pdf",
    ]
    
    removed = 0
    for file_path in test_files:
        if os.path.exists(file_path):
            os.remove(file_path)
            removed += 1
            print(f"✓ Removed {file_path}")
    
    if removed == 0:
        print("No test files found (already clean)")
    else:
        print(f"✓ Removed {removed} test files")

def comment_out_seed_endpoint():
    """Comment out the seed mock data endpoint in admin routes"""
    print("Disabling seed mock data endpoint in routes/admin.py...")
    
    file_path = "routes/admin.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find and comment out the seed-all-data endpoint
    in_seed_function = False
    modified = False
    
    for i, line in enumerate(lines):
        if '@bp.route("/seed-all-data"' in line:
            in_seed_function = True
            modified = True
        
        if in_seed_function and not line.strip().startswith('#'):
            # Check if we've reached the next function
            if line.strip() and not line.strip().startswith('@') and i > 0:
                if lines[i-1].strip() == '' and line.startswith('@bp.route'):
                    in_seed_function = False
                    continue
            
            if line.strip():
                lines[i] = '# ' + line
    
    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        print(f"✓ Commented out seed endpoint in {file_path}")
    else:
        print("Seed endpoint not found or already disabled")

def main():
    print_header("PRODUCTION CLEANUP - REMOVE MOCK DATA")
    
    print("This script will:")
    print("  1. Remove mock data fallbacks from dashboards")
    print("  2. Remove 'Seed Mock Data' button from admin")
    print("  3. Remove test upload files")
    print("  4. Disable seed mock data endpoint")
    print("  5. Clean up console logs")
    
    response = input("\nProceed with cleanup? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Cleanup cancelled.")
        return
    
    try:
        print_step(1, "Removing Mock Data from Corporate Dashboard")
        remove_mock_data_from_corporate_dashboard()
        
        print_step(2, "Cleaning Console Logs")
        remove_mock_data_console_log()
        
        print_step(3, "Removing Admin Seed Button")
        remove_seed_mock_button()
        
        print_step(4, "Removing Test Upload Files")
        remove_test_files()
        
        print_step(5, "Disabling Seed Endpoint")
        comment_out_seed_endpoint()
        
        print_header("✓ CLEANUP COMPLETE")
        
        print("\nProduction Readiness Summary:")
        print("  ✓ Mock data fallbacks removed")
        print("  ✓ Test files cleaned up")
        print("  ✓ Seed endpoints disabled")
        print("  ✓ Console logs updated")
        
        print("\n" + "="*70)
        print("NEXT STEPS FOR PRODUCTION:")
        print("="*70)
        print("\n1. Review and test all dashboards")
        print("2. Ensure all API endpoints return real data")
        print("3. Set up production environment variables:")
        print("   - RAZORPAY_KEY_ID (live keys)")
        print("   - RAZORPAY_KEY_SECRET")
        print("   - GOOGLE_CLIENT_ID")
        print("   - SENTRY_DSN")
        print("   - MAIL_USERNAME & MAIL_PASSWORD")
        print("\n4. Run final tests:")
        print("   python -m pytest tests/")
        print("\n5. Deploy to production")
        
    except Exception as e:
        print(f"\n✗ Error during cleanup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
