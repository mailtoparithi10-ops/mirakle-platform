# Render Login Troubleshooting Guide

## Issue: Login Not Working on Render

### Root Cause: SQLite Ephemeral Storage

**Problem**: Render uses ephemeral storage, meaning:
- Files are reset on every deployment
- Database (`instance/mirakle.db`) is recreated fresh
- Test users don't persist between deploys
- Any data added is lost on redeploy

### Local vs Production

#### Local (Working) ✅
- Database: `instance/mirakle.db` (persistent)
- Test user exists: `enabler@test.com` / `enabler123`
- Password hash verified and working
- Login works perfectly

#### Render (Not Working) ❌
- Database: Recreated on every deploy
- Test users: Not present (unless seeded)
- Storage: Ephemeral (resets on redeploy)
- Login fails: User doesn't exist

## Solutions

### Solution 1: Create User After Deployment (Quick Fix)

You need to create the test user in Render's database after each deployment.

#### Option A: Using Render Shell
```bash
# Access Render shell from dashboard
# Then run:
python -c "
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

with app.app_context():
    # Check if user exists
    user = User.query.filter_by(email='enabler@test.com').first()
    
    if not user:
        # Create user
        user = User(
            email='enabler@test.com',
            password_hash=generate_password_hash('enabler123'),
            name='Test Enabler',
            role='enabler'
        )
        db.session.add(user)
        db.session.commit()
        print('✅ User created!')
    else:
        print('✅ User already exists!')
"
```

#### Option B: Create Seed Script
Add this to your deployment process:

**File: `seed_production.py`**
```python
"""Seed production database with essential data"""
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

def seed_users():
    """Create essential test users"""
    with app.app_context():
        users = [
            {
                'email': 'enabler@test.com',
                'password': 'enabler123',
                'name': 'Test Enabler',
                'role': 'enabler'
            },
            {
                'email': 'admin@test.com',
                'password': 'admin123',
                'name': 'Test Admin',
                'role': 'admin'
            },
            {
                'email': 'startup@test.com',
                'password': 'startup123',
                'name': 'Test Startup',
                'role': 'startup'
            }
        ]
        
        for user_data in users:
            existing = User.query.filter_by(email=user_data['email']).first()
            
            if not existing:
                user = User(
                    email=user_data['email'],
                    password_hash=generate_password_hash(user_data['password']),
                    name=user_data['name'],
                    role=user_data['role']
                )
                db.session.add(user)
                print(f"✅ Created: {user_data['email']}")
            else:
                print(f"⏭️  Exists: {user_data['email']}")
        
        db.session.commit()
        print("\n✅ Seeding complete!")

if __name__ == '__main__':
    seed_users()
```

**Update Render Build Command**:
```bash
# In Render dashboard, set build command to:
pip install -r requirements.txt && python seed_production.py
```

### Solution 2: Migrate to PostgreSQL (Recommended)

SQLite is not suitable for production. Migrate to PostgreSQL for persistent storage.

#### Step 1: Create PostgreSQL Database in Render
1. Go to Render Dashboard
2. Click "New +" → "PostgreSQL"
3. Choose free tier or paid tier
4. Note the connection details

#### Step 2: Update Application
```python
# config.py
import os

class Config:
    # Use PostgreSQL in production, SQLite in development
    if os.environ.get('DATABASE_URL'):
        # Render provides DATABASE_URL
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL').replace(
            'postgres://', 'postgresql://'
        )
    else:
        # Local development
        SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/mirakle.db'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
```

#### Step 3: Update requirements.txt
```txt
# Add PostgreSQL adapter
psycopg2-binary==2.9.9
```

