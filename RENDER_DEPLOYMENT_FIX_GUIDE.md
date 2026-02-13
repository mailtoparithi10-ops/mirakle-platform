# Render Deployment Fix - Login Issue

## Problem Summary

**Issue**: Login with `enabler@test.com` / `enabler123` works locally but not on Render.

**Root Cause**: Render uses ephemeral storage. The SQLite database (`instance/mirakle.db`) is recreated on every deployment, so test users don't persist.

## Solution: Add Database Seeding

### Step 1: Files Created ✅

The following files have been created to fix this issue:

1. **`seed_production.py`** - Seeds database with test users
2. **`reset_enabler_credentials.py`** - Resets local enabler credentials
3. **`check_enabler_password.py`** - Verifies password hash
4. **`RENDER_LOGIN_TROUBLESHOOTING.md`** - Detailed troubleshooting guide

### Step 2: Update Render Build Command

You need to update your Render service to run the seed script after building.

#### In Render Dashboard:

1. Go to your service
2. Click "Settings" or "Environment"
3. Find "Build Command"
4. Update it to:

```bash
pip install -r requirements.txt && python seed_production.py
```

This will:
- Install all dependencies
- Create database tables
- Seed test users automatically

### Step 3: Redeploy

After updating the build command:

1. Click "Manual Deploy" → "Deploy latest commit"
2. Wait for deployment to complete (3-5 minutes)
3. Check logs to verify seeding worked

Expected log output:
```
🌱 Starting database seeding...
✅ Database tables created/verified
✅ Created: enabler@test.com (enabler)
✅ Created: admin@test.com (admin)
✅ Created: startup@test.com (startup)
✅ Created: corporate@test.com (corporate)

✅ Seeding complete!
   Created: 4 users
   Existing: 0 users
   Total: 4 users

🔑 Test Credentials
============================================================

ENABLER:
  Email: enabler@test.com
  Password: enabler123

ADMIN:
  Email: admin@test.com
  Password: admin123

STARTUP:
  Email: startup@test.com
  Password: startup123

CORPORATE:
  Email: corporate@test.com
  Password: corporate123
```

### Step 4: Test Login

After deployment completes:

1. Visit: `https://your-app.onrender.com/enabler`
2. Enter credentials:
   - Email: `enabler@test.com`
   - Password: `enabler123`
3. Click "Login"
4. Should redirect to enabler dashboard

## Alternative: Use Render Shell (Quick Test)

If you want to test immediately without redeploying:

1. Go to Render Dashboard
2. Click on your service
3. Click "Shell" tab
4. Run:

```bash
python seed_production.py
```

This will seed the database immediately without redeploying.

## Local Testing ✅

Your local environment is now fixed:

```
✅ User: Test Enabler
✅ Email: enabler@test.com
✅ Password: enabler123
✅ Role: enabler
✅ Login: http://localhost:5001/enabler
```

## Test Credentials (All Roles)

After seeding, these credentials will work:

### Enabler
- URL: `/enabler`
- Email: `enabler@test.com`
- Password: `enabler123`

### Admin
- URL: `/admin`
- Email: `admin@test.com`
- Password: `admin123`

### Startup
- URL: `/startup`
- Email: `startup@test.com`
- Password: `startup123`

### Corporate
- URL: `/corporate`
- Email: `corporate@test.com`
- Password: `corporate123`

## Long-Term Solution: PostgreSQL

For production, you should migrate from SQLite to PostgreSQL:

### Why PostgreSQL?
- ✅ Persistent storage (data survives redeployments)
- ✅ Better performance for concurrent users
- ✅ Industry standard for web applications
- ✅ Free tier available on Render
- ✅ Automatic backups

### How to Migrate

1. **Create PostgreSQL Database in Render**
   - Dashboard → New + → PostgreSQL
   - Choose free tier
   - Note the connection URL

2. **Update `config.py`**
   ```python
   import os
   
   class Config:
       # Use PostgreSQL in production, SQLite locally
       if os.environ.get('DATABASE_URL'):
           SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL').replace(
               'postgres://', 'postgresql://'
           )
       else:
           SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/mirakle.db'
   ```

3. **Add to `requirements.txt`**
   ```
   psycopg2-binary==2.9.9
   ```

4. **Update Environment Variables in Render**
   - Add: `DATABASE_URL` (from PostgreSQL database)
   - Keep: `SECRET_KEY`, `FLASK_ENV=production`

5. **Redeploy**
   - Render will use PostgreSQL
   - Data will persist between deployments
   - Seed script will still work

## Troubleshooting

### If login still doesn't work:

1. **Check Render Logs**
   ```
   Dashboard → Logs tab
   Look for:
   - "Seeding complete" message
   - Any error messages
   - Database connection errors
   ```

2. **Verify Build Command**
   ```
   Settings → Build Command should be:
   pip install -r requirements.txt && python seed_production.py
   ```

3. **Check Environment Variables**
   ```
   Settings → Environment
   Required:
   - SECRET_KEY (any random string)
   - FLASK_ENV=production
   Optional:
   - DATABASE_URL (for PostgreSQL)
   ```

4. **Test in Render Shell**
   ```bash
   # Check if users exist
   python -c "from app import app, db; from models import User; app.app_context().push(); print(User.query.all())"
   
   # Manually seed if needed
   python seed_production.py
   ```

### If you see "User not found" error:

This means seeding didn't run. Solutions:
1. Update build command (see Step 2)
2. Run seed script in Render Shell
3. Check logs for seeding errors

### If you see "Invalid password" error:

This means user exists but password is wrong. Solutions:
1. Verify you're using `enabler123` (not `Enabler123` or other variation)
2. Re-run seed script to reset password
3. Check if password hashing is working correctly

## Summary

### What Was Fixed Locally ✅
- Reset enabler password to `enabler123`
- Verified password hash is valid
- Login works on `http://localhost:5001/enabler`

### What Needs to Be Done on Render ⚠️
1. Update build command to include `python seed_production.py`
2. Redeploy the application
3. Verify seeding in logs
4. Test login with `enabler@test.com` / `enabler123`

### Long-Term Recommendation 💡
- Migrate to PostgreSQL for persistent storage
- Remove dependency on seeding for every deployment
- Use proper database migrations

## Next Steps

1. **Immediate**: Update Render build command and redeploy
2. **Test**: Try login after deployment completes
3. **Monitor**: Check logs to ensure seeding works
4. **Plan**: Consider PostgreSQL migration for production

---

**Status**: Local fixed ✅, Render needs build command update ⚠️
**Files Created**: 4 new files for seeding and troubleshooting
**Action Required**: Update Render build command and redeploy
