# Quick Fix: Render Login Issue

## Problem
Login works locally but not on Render with `enabler@test.com` / `enabler123`

## Root Cause
Render uses ephemeral storage → database resets on every deploy → users don't persist

## Quick Fix (5 minutes)

### Option 1: Update Build Command (Recommended)

1. Go to Render Dashboard
2. Select your service
3. Go to "Settings"
4. Find "Build Command"
5. Change to:
   ```bash
   pip install -r requirements.txt && python seed_production.py
   ```
6. Click "Save Changes"
7. Click "Manual Deploy" → "Deploy latest commit"
8. Wait 3-5 minutes
9. Test login at: `https://your-app.onrender.com/enabler`

### Option 2: Use Render Shell (Immediate)

1. Go to Render Dashboard
2. Select your service
3. Click "Shell" tab
4. Run:
   ```bash
   python seed_production.py
   ```
5. Test login immediately

## Test Credentials

After seeding:

```
Enabler:
  Email: enabler@test.com
  Password: enabler123
  URL: /enabler

Admin:
  Email: admin@test.com
  Password: admin123
  URL: /admin

Startup:
  Email: startup@test.com
  Password: startup123
  URL: /startup

Corporate:
  Email: corporate@test.com
  Password: corporate123
  URL: /corporate
```

## Verify Success

Look for this in Render logs:
```
✅ Seeding complete!
   Created: 4 users
```

## Local Status ✅

Your local environment is fixed:
- Email: `enabler@test.com`
- Password: `enabler123`
- URL: `http://localhost:5001/enabler`
- Status: Working

## Files Created

1. `seed_production.py` - Seeds database with test users
2. `reset_enabler_credentials.py` - Resets local credentials
3. `check_enabler_password.py` - Verifies password
4. `RENDER_LOGIN_TROUBLESHOOTING.md` - Full guide
5. `RENDER_DEPLOYMENT_FIX_GUIDE.md` - Detailed steps

## Long-Term Solution

Migrate to PostgreSQL for persistent storage:
- Free tier available on Render
- Data persists between deployments
- Better for production

See `RENDER_DEPLOYMENT_FIX_GUIDE.md` for PostgreSQL migration steps.

---

**TL;DR**: Update Render build command to include `python seed_production.py`, then redeploy.
