# 🚀 Rafad Clinic System - Deployment Guide

## Overview
This guide provides step-by-step instructions to deploy your Flask clinic system online.

---

## 📋 Prerequisites
- Git installed on your computer
- GitHub account (free)
- Your application tested locally and working

---

## ✅ Option 1: Deploy to Render (Recommended - Free)

### Step 1: Push to GitHub

1. **Initialize Git Repository** (if not already done)
```powershell
cd c:\Users\maiso\rafad_clinic_system
git init
git add .
git commit -m "Initial commit - Ready for deployment"
```

2. **Create GitHub Repository**
   - Go to https://github.com/new
   - Repository name: `rafad-clinic-system`
   - Keep it Public or Private
   - Don't initialize with README (you already have files)
   - Click "Create repository"

3. **Push to GitHub**
```powershell
git remote add origin https://github.com/YOUR_USERNAME/rafad-clinic-system.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy on Render

1. **Sign up for Render**
   - Go to https://render.com
   - Sign up with GitHub (easiest)

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository: `rafad-clinic-system`
   - Configure:
     - **Name**: `rafad-clinic`
     - **Environment**: `Python 3`
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn run:app`
     - **Instance Type**: `Free`

3. **Set Environment Variables**
   - Click "Environment" tab
   - Add these variables:
     ```
     FLASK_CONFIG = production
     SECRET_KEY = [Render will auto-generate or use a strong random string]
     PYTHON_VERSION = 3.11.0
     ```

4. **Deploy**
   - Click "Create Web Service"
   - Wait 5-10 minutes for deployment
   - Your app will be live at: `https://rafad-clinic.onrender.com`

5. **Initialize Database** (Important!)
   - After first deployment, go to your service's "Shell" tab
   - Run:
     ```bash
     flask init_db
     flask seed_db
     ```

### 🎉 Done! Your clinic system is now live!

---

## ✅ Option 2: Deploy to PythonAnywhere (Easiest)

### Step 1: Sign Up
1. Go to https://www.pythonanywhere.com
2. Create a free "Beginner" account
3. Confirm your email

### Step 2: Upload Your Code
1. Click "Files" tab
2. Upload your entire project folder OR use Git:
   ```bash
   git clone https://github.com/YOUR_USERNAME/rafad-clinic-system.git
   cd rafad-clinic-system
   ```

### Step 3: Set Up Virtual Environment
1. Click "Consoles" → "Bash"
2. Run:
   ```bash
   mkvirtualenv --python=/usr/bin/python3.11 rafad-env
   cd rafad-clinic-system
   pip install -r requirements.txt
   ```

### Step 4: Configure Web App
1. Click "Web" tab → "Add a new web app"
2. Choose "Manual configuration" → Python 3.11
3. In the "Code" section:
   - **Source code**: `/home/YOUR_USERNAME/rafad-clinic-system`
   - **Working directory**: `/home/YOUR_USERNAME/rafad-clinic-system`
4. Edit WSGI configuration file:
   ```python
   import sys
   path = '/home/YOUR_USERNAME/rafad-clinic-system'
   if path not in sys.path:
       sys.path.append(path)
   
   from run import app as application
   ```
5. In "Virtualenv" section:
   - Enter: `/home/YOUR_USERNAME/.virtualenvs/rafad-env`

### Step 5: Initialize Database
1. Open a Bash console
2. Run:
   ```bash
   cd rafad-clinic-system
   export FLASK_APP=run.py
   flask init_db
   flask seed_db
   ```

### Step 6: Reload Web App
1. Go back to "Web" tab
2. Click "Reload YOUR_USERNAME.pythonanywhere.com"
3. Visit: `https://YOUR_USERNAME.pythonanywhere.com`

### 🎉 Your clinic is live!

---

## ✅ Option 3: Deploy to Railway

### Step 1: Push to GitHub (same as Render)

### Step 2: Deploy on Railway
1. Go to https://railway.app
2. Sign up with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your `rafad-clinic-system` repository
5. Railway auto-detects Python and deploys
6. Add environment variables in Settings:
   ```
   FLASK_CONFIG = production
   SECRET_KEY = your-secret-key-here
   ```
7. Initialize database via Railway CLI or web console:
   ```bash
   flask init_db
   flask seed_db
   ```

### 🎉 Live at: `https://your-app.up.railway.app`

---

## 🔧 Post-Deployment Checklist

### 1. Test Your Deployment
- ✅ Visit your live URL
- ✅ Try logging in as admin (admin@rafadclinic.com / Admin@123)
- ✅ Create a test patient account
- ✅ Book a test appointment
- ✅ Check analytics dashboard
- ✅ Test CSV export

### 2. Update Clinic Information
- Login as admin
- Update contact information for your actual clinic
- Verify Google Maps link works

### 3. Change Default Admin Password
After deployment, create a new admin with a secure password:
```python
flask shell
>>> from app.models.user import User
>>> from app import db
>>> admin = User.query.filter_by(email='admin@rafadclinic.com').first()
>>> admin.password = 'YOUR_NEW_SECURE_PASSWORD'
>>> db.session.commit()
```

### 4. Set Up Custom Domain (Optional)
- Purchase a domain (e.g., rafadclinic.com)
- Add custom domain in your hosting platform settings
- Update DNS records as instructed

---

## 📊 Monitoring & Maintenance

### Check Logs
- **Render**: Dashboard → Logs tab
- **PythonAnywhere**: Web tab → Error log, Server log
- **Railway**: Dashboard → Deployments → Logs

### Database Backups
Schedule regular backups:
```bash
# Export database
sqlite3 rafad_prod.sqlite .dump > backup_$(date +%Y%m%d).sql

# Import backup
sqlite3 rafad_prod.sqlite < backup_20250101.sql
```

### Update Your App
```bash
git add .
git commit -m "Update description"
git push origin main
```
Most platforms auto-deploy on push!

---

## 🆘 Troubleshooting

### "Application Error" or 500 Error
1. Check logs for error details
2. Verify all environment variables are set
3. Ensure database is initialized
4. Check SECRET_KEY is set

### Database Not Found
```bash
flask init_db
flask seed_db
```

### Static Files Not Loading
- Check `UPLOAD_FOLDER` path in production config
- Ensure folders exist: `mkdir -p app/static/uploads`

### Can't Login
- Verify database was seeded
- Check user table has admin account
- Try resetting password via Flask shell

---

## 💰 Cost Comparison

| Platform | Free Tier | Best For | Limitations |
|----------|-----------|----------|-------------|
| **Render** | ✅ Yes | Production apps | Sleeps after 15min inactive |
| **PythonAnywhere** | ✅ Yes | Learning/Testing | 100k requests/day |
| **Railway** | $5 credit/mo | Development | Credit runs out |
| **Heroku** | ❌ No | Enterprise | $5+/month |

---

## 🎓 Need Help?

Common issues:
1. **Import errors**: Check Python version matches (3.11)
2. **Database errors**: Run init_db and seed_db
3. **Static files 404**: Check file paths are relative
4. **Timeout errors**: Free tiers may have limits

---

## 🌟 Your Deployment URLs

After deployment, your clinic will be accessible at:
- **Render**: `https://rafad-clinic.onrender.com`
- **PythonAnywhere**: `https://YOUR_USERNAME.pythonanywhere.com`
- **Railway**: `https://rafad-clinic.up.railway.app`

Share this URL with your users! 🎉
