# Render Deployment Guide for InnoBridge Platform

## ✅ Pre-Deployment Checklist

All necessary files are in place:
- ✅ `Procfile` - Gunicorn configuration with WebSocket support
- ✅ `requirements.txt` - All Python dependencies including gevent
- ✅ `runtime.txt` - Python 3.11.9
- ✅ `render.yaml` - Render service configuration
- ✅ `wsgi.py` - WSGI entry point
- ✅ `init_database.py` - Database initialization script

## 🚀 Deployment Steps

### Step 1: Create a New Web Service on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository: `mailtoparithi10-ops/mirakle-platform`
4. Configure the service:

### Step 2: Service Configuration

**Basic Settings:**
- **Name:** `mirakle-platform` (or your preferred name)
- **Region:** Choose closest to your users
- **Branch:** `main`
- **Root Directory:** Leave blank
- **Runtime:** `Python 3`

**Build & Deploy:**
- **Build Command:** 
  ```bash
  pip install -r requirements.txt && python init_database.py
  ```
- **Start Command:**
  ```bash
  gunicorn --worker-class geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 --bind 0.0.0.0:$PORT wsgi:app
  ```

### Step 3: Environment Variables

Add these environment variables in Render dashboard:

| Key | Value | Notes |
|-----|-------|-------|
| `SECRET_KEY` | Auto-generate | Click "Generate" button |
| `DATABASE_URL` | From PostgreSQL | Link to your database |
| `FLASK_ENV` | `production` | Production mode |
| `SOCKETIO_ASYNC_MODE` | `gevent` | For WebSocket support |
| `PYTHON_VERSION` | `3.11.9` | Python runtime |

### Step 4: Create PostgreSQL Database

1. In Render Dashboard, click **"New +"** → **"PostgreSQL"**
2. Configure:
   - **Name:** `mirakle-db`
   - **Database:** `mirakle`
   - **User:** `mirakle`
   - **Region:** Same as web service
   - **Plan:** Free or Starter

3. After creation, copy the **Internal Database URL**
4. Add it to your web service as `DATABASE_URL` environment variable

### Step 5: Deploy

1. Click **"Create Web Service"**
2. Render will automatically:
   - Clone your repository
   - Install dependencies
   - Initialize the database
   - Start the application

3. Monitor the deployment logs for any errors

### Step 6: Post-Deployment Setup

Once deployed, you'll need to create test users. You can do this by:

1. **Option A:** Use Render Shell
   ```bash
   python create_test_users.py
   ```

2. **Option B:** Access the signup page and create users manually

## 🔧 Important Configuration Notes

### WebSocket Support
The application uses Flask-SocketIO with gevent for real-time features:
- Meeting system
- Live notifications
- Real-time updates

### Database Migrations
If you need to run migrations:
```bash
flask db upgrade
```

### Static Files
Static files are served directly by Flask. For production, consider using a CDN.

## 📝 Test User Credentials

After running `create_test_users.py`, you'll have:

- **Admin:** `admin@test.com` / `admin123`
- **Connector:** `connector@test.com` / `connector123`
- **Corporate:** `corporate@test.com` / `corporate123`
- **Startup:** `startup@test.com` / `startup123`

## 🐛 Troubleshooting

### Build Fails
- Check Python version matches `runtime.txt`
- Verify all dependencies in `requirements.txt`
- Check build logs for specific errors

### Database Connection Issues
- Verify `DATABASE_URL` is correctly set
- Ensure database is in same region as web service
- Check database is running and accessible

### WebSocket Not Working
- Verify `SOCKETIO_ASYNC_MODE=gevent` is set
- Check that gevent-websocket is installed
- Ensure start command uses correct worker class

### Application Crashes
- Check application logs in Render dashboard
- Verify all environment variables are set
- Check for database initialization errors

## 🔗 Useful Links

- **Render Dashboard:** https://dashboard.render.com/
- **Render Docs:** https://render.com/docs
- **GitHub Repo:** https://github.com/mailtoparithi10-ops/mirakle-platform

## 📊 Monitoring

After deployment:
1. Check the **Logs** tab for application output
2. Monitor **Metrics** for performance
3. Set up **Alerts** for downtime or errors

## 🎉 Success!

Your application should now be live at:
```
https://mirakle-platform.onrender.com
```
(or your custom domain if configured)

## 🔄 Continuous Deployment

Render automatically deploys when you push to the `main` branch:
1. Make changes locally
2. Commit: `git commit -m "your message"`
3. Push: `git push origin main`
4. Render automatically rebuilds and deploys

---

**Last Updated:** January 29, 2026
**Status:** ✅ Ready for deployment