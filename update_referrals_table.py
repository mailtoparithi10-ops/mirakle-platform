#!/usr/bin/env python3
"""
Update referrals table to add token and is_link_referral columns
"""
from app import create_app
from extensions import db

print("🔧 Updating referrals table...")
print("=" * 60)

app = create_app()

with app.app_context():
    try:
        # Check if columns exist
        result = db.session.execute(db.text("PRAGMA table_info(referrals)"))
        columns = [row[1] for row in result]
        
        print(f"Current columns: {columns}")
        
        # Add token column if it doesn't exist
        if 'token' not in columns:
            print("Adding 'token' column...")
            db.session.execute(db.text(
                "ALTER TABLE referrals ADD COLUMN token VARCHAR(100)"
            ))
            db.session.commit()
            print("✅ Added 'token' column")
        else:
            print("⏭️  'token' column already exists")
        
        # Add is_link_referral column if it doesn't exist
        if 'is_link_referral' not in columns:
            print("Adding 'is_link_referral' column...")
            db.session.execute(db.text(
                "ALTER TABLE referrals ADD COLUMN is_link_referral BOOLEAN DEFAULT 0"
            ))
            db.session.commit()
            print("✅ Added 'is_link_referral' column")
        else:
            print("⏭️  'is_link_referral' column already exists")
        
        # Verify the changes
        result = db.session.execute(db.text("PRAGMA table_info(referrals)"))
        columns = [row[1] for row in result]
        print(f"\nUpdated columns: {columns}")
        
        print("\n" + "=" * 60)
        print("✅ Referrals table updated successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error updating table: {e}")
        db.session.rollback()
        raise
