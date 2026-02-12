#!/usr/bin/env python3
"""
Remove All Programs Without Images
Keep only CII and Natural Salon programs (which have images)
"""

from extensions import db
from models import Opportunity
from app import create_app

def remove_programs_without_images():
    app = create_app()
    with app.app_context():
        print("🔍 REMOVING PROGRAMS WITHOUT IMAGES")
        print("=" * 70)
        
        # Get all opportunities
        all_opps = Opportunity.query.all()
        print(f"Total programs in database: {len(all_opps)}")
        
        programs_to_keep = []
        programs_to_delete = []
        
        print("\n" + "=" * 70)
        print("ANALYZING PROGRAMS:")
        print("=" * 70)
        
        for opp in all_opps:
            # Check if program has an image URL
            has_image = bool(opp.banner_url)
            
            if has_image:
                print(f"\n✅ KEEP: {opp.title}")
                print(f"   ID: {opp.id}")
                print(f"   Type: {opp.type}")
                print(f"   Image: {opp.banner_url[:80]}...")
                programs_to_keep.append(opp)
            else:
                print(f"\n❌ DELETE: {opp.title}")
                print(f"   ID: {opp.id}")
                print(f"   Type: {opp.type}")
                print(f"   Reason: No image")
                programs_to_delete.append(opp)
        
        # Summary
        print("\n" + "=" * 70)
        print("SUMMARY:")
        print("=" * 70)
        print(f"Programs to keep: {len(programs_to_keep)}")
        print(f"Programs to delete: {len(programs_to_delete)}")
        
        if programs_to_delete:
            print("\n⚠️  About to DELETE the following programs:")
            for opp in programs_to_delete:
                print(f"   • {opp.title} (ID: {opp.id})")
            
            print("\n⚠️  This action CANNOT be undone!")
            response = input("\nProceed with deletion? (yes/no): ")
            
            if response.lower() == 'yes':
                deleted_count = 0
                for opp in programs_to_delete:
                    print(f"Deleting: {opp.title}")
                    db.session.delete(opp)
                    deleted_count += 1
                
                db.session.commit()
                print(f"\n✅ Successfully deleted {deleted_count} programs")
            else:
                print("\n❌ Deletion cancelled")
                return
        else:
            print("\n✅ No programs to delete - all programs have images!")
        
        # Final verification
        print("\n" + "=" * 70)
        print("FINAL DATABASE STATE:")
        print("=" * 70)
        
        remaining_opps = Opportunity.query.all()
        print(f"Total programs: {len(remaining_opps)}")
        
        print("\n📋 REMAINING PROGRAMS:")
        for opp in remaining_opps:
            print(f"\n• {opp.title}")
            print(f"  ID: {opp.id}")
            print(f"  Type: {opp.type}")
            print(f"  Status: {opp.status}")
            print(f"  Image: {opp.banner_url[:80] if opp.banner_url else 'None'}...")
        
        # Verify visibility
        print("\n" + "=" * 70)
        print("VISIBILITY VERIFICATION:")
        print("=" * 70)
        
        published_opps = Opportunity.query.filter_by(status="published").all()
        print(f"\nPublished programs: {len(published_opps)}")
        
        for opp in published_opps:
            print(f"\n✅ {opp.title}")
            print(f"   Will be visible in:")
            print(f"   • Startup Dashboard")
            print(f"   • Enabler Dashboard")
            print(f"   • Admin Dashboard")
            print(f"   • Opportunities Page")
        
        print("\n" + "=" * 70)
        print("✅ CLEANUP COMPLETE")
        print("=" * 70)
        print(f"\nOnly {len(remaining_opps)} programs remain (all with images)")
        print("These programs will be visible in all user dashboards")

if __name__ == "__main__":
    remove_programs_without_images()
