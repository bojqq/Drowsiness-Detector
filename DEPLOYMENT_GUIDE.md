# Deployment Guide - Netlify & Render

## Overview
This guide covers deploying the drowsiness detector:
- **Frontend**: Netlify (React app)
- **Backend**: Render (Python Flask API)

## ✅ Pre-Deployment Checklist

### Frontend Ready
- ✅ Production build created (`npm run build`)
- ✅ All responsive styles included
- ✅ Alarm system working
- ✅ Mobile-optimized
- ✅ `netlify.toml` configuration added
- ✅ `_redirects` file in build folder

### Backend Ready
- ✅ `requirements.txt` up to date
- ✅ `Procfile` configured for Render
- ✅ `gunicorn_config.py` optimized
- ✅ `render.yaml` configured
- ✅ CORS configured for production
- ✅ Environment variables ready

---

## 🚀 Backend Deployment (Render)

### Step 1: Create Render Account
1. Go to https://render.com
2. Sign up with GitHub
3. Authorize Render to access your repository

### Step 2: Create New Web Service
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Select the repository: `app2`
4. Configure:
   - **Name**: `drowsiness-detector-backend`
   - **Region**: Oregon (US West)
   - **Branch**: `main`
   - **Root Directory**: `backend`
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn api_server:app --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 120`

### Step 3: Environment Variables
Add these in Render dashboard:
```
PYTHON_VERSION = 3.10.14
FRONTEND_ORIGIN = https://your-app-name.netlify.app
PORT = 10000 (auto-set by Render)
```

### Step 4: Deploy
1. Click "Create Web Service"
2. Wait for deployment (5-10 minutes first time)
3. Copy your backend URL: `https://drowsiness-detector-backend.onrender.com`

### Step 5: Test Backend
```bash
curl https://your-backend-url.onrender.com/health
# Should return: {"status": "ok"}
```

---

## 🌐 Frontend Deployment (Netlify)

### Step 1: Create Netlify Account
1. Go to https://netlify.com
2. Sign up with GitHub
3. Authorize Netlify

### Step 2: Deploy from GitHub
1. Click "Add new site" → "Import an existing project"
2. Choose "Deploy with GitHub"
3. Select your repository: `app2`
4. Configure:
   - **Base directory**: `frontend`
   - **Build command**: `npm run build`
   - **Publish directory**: `frontend/build`
   - **Branch**: `main`

### Step 3: Environment Variables
Go to Site Settings → Environment Variables:
```
REACT_APP_API_URL = https://your-backend-url.onrender.com
NODE_VERSION = 18.x
```

### Step 4: Deploy
1. Click "Deploy site"
2. Wait for build (2-3 minutes)
3. Get your URL: `https://your-app-name.netlify.app`

### Step 5: Update Backend CORS
Go back to Render and update the environment variable:
```
FRONTEND_ORIGIN = https://your-actual-netlify-url.netlify.app
```
Then redeploy the backend.

---

## 🔧 Configuration Files