#### Step 4: Create Migration Script
```python
# migrate_to_postgres.py
"""Migrate data from SQLite to PostgreSQL"""
import sqlite3
import psycopg2
from urllib.parse import urlparse

def migrate():
    # Connect to SQLite
    sqlite_conn = sqlite3.connect('instance/mirakle.db')
    sqlite_cursor = sqlite_conn.cursor()
    
    # Connect to PostgreSQL
    postgres_url = os.environ.get('DATABASE_URL')
    postgres_conn = psycopg2.connect(postgres_url)
    postgres_cursor = postgres_conn.cursor()
    
    # Migrate users
    sqlite_cursor.execute('SELECT * FROM users')
    users = sqlite_cursor.fetchall()
    
    for user in users:
        postgres_cursor.execute("""
            INSERT INTO users (id, name, email, password_hash, role, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (email) DO NOTHING
        """, user[:6])
    
    postgres_conn.commit()
    print(f"✅ Migrated {len(users)} users")
    
    # Migrate other tables...
    
    sqlite_conn.close()
    postgres_conn.close()

if __name__ == '__main__':
    migrate()
```

#### Step 5: Update Render Environment Variables
```
DATABASE_URL=<your_postgres_url>
SECRET_KEY=<your_secret_key>
FLASK_ENV=production
```

### Solution 3: Use Render Disk (Persistent Storage)

Render offers persistent disk storage (paid feature).

#### Step 1: Add Persistent Disk
1. Go to your service in Render
2. Navigate to "Disks" tab
3. Click "Add Disk"
4. Mount path: `/data`
5. Size: 1GB (minimum)

#### Step 2: Update Database Path
```python
# config.py
import os

class Config:
    # Use persistent disk in production
    if os.environ.get('RENDER'):
        SQLALCHEMY_DATABASE_URI = 'sqlite:////data/mirakle.db'
    else:
        SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/mirakle.db'
```

#### Step 3: Set Environment Variable
```
RENDER=true
```

## Testing After Fix

### Test Locally First
```bash
# Reset credentials
python reset_enabler_credentials.py

# Start server
python app.py

# Test login
# Visit: http://localhost:5001/enabler
# Email: enabler@test.com
# Password: enabler123
```

### Test on Render
```bash
# After applying one of the solutions above:

# 1. Visit your Render URL
https://your-app.onrender.com/enabler

# 2. Try login
Email: enabler@test.com
Password: enabler123

# 3. Check Render logs if it fails
# Dashboard → Logs tab
```

## Verification Checklist

### Local Environment ✅
- [x] User exists in database
- [x] Password hash is valid
- [x] Login works on localhost:5001
- [x] Credentials: enabler@test.com / enabler123

### Render Environment ⚠️
- [ ] Database is persistent (PostgreSQL or Disk)
- [ ] Test users are seeded after deployment
- [ ] Environment variables are set
- [ ] Login works on production URL

## Recommended Approach

**For Testing/Development**:
- Use Solution 1 (Seed Script)
- Quick to implement
- Good for testing

**For Production**:
- Use Solution 2 (PostgreSQL)
- Industry standard
- Scalable and reliable
- Free tier available on Render

## Current Status

### Local Database ✅
```
User: Test Enabler
Email: enabler@test.com
Password: enabler123
Role: enabler
Status: Working
```

### Render Database ❌
```
Status: Empty (ephemeral storage)
Issue: Users not persisting
Solution: Implement one of the solutions above
```

## Next Steps

1. **Immediate**: Create seed script and update build command
2. **Short-term**: Test login on Render after seeding
3. **Long-term**: Migrate to PostgreSQL for production

## Support Commands

### Check if user exists in Render
```bash
# In Render shell:
python -c "from app import app, db; from models import User; app.app_context().push(); print(User.query.filter_by(email='enabler@test.com').first())"
```

### Create user in Render
```bash
# In Render shell:
python seed_production.py
```

### Check database type
```bash
# In Render shell:
python -c "from app import app; print(app.config['SQLALCHEMY_DATABASE_URI'])"
```

## Summary

The login works locally but not on Render because:
1. Render uses ephemeral storage
2. Database is recreated on each deploy
3. Test users don't persist

**Solution**: Implement seeding script or migrate to PostgreSQL.

---

**Status**: Issue identified and solutions provided
**Local**: ✅ Working (enabler@test.com / enabler123)
**Render**: ⚠️ Needs implementation of one of the solutions above
