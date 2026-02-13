"""
Deploy Latest Changes to GitHub
This script commits and pushes all recent changes including:
- Program details section restoration
- Profile & Settings form validation
- Referral link functionality
"""

import subprocess
import sys

def run_command(command, description):
    """Run a git command and handle errors"""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.stdout:
            print(result.stdout)
        
        if result.returncode != 0:
            if result.stderr:
                print(f"⚠️ Warning: {result.stderr}")
            # Don't fail on warnings, continue
            return False
        
        print(f"✅ {description} - Success")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("🚀 DEPLOYING TO GITHUB")
    print("="*60)
    
    # Step 1: Check git status
    print("\n📊 Checking current git status...")
    run_command("git status", "Git Status Check")
    
    # Step 2: Add all changes
    if not run_command("git add .", "Adding all changes to staging"):
        print("⚠️ Some files may not have been added, continuing...")
    
    # Step 3: Check what will be committed
    print("\n📋 Files to be committed:")
    run_command("git status --short", "Staged Files")
    
    # Step 4: Create commit message
    commit_message = """feat: Add profile validation and program details

- Added HTML5 form validation to Profile & Settings
- Required fields: name (2-100 chars), phone (10-15 digits)
- Password validation: min 8 chars, uppercase, lowercase, number
- Restored program details section with referral links
- Added copy, WhatsApp, and Email sharing for referral links
- Enhanced JavaScript validation with form.checkValidity()
- Added placeholder text and helper messages
- Improved UX with red asterisk on required fields
- Form reset after successful password change
- Input trimming and custom error messages

Frontend changes only - backend APIs still needed for full functionality
"""
    
    # Step 5: Commit changes
    commit_cmd = f'git commit -m "{commit_message}"'
    if not run_command(commit_cmd, "Committing changes"):
        print("⚠️ Commit may have failed or no changes to commit")
        print("Checking if there are uncommitted changes...")
        run_command("git status", "Final Status Check")
        return
    
    # Step 6: Push to GitHub
    print("\n🌐 Pushing to GitHub...")
    print("Note: You may need to enter your GitHub credentials")
    
    if not run_command("git push origin main", "Pushing to main branch"):
        print("\n⚠️ Push to 'main' failed, trying 'master' branch...")
        if not run_command("git push origin master", "Pushing to master branch"):
            print("\n❌ Push failed. Please check:")
            print("1. Your GitHub credentials")
            print("2. Your internet connection")
            print("3. The remote repository URL")
            print("\nYou can manually push with: git push origin main")
            return
    
    print("\n" + "="*60)
    print("✅ DEPLOYMENT COMPLETE!")
    print("="*60)
    print("\n📦 Changes pushed to GitHub successfully")
    print("\n🔗 Next steps:")
    print("1. Check your GitHub repository to verify changes")
    print("2. Render will auto-deploy if connected to GitHub")
    print("3. Monitor Render deployment logs")
    print("4. Test on production after deployment completes")
    
    print("\n📝 Deployment Summary:")
    print("- Profile & Settings form validation added")
    print("- Program details section restored")
    print("- Referral link sharing functionality added")
    print("- All changes committed and pushed to GitHub")

if __name__ == "__main__":
    main()
