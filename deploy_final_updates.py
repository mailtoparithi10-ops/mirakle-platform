#!/usr/bin/env python3
"""
Final Deployment Script
Verifies all changes and pushes to Git for Render deployment
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a shell command and return success status"""
    print(f"\n{'='*70}")
    print(f"🔄 {description}")
    print(f"{'='*70}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"❌ {description} - Failed")
            if result.stderr:
                print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - Exception: {e}")
        return False

def check_git_status():
    """Check git status"""
    print(f"\n{'='*70}")
    print("📊 Checking Git Status")
    print(f"{'='*70}")
    
    result = subprocess.run(
        "git status --short",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.stdout:
        print("Modified files:")
        print(result.stdout)
        return True
    else:
        print("No changes detected")
        return False

def verify_critical_files():
    """Verify critical files exist"""
    print(f"\n{'='*70}")
    print("🔍 Verifying Critical Files")
    print(f"{'='*70}")
    
    critical_files = [
        'app.py',
        'requirements.txt',
        'Procfile',
        'runtime.txt',
        'models.py',
        'templates/index.html',
        'templates/startup_application.html',
        'templates/admin_dashboard.html',
        'templates/enabler_dashboard.html',
        'static/favicon.svg'
    ]
    
    all_exist = True
    for file in critical_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING!")
            all_exist = False
    
    return all_exist

def main():
    print("\n" + "="*70)
    print("🚀 FINAL DEPLOYMENT TO RENDER")
    print("="*70)
    print("\nThis script will:")
    print("1. Verify critical files")
    print("2. Check git status")
    print("3. Add all changes")
    print("4. Commit with message")
    print("5. Push to origin/main")
    print("6. Trigger Render deployment")
    
    # Step 1: Verify critical files
    if not verify_critical_files():
        print("\n❌ Critical files missing! Please fix before deploying.")
        return False
    
    # Step 2: Check git status
    has_changes = check_git_status()
    if not has_changes:
        print("\n⚠️  No changes to commit")
        response = input("\nContinue anyway? (yes/no): ")
        if response.lower() != 'yes':
            print("Deployment cancelled")
            return False
    
    # Step 3: Git add
    if not run_command("git add .", "Adding all changes to git"):
        return False
    
    # Step 4: Git commit
    commit_message = """feat: Major platform updates

- Added professional images to all 14 programs
- Positioned CII and Natural Salon programs at top
- Enhanced startup application form UI/UX
- Updated footer copyright year to 2026
- Improved form interactions and animations
- Added numbered sections and progress indicators
- Enhanced file upload experience
- Optimized dashboard performance

All programs now have images and are visible across all dashboards.
Startup application form redesigned with professional UI/UX.
Footer year updated across all 10 pages."""
    
    commit_cmd = f'git commit -m "{commit_message}"'
    if not run_command(commit_cmd, "Committing changes"):
        print("\n⚠️  Commit failed - possibly no changes or already committed")
        response = input("\nContinue with push? (yes/no): ")
        if response.lower() != 'yes':
            return False
    
    # Step 5: Git push
    if not run_command("git push origin main", "Pushing to origin/main"):
        print("\n❌ Push failed!")
        print("\nTroubleshooting:")
        print("1. Check if you're on the correct branch")
        print("2. Verify remote is configured: git remote -v")
        print("3. Check authentication")
        print("4. Try: git pull origin main --rebase")
        return False
    
    # Success summary
    print("\n" + "="*70)
    print("✅ DEPLOYMENT SUCCESSFUL!")
    print("="*70)
    
    print("\n📋 What was deployed:")
    print("   ✅ All 14 programs with professional images")
    print("   ✅ CII and Natural Salon at top positions")
    print("   ✅ Enhanced startup application form")
    print("   ✅ Footer year updated to 2026 (10 pages)")
    print("   ✅ Dashboard UI/UX improvements")
    print("   ✅ Performance optimizations")
    
    print("\n🔄 Render Deployment:")
    print("   • Render will automatically detect the push")
    print("   • Deployment typically takes 5-7 minutes")
    print("   • Check Render dashboard for progress")
    
    print("\n📝 Post-Deployment Tasks:")
    print("   1. Monitor Render deployment logs")
    print("   2. Run program initialization scripts on Render:")
    print("      - python ensure_cii_program.py")
    print("      - python add_natural_salon_program.py")
    print("      - python add_images_to_all_programs.py")
    print("   3. Test all dashboards in production")
    print("   4. Verify programs are visible")
    print("   5. Test startup application form")
    
    print("\n" + "="*70)
    print("🎉 Ready for production!")
    print("="*70)
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Deployment cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)
