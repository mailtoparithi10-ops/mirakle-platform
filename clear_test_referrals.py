"""
Clear test/fake referral data from the database
This will remove all existing referrals so new users see a clean dashboard
"""

from app import app
from models import Referral
from extensions import db

with app.app_context():
    # Get all referrals
    all_referrals = Referral.query.all()
    
    print(f"Found {len(all_referrals)} referrals in database")
    
    if len(all_referrals) > 0:
        print("\nReferrals to be deleted:")
        for ref in all_referrals:
            print(f"  - ID: {ref.id}, Startup: {ref.startup_name}, Program: {ref.opportunity_id}, Status: {ref.status}")
        
        # Ask for confirmation
        confirm = input(f"\nDelete all {len(all_referrals)} referrals? (yes/no): ")
        
        if confirm.lower() == 'yes':
            # Delete all referrals
            Referral.query.delete()
            db.session.commit()
            print(f"\n✓ Successfully deleted all {len(all_referrals)} referrals")
            print("✓ Database is now clean for production")
            print("\nNew users will now see:")
            print("  - Empty Recent Referral Activity table")
            print("  - 'No referrals yet' message")
            print("  - All counters at 0")
        else:
            print("\n✗ Deletion cancelled")
    else:
        print("\n✓ Database is already clean - no referrals found")
