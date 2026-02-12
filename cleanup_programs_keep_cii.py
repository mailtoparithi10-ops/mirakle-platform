#!/usr/bin/env python3
"""
Remove all programs except CII (which has an image)
Keep only programs with proper images
"""

from extensions import db
from models import Opportunity
from app import create_app
import os

def cleanup_programs():
    app = create_app()
    with app.app_context():
        print("🔍 Checking all programs...")
        print("=" * 70)
        
        # Get all opportunities
        all_opps = Opportunity.query.all()
        print(f"Total programs found: {len(all_opps)}")
        
        # Programs to keep (with images in static/images/opportunities/)
        programs_with_images = []
        programs_to_delete = []
        
        # Check which programs have local images
        image_folder = "static/images/opportunities"
        if os.path.exists(image_folder):
            local_images = os.listdir(image_folder)
            print(f"\n📁 Local images found: {len(local_images)}")
            for img in local_images:
                print(f"   • {img}")
        else:
            local_images = []
            print("\n⚠️  No local images folder found")
        
        print("\n" + "=" * 70)
        print("PROGRAM ANALYSIS:")
        print("=" * 70)
        
        for opp in all_opps:
            has_local_image = False
            
            # Check if it's the CII program
            if "CII" in opp.title or "Disability" in opp.title or "Capacity Building" in opp.title:
                print(f"\n✅ KEEP: {opp.title}")
                print(f"   ID: {opp.id}")
                print(f"   Type: {opp.type}")
                print(f"   Reason: CII program with image")
                programs_with_images.append(opp)
                continue
            
            # Check if banner_url points to local image
            if opp.banner_url and "/static/images/opportunities/" in opp.banner_url:
                # Extract filename
                filename = opp.banner_url.split("/")[-1]
                if filename in local_images:
                    has_local_image = True
                    print(f"\n✅ KEEP: {opp.title}")
                    print(f"   ID: {opp.id}")
                    print(f"   Image: {filename}")
                    programs_with_images.append(opp)
                    continue
            
            # Mark for deletion
            print(f"\n❌ DELETE: {opp.title}")
            print(f"   ID: {opp.id}")
            print(f"   Reason: No local image")
            programs_to_delete.append(opp)
        
        # Summary
        print("\n" + "=" * 70)
        print("SUMMARY:")
        print("=" * 70)
        print(f"Programs to keep: {len(programs_with_images)}")
        print(f"Programs to delete: {len(programs_to_delete)}")
        
        # Confirm deletion
        if programs_to_delete:
            print("\n⚠️  About to delete the following programs:")
            for opp in programs_to_delete:
                print(f"   • {opp.title} (ID: {opp.id})")
            
            response = input("\nProceed with deletion? (yes/no): ")
            if response.lower() == 'yes':
                for opp in programs_to_delete:
                    db.session.delete(opp)
                db.session.commit()
                print(f"\n✅ Deleted {len(programs_to_delete)} programs")
            else:
                print("\n❌ Deletion cancelled")
        else:
            print("\n✅ No programs to delete")
        
        # Final count
        remaining = Opportunity.query.count()
        print(f"\n📊 Final program count: {remaining}")
        
        # List remaining programs
        print("\n" + "=" * 70)
        print("REMAINING PROGRAMS:")
        print("=" * 70)
        remaining_opps = Opportunity.query.all()
        for opp in remaining_opps:
            print(f"\n• {opp.title}")
            print(f"  ID: {opp.id}")
            print(f"  Type: {opp.type}")
            print(f"  Status: {opp.status}")
            print(f"  Image: {opp.banner_url}")

if __name__ == "__main__":
    cleanup_programs()
