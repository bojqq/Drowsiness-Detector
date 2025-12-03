# Quick Deploy Commands

## 🚀 One-Page Deployment Reference

### Prerequisites
- GitHub account
- Netlify account (signup at netlify.com)
- Render account (signup at render.com)

---

## Backend (Render) - 5 Steps

### 1. Push to GitHub
```bash
cd /Users/ilyasmalghamdi/Documents/app2
git add .
git commit -m "Production ready"
git push origin main
```

### 2. Create Render Service
- Go to: https://dashboard.render.com
- Click: **New +** → **Web Service**
- Connect GitHub repository

### 3. Configure Service
```
Name: drowsiness-detector-backend
Region: Oregon
Branch: main
Root Directory: backend
Runtime: Python 3

Build Command:
pip install -r requirements.txt

Start Command:
gunicorn api_server:app --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 120 --graceful-timeout 120
```

### 4. Add Environment Variables
```
PYTHON_VERSION = 3.10.14
FRONTEND_ORIGIN = https://your-app.netlify.app
```

### 5. Deploy
- Click **Create Web Service**
- Wait 5-10 minutes
- Copy URL: `https://drowsiness-detector-backend-xxxx.onrender.com`

---

## Frontend (Netlify) - 5 Steps

### 1. Go to Netlify
- Visit: https://app.netlify.com
- Click: **Add new site** → **Import an existing project**

### 2. Connect GitHub
- Choose **GitHub**
- Select repository: `app2`
- Authorize access

### 3. Configure Build
```
Base directory: frontend
Build command: npm run build
Publish directory: frontend/build
Branch: main
```

### 4. Add Environment Variables
Go to: **Site settings** → **Environment variables**
```
REACT_APP_API_URL = https://your-backend.onrender.com
NODE_VERSION = 18
```

### 5. Deploy
- Click **Deploy site**
- Wait 2-3 minutes
- Get URL: `https://your-app-name.netlify.app`

---

## Post-Deployment

### Update Backend CORS
1. Go back to Render dashboard
2. Environment Variables → Edit **FRONTEND_ORIGIN**
3. Set to: `https://your-actual-netlify-url.netlify.app`
4. Click **Manual Deploy** → **Deploy latest commit**

### Test Everything
```bash
# Test backend health
curl https://your-backend.onrender.com/health

# Visit frontend
open https://your-app.netlify.app
```

---

## URLs to Remember

**Backend**: `https://drowsiness-detector-backend-xxxx.onrender.com`  
**Frontend**: `https://your-app-name.netlify.app`  
**GitHub**: `https://github.com/yourusername/app2`

---

## Common Issues

### Backend not responding
- Wait 30 seconds (cold start on free tier)
- Check Render logs
- Verify environment variables

### Frontend can't connect
- Check `REACT_APP_API_URL` matches backend URL
- Verify CORS is configured
- Check browser console

### Camera not working
- Must be HTTPS (Netlify provides this)
- User must allow camera permissions
- Try different browser

---

## 🎉 Done!

Your app is now live:
1. Share the Netlify URL with users
2. They can use it immediately on any device
3. Camera detection works on mobile & desktop

**First request may take 30s (cold start), then it's fast!**