### Frontend: `netlify.toml`
```toml
[build]
  base = "frontend"
  command = "npm run build"
  publish = "build"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

### Frontend: `frontend/public/_redirects`
```
/*    /index.html   200
```

### Backend: `render.yaml`
```yaml
services:
  - type: web
    name: drowsiness-detector-backend
    env: python
    region: oregon
    plan: free
    branch: main
    rootDir: backend
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn api_server:app --bind 0.0.0.0:$PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.10.14
      - key: FRONTEND_ORIGIN
        value: https://your-netlify-url.netlify.app
```

### Backend: `backend/Procfile`
```
web: gunicorn api_server:app --config gunicorn_config.py
```

---

## 🔄 Continuous Deployment

### Automatic Deployments
Both platforms support auto-deploy on git push:

**Netlify**:
- Push to `main` branch → Auto-deploy frontend
- Build time: ~2-3 minutes
- Zero downtime

**Render**:
- Push to `main` branch → Auto-deploy backend
- Build time: ~5-10 minutes
- Free tier may have cold starts

### Manual Deployments
**Netlify**: Click "Trigger deploy" in dashboard  
**Render**: Click "Manual Deploy" → "Deploy latest commit"

---

## 📊 Post-Deployment Checklist

### Test Frontend
- [ ] Visit Netlify URL
- [ ] Landing page loads
- [ ] Camera permissions work
- [ ] Face detection works
- [ ] Alarm sounds play
- [ ] Mobile responsive
- [ ] No console errors

### Test Backend
- [ ] Visit `https://backend-url.onrender.com/health`
- [ ] Returns `{"status": "ok"}`
- [ ] CORS headers allow frontend
- [ ] Detection endpoint works
- [ ] Processes images correctly

### Test Integration
- [ ] Frontend connects to backend
- [ ] Face detection works end-to-end
- [ ] Alarm triggers on drowsiness
- [ ] Recovery detection works
- [ ] Mobile devices work
- [ ] Multiple users can access

---

## 🐛 Troubleshooting

### Frontend Issues

**"Failed to fetch" errors**:
- Check `REACT_APP_API_URL` environment variable
- Verify backend URL is correct
- Check browser console for errors

**Camera not working**:
- Ensure HTTPS (Netlify provides this)
- Check camera permissions in browser
- Test on different browsers

**Blank page**:
- Check build logs in Netlify
- Verify all files built correctly
- Check for JavaScript errors

### Backend Issues

**Backend not responding**:
- Check Render logs
- Verify service is running
- Check for memory/CPU limits

**CORS errors**:
- Update `FRONTEND_ORIGIN` environment variable
- Redeploy backend after changes
- Check allowed origins in `api_server.py`

**Slow response (cold start)**:
- Free tier has cold starts (~30s)
- First request may be slow
- Subsequent requests are fast

---

## 💰 Cost Breakdown

### Free Tier Limits

**Netlify Free**:
- 100 GB bandwidth/month
- 300 build minutes/month
- Unlimited sites
- Custom domains
- HTTPS included

**Render Free**:
- 750 hours/month
- Sleeps after 15 min inactivity
- Cold start on wake (~30s)
- 512 MB RAM
- Shared CPU

### Upgrading

**Netlify Pro ($19/month)**:
- 400 GB bandwidth
- Faster builds
- No sleep

**Render Starter ($7/month)**:
- No sleep
- Always on
- More resources
- Faster performance

---

## 🔒 Security Best Practices

### Environment Variables
- Never commit API keys
- Use Netlify/Render dashboards
- Rotate keys regularly

### CORS Configuration
- Only allow specific origins
- Don't use wildcard `*` in production
- Update when deploying to new domains

### HTTPS
- Always use HTTPS (both provide this)
- Enforce HTTPS redirects
- Use secure cookies

---

## 📈 Monitoring

### Netlify Analytics
- Page views
- Build history
- Deploy status
- Bandwidth usage

### Render Metrics
- CPU usage
- Memory usage
- Request logs
- Error logs

### User Monitoring
- Browser console errors
- Camera permission rates
- Detection accuracy
- Mobile vs desktop usage

---

## 🔄 Updates & Maintenance

### Updating Frontend
```bash
# Make changes
cd frontend
npm run build

# Commit and push
git add .
git commit -m "Update frontend"
git push origin main

# Netlify auto-deploys
```

### Updating Backend
```bash
# Make changes to backend/
git add backend/
git commit -m "Update backend"
git push origin main

# Render auto-deploys
```

### Rollback
**Netlify**: Deploys → Select previous → "Publish deploy"  
**Render**: Manual Deploy → Select previous commit

---

## 📝 Final URLs

After deployment, you'll have:

**Frontend (Netlify)**:
- Production: `https://drowsiness-detector-ai.netlify.app`
- Preview: Auto-generated for pull requests

**Backend (Render)**:
- Production: `https://drowsiness-detector-backend.onrender.com`
- Health check: `https://your-backend.onrender.com/health`

---

## ✅ Deployment Complete!

Your drowsiness detector is now live and accessible worldwide:
- 🌍 Global CDN (Netlify)
- 🚀 Fast response times
- 📱 Mobile-optimized
- 🔒 HTTPS secure
- 💰 Free tier (for moderate usage)

**Share your app**: Send the Netlify URL to users!

---

## 📞 Support Resources

- **Netlify Docs**: https://docs.netlify.com
- **Render Docs**: https://render.com/docs
- **React Build Issues**: https://create-react-app.dev
- **Flask Deployment**: https://flask.palletsprojects.com

---

## 🎉 Success Metrics

Monitor these to ensure successful deployment:
- ✅ Frontend loads in <2 seconds
- ✅ Backend responds in <1 second
- ✅ Face detection works on mobile
- ✅ Alarm sounds reliable
- ✅ 99%+ uptime
- ✅ No CORS errors
- ✅ Camera permissions granted

**Your drowsiness detector is now production-ready!** 🚀

