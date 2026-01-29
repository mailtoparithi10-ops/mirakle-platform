#!/usr/bin/env python3
"""
Create referral_clicks table if it doesn't exist
"""
from app import create_app
from extensions import db

print("🔧 Creating referral_clicks table...")
print("=" * 60)

app = create_app()

with app.app_context():
    try:
        # Check if table exists
        result = db.session.execute(db.text(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='referral_clicks'"
        ))
        table_exists = result.fetchone() is not None
        
        if not table_exists:
            print("Creating 'referral_clicks' table...")
            db.session.execute(db.text("""
                CREATE TABLE referral_clicks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    referral_id INTEGER NOT NULL,
                    user_id INTEGER,
                    startup_id INTEGER,
                    ip_address VARCHAR(50),
                    user_agent VARCHAR(500),
                    clicked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    viewed_opportunity BOOLEAN DEFAULT 0,
                    applied BOOLEAN DEFAULT 0,
                    applied_at DATETIME,
                    FOREIGN KEY (referral_id) REFERENCES referrals(id),
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (startup_id) REFERENCES startups(id)
                )
            """))
            db.session.commit()
            print("✅ Created 'referral_clicks' table")
        else:
            print("⏭️  'referral_clicks' table already exists")
        
        # Verify the table
        result = db.session.execute(db.text("PRAGMA table_info(referral_clicks)"))
        columns = [row[1] for row in result]
        print(f"\nTable columns: {columns}")
        
        print("\n" + "=" * 60)
        print("✅ Referral clicks table ready!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        db.session.rollback()
        raise
