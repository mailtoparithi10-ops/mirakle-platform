# Render Production - Enabler Login Fix Guide

## Issue
The enabler@test.com user credentials are not working on Render production environment.

## Root Cause
The production database may not have the enabler user, or the password hash may be incorrect.

## Solution Options

### Option 1: Run Script via Render Shell (Recommended)

1. **Access Render Shell**
   - Go to your Render dashboard
   - Select your web service
   - Click "Shell" tab
   - This opens a terminal in your production environment

2. **Run the Script**
   ```bash
   python create_enabler_production_v2.py
   ```

3. **Verify Output**
   - Look for "✅ ENABLER USER READY FOR PRODUCTION"
   - Note the credentials displayed

4. **Test Login**
   - Go to: `https://your-app.onrender.com/enabler/login`
   - Email: `enabler@test.com`
   - Password: `enabler123`

### Option 2: Update seed_production.py and Redeploy

1. **The seed_production.py has been updated** to:
   - Use `user.set_password()` method instead of direct password_hash
   - Update existing users' passwords if they already exist
   - Ensure all test users are active

2. **Commit and Push Changes**
   ```bash
   git add seed_production.py create_enabler_production_v2.py
   git commit -m "Fix: Update seed_production to use set_password method"
   git push origin main
   ```

3. **Run on Render**
   - After deployment, access Render Shell
   - Run: `python seed_production.py`

### Option 3: Manual Database Update via Render Shell

If scripts don't work, manually create the user:

```python
# In Render Shell, run: python
from app import create_app
from extensions import db
from models import User

app = create_app()
with app.app_context():
    user = User.query.filter_by(email='enabler@test.com').first()
    if not user:
        user = User(email='enabler@test.com', role='enabler', name='Test Enabler', is_active=True)
        db.session.add(user)
    user.set_password('enabler123')
    db.session.commit()
    print(f"✅ User ready: {user.email}")
```

## Files Modified

1. **create_enabler_production_v2.py** (NEW)
   - Improved version with better error handling
   - Works in both local and Render environments
   - Includes verification steps

2. **seed_production.py** (UPDATED)
   - Now uses `user.set_password()` method
   - Updates existing users' passwords
   - Ensures all users are active

3. **routes/referrals.py** (FIXED)
   - Changed `connector_id` to `enabler_id` (line 277)
   - Fixes AttributeError in production

4. **admin_search_service.py** (FIXED)
   - Changed all `connector_id` references to `enabler_id`
   - Ensures search functionality works

## Test Credentials (Production)

After running the fix:

```
ENABLER:
  Email: enabler@test.com
  Password: enabler123
  Login: /enabler/login

ADMIN:
  Email: admin@test.com
  Password: admin123
  Login: /admin/login

STARTUP:
  Email: startup@test.com
  Password: startup123
  Login: /startup/login

CORPORATE:
  Email: corporate@test.com
  Password: corporate123
  Login: /corporate/login
```

## Verification Steps

1. **Check User Exists**
   ```python
   from models import User
   user = User.query.filter_by(email='enabler@test.com').first()
   print(f"User: {user.email}, Role: {user.role}, Active: {user.is_active}")
   ```

2. **Test Password**
   ```python
   if user.check_password('enabler123'):
       print("✅ Password correct")
   else:
       print("❌ Password incorrect")
   ```

3. **Test Login**
   - Navigate to `/enabler/login`
   - Enter credentials
   - Should redirect to `/enabler/dashboard`

## Common Issues

### Issue: "User not found"
**Solution**: Run `create_enabler_production_v2.py` to create the user

### Issue: "Invalid password"
**Solution**: The password hash may be wrong. Run the script again to reset it.

### Issue: "AttributeError: 'Referral' object has no attribute 'connector_id'"
**Solution**: This has been fixed in routes/referrals.py. Push changes and redeploy.

### Issue: Script fails with import errors
**Solution**: Ensure you're running the script from the project root directory where app.py exists

## Next Steps

1. Commit all changes to git
2. Push to GitHub
3. Render will auto-deploy
4. Access Render Shell and run: `python create_enabler_production_v2.py`
5. Test login at production URL

## Support

If issues persist:
1. Check Render logs for errors
2. Verify database connection
3. Ensure all migrations have run
4. Check environment variables are set correctly
