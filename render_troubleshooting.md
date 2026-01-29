# Render Deployment Troubleshooting Guide

## Common Issues and Solutions

### 1. **Database Not Populated**
**Problem:** Local database changes (new users, opportunities) don't exist on Render
**Solution:** Run the deployment script after build

### 2. **Static Files Not Loading**
**Problem:** Images or CSS not loading on Render
**Solution:** Ensure all static files are committed to git

### 3. **Environment Variables**
**Problem:** Missing or incorrect environment variables
**Solution:** Check Render dashboard environment variables

### 4. **Build Failures**
**Problem:** Build command fails during deployment
**Solution:** Check build logs in Render dashboard

## Deployment Steps

1. **Commit all changes to git**
   ```bash
   git add .
   git commit -m "fix: Render deployment updates"
   git push origin main
   ```

2. **Render will automatically redeploy**
   - Check build logs for errors
   - Verify environment variables are set
   - Check database connection

3. **Manual data setup (if needed)**
   - SSH into Render service (if available)
   - Run: `python deploy_to_render.py`

## Login Credentials for Testing

- **Admin:** admin@test.com / admin123
- **Startup:** startup@test.com / startup123  
- **Corporate:** corporate@test.com / corporate123
- **Connector:** connector@test.com / connector123

## Debugging Steps

1. Check Render build logs
2. Check Render runtime logs
3. Verify database connection
4. Test API endpoints manually
5. Check static file serving

## Files Updated for Render

- `render.yaml` - Updated build command
- `deploy_to_render.py` - Deployment script
- `static/images/opportunities/cii_capacity_building.jpg` - CII program image
- `templates/connector_dashboard.html` - Referral tracking section