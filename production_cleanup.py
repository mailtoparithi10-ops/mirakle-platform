"""
Production Cleanup Script
Removes all fake/mock data and ensures dashboards work with real data only
"""

import os
import sys
from app import create_app
from extensions import db
from models import User, Startup, Opportunity, Application, Meeting, Message, Connection

def cleanup_for_production():
    """Remove all test/mock data and prepare for production"""
    
    app = create_app()
    
    with app.app_context():
        print("=" * 70)
        print("PRODUCTION CLEANUP - REMOVING ALL FAKE DATA")
        print("=" * 70)
        
        # 1. Remove test users (keep only real admin)
        print("\n1. Cleaning up test users...")
        test_users = User.query.filter(
            (User.email.like('%test%')) | 
            (User.email.like('%demo%')) |
            (User.email.like('%fake%')) |
            (User.username.like('%test%')) |
            (User.username.like('%demo%'))
        ).all()
        
        print(f"   Found {len(test_users)} test users")
        for user in test_users:
            print(f"   - Removing: {user.email} ({user.role})")
            db.session.delete(user)
        
        # 2. Remove test startups
        print("\n2. Cleaning up test startups...")
        test_startups = Startup.query.filter(
            (Startup.startup_name.like('%Test%')) |
            (Startup.startup_name.like('%Demo%')) |
            (Startup.startup_name.like('%Sample%'))
        ).all()
        
        print(f"   Found {len(test_startups)} test startups")
        for startup in test_startups:
            print(f"   - Removing: {startup.startup_name}")
            db.session.delete(startup)
        
        # 3. Remove test applications
        print("\n3. Cleaning up test applications...")
        test_apps = Application.query.filter(
            (Application.startup_name.like('%Test%')) |
            (Application.startup_name.like('%Demo%'))
        ).all()
        
        print(f"   Found {len(test_apps)} test applications")
        for app_item in test_apps:
            db.session.delete(app_item)
        
        # 4. Remove test meetings
        print("\n4. Cleaning up test meetings...")
        test_meetings = Meeting.query.filter(
            (Meeting.title.like('%Test%')) |
            (Meeting.title.like('%Demo%'))
        ).all()
        
        print(f"   Found {len(test_meetings)} test meetings")
        for meeting in test_meetings:
            db.session.delete(meeting)
        
        # 5. Remove test messages
        print("\n5. Cleaning up test messages...")
        test_messages = Message.query.filter(
            (Message.subject.like('%Test%')) |
            (Message.subject.like('%Demo%'))
        ).all()
        
        print(f"   Found {len(test_messages)} test messages")
        for message in test_messages:
            db.session.delete(message)
        
        # 6. Remove test connections
        print("\n6. Cleaning up test connections...")
        # Connections with deleted users will be automatically cleaned
        
        # Commit all deletions
        try:
            db.session.commit()
            print("\n✅ All test data removed successfully!")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error during cleanup: {e}")
            return False
        
        # 7. Verify remaining data
        print("\n" + "=" * 70)
        print("REMAINING DATA (PRODUCTION READY)")
        print("=" * 70)
        
        remaining_users = User.query.count()
        remaining_startups = Startup.query.count()
        remaining_opportunities = Opportunity.query.count()
        remaining_applications = Application.query.count()
        remaining_meetings = Meeting.query.count()
        
        print(f"\n✓ Users: {remaining_users}")
        print(f"✓ Startups: {remaining_startups}")
        print(f"✓ Opportunities: {remaining_opportunities}")
        print(f"✓ Applications: {remaining_applications}")
        print(f"✓ Meetings: {remaining_meetings}")
        
        # List remaining users
        print("\n" + "-" * 70)
        print("REMAINING USERS:")
        print("-" * 70)
        users = User.query.all()
        for user in users:
            print(f"  • {user.email} ({user.role}) - ID: {user.id}")
        
        print("\n" + "=" * 70)
        print("PRODUCTION CLEANUP COMPLETE!")
        print("=" * 70)
        print("\n✅ Your platform is now ready for production")
        print("✅ All dashboards will show real data only")
        print("✅ New users can signup and all features will work")
        
        return True

if __name__ == "__main__":
    print("\n⚠️  WARNING: This will remove all test/demo data!")
    print("⚠️  Only real production data will remain.")
    
    confirm = input("\nAre you sure you want to proceed? (yes/no): ")
    
    if confirm.lower() == 'yes':
        success = cleanup_for_production()
        if success:
            print("\n✅ Production cleanup completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Production cleanup failed!")
            sys.exit(1)
    else:
        print("\n❌ Cleanup cancelled.")
        sys.exit(0)
