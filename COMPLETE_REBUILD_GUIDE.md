# Complete Rebuild Guide - Netlify & Render Connection Fix

## 🎯 Overview
This guide will help you rebuild and fix the connection between your Netlify frontend and Render backend. Follow these steps **in order** to ensure everything works correctly.

---

## ✅ Pre-Flight Checklist

Before starting, make sure you have:
- [ ] GitHub repository pushed and up to date
- [ ] Render account (free tier works)
- [ ] Netlify account (free tier works)
- [ ] Your Netlify site URL (e.g., `https://prototype201.netlify.app`)
- [ ] Terminal access to run commands

---

## 🚀 Step 1: Backend Setup on Render

### 1.1 Create/Update Render Web Service

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **New +** → **Web Service**
3. Connect your GitHub repository (`app2`)
4. Configure the service:

```
Name: drowsiness-detector-backend
Region: Oregon (or closest to you)
Branch: main
Root Directory: backend
Runtime: Python 3
```

### 1.2 Set Build & Start Commands

**Build Command:**
```bash
pip install -r requirements.txt
```

**Start Command:**
```bash
gunicorn api_server:app --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 120 --graceful-timeout 120
```

### 1.3 Set Environment Variables in Render

Go to **Environment** tab and add:

```
PYTHON_VERSION = 3.10.14
FRONTEND_ORIGIN = https://prototype201.netlify.app
```

**⚠️ IMPORTANT:** Replace `prototype201.netlify.app` with your **actual Netlify URL**!

### 1.4 Deploy Backend

1. Click **Create Web Service** (or **Manual Deploy** if updating)
2. Wait 5-10 minutes for first deployment
3. **Copy your backend URL** - it will look like:
   ```
   https://drowsiness-detector-backend-xxxx.onrender.com
   ```
   ⚠️ **SAVE THIS URL** - you'll need it in the next step!

### 1.5 Test Backend

Open a terminal and run:
```bash
curl https://your-backend-url.onrender.com/health
```

Expected response:
```json
{"status": "ok"}
```

If you get an error, wait a few more minutes (cold start on free tier) and try again.

---

## 🌐 Step 2: Frontend Setup on Netlify

### 2.1 Create/Update Netlify Site

1. Go to [Netlify Dashboard](https://app.netlify.com)
2. Click **Add new site** → **Import an existing project**
3. Choose **GitHub** and select your repository (`app2`)

### 2.2 Configure Build Settings

In the build configuration:

```
Base directory: frontend
Build command: npm run build
Publish directory: frontend/build
Branch: main
```

### 2.3 ⚠️ CRITICAL: Set Environment Variable

**This is the most important step!**

1. Go to **Site settings** → **Environment variables**
2. Click **Add variable**
3. Set:
   - **Key**: `REACT_APP_API_URL`
   - **Value**: `https://your-backend-url.onrender.com`
     (Use the URL you copied from Step 1.4 - **NO trailing slash**)
   - **Scopes**: All scopes
4. Click **Save**

**Example:**
```
REACT_APP_API_URL = https://drowsiness-detector-backend-xxxx.onrender.com
```

### 2.4 Deploy Frontend

1. Click **Deploy site** (or **Trigger deploy** if updating)
2. Wait 2-3 minutes for build to complete
3. Your site will be available at: `https://your-site-name.netlify.app`

---

## 🔄 Step 3: Update Backend CORS (If Needed)

If your Netlify URL changed or you want to add additional domains:

1. Go back to Render Dashboard
2. Your service → **Environment** tab
3. Update `FRONTEND_ORIGIN` to match your **actual Netlify URL**:
   ```
   FRONTEND_ORIGIN = https://your-actual-netlify-url.netlify.app
   ```
4. Click **Save Changes**
5. Click **Manual Deploy** → **Deploy latest commit**

---

## ✅ Step 4: Verify Everything Works

### 4.1 Test Backend Health
```bash
curl https://your-backend-url.onrender.com/health
```
Should return: `{"status": "ok"}`

### 4.2 Test Frontend Connection

1. Open your Netlify site in a browser
2. Open **Developer Console** (F12 or Right-click → Inspect → Console)
3. Look for these logs:
   ```
   [CONFIG] API_URL: https://your-backend-url.onrender.com
   [CONFIG] REACT_APP_API_URL env: https://your-backend-url.onrender.com
   ```
4. Allow camera access
5. Check console for:
   - ✅ No 502 errors
   - ✅ POST requests going to your Render backend (not Netlify domain)
   - ✅ Face detection working

### 4.3 Expected Console Output

**✅ Good (Working):**
```
[CONFIG] API_URL: https://drowsiness-detector-backend-xxxx.onrender.com
[CONFIG] REACT_APP_API_URL env: https://drowsiness-detector-backend-xxxx.onrender.com
[DEBUG] EAR: 0.285 | Raw: 0.287 | Drowsy: false | Score: 12.5/100
```

**❌ Bad (Not Working):**
```
[CONFIG] API_URL: http://localhost:5001
[ERROR] ⚠️ REACT_APP_API_URL is not set in Netlify environment variables!
POST https://prototype201.netlify.app/api/detect_drowsiness 502 (Bad Gateway)
```

---

## 🐛 Troubleshooting

### Problem: 502 Bad Gateway Errors

**Cause:** Frontend can't reach backend

**Solutions:**
1. ✅ Check `REACT_APP_API_URL` is set in Netlify (Step 2.3)
2. ✅ Verify backend URL is correct (no trailing slash)
3. ✅ Rebuild frontend after setting environment variable
4. ✅ Check backend is running: `curl https://your-backend.onrender.com/health`

### Problem: CORS Errors

**Cause:** Backend not allowing your Netlify domain

**Solutions:**
1. ✅ Update `FRONTEND_ORIGIN` in Render to match your Netlify URL exactly
2. ✅ Redeploy backend after changing environment variable
3. ✅ Check backend logs in Render dashboard for CORS messages

### Problem: "API_URL not configured" Error

**Cause:** `REACT_APP_API_URL` not set or empty

**Solutions:**
1. ✅ Go to Netlify → Site settings → Environment variables
2. ✅ Add/update `REACT_APP_API_URL` with your Render backend URL
3. ✅ Trigger a new deploy (environment variables require rebuild)

### Problem: Backend Returns 500 Error

**Cause:** Backend code error or missing dependencies

**Solutions:**
1. ✅ Check Render logs for error messages
2. ✅ Verify `requirements.txt` is up to date
3. ✅ Check backend is using correct Python version (3.10.14)

### Problem: Frontend Shows "Connection error"

**Cause:** Network issue or backend down

**Solutions:**
1. ✅ Test backend health endpoint directly
2. ✅ Check Render dashboard - service should be "Live"
3. ✅ Wait 30 seconds (free tier cold starts)
4. ✅ Check browser console for specific error message

---

## 📋 Quick Reference Checklist

Use this checklist to verify everything is set up correctly:

### Backend (Render)
- [ ] Service is "Live" in Render dashboard
- [ ] `PYTHON_VERSION = 3.10.14` is set
- [ ] `FRONTEND_ORIGIN = https://your-netlify-url.netlify.app` is set
- [ ] Health endpoint returns `{"status": "ok"}`
- [ ] Backend URL copied and saved

### Frontend (Netlify)
- [ ] `REACT_APP_API_URL = https://your-backend-url.onrender.com` is set
- [ ] Environment variable has **no trailing slash**
- [ ] Build completed successfully
- [ ] Console shows correct API_URL (not localhost)
- [ ] No 502 errors in console

### Connection Test
- [ ] Camera access granted
- [ ] Face detection working
- [ ] No CORS errors
- [ ] API calls going to Render backend (check Network tab)

---

## 🔧 Manual Rebuild Steps (If Something Goes Wrong)

### Option 1: Rebuild Everything

1. **Backend:**
   ```bash
   # In Render dashboard
   - Go to your service
   - Click "Manual Deploy" → "Deploy latest commit"
   ```

2. **Frontend:**
   ```bash
   # In Netlify dashboard
   - Go to your site
   - Click "Trigger deploy" → "Deploy site"
   ```

### Option 2: Fix Environment Variables

1. **Update Netlify:**
   - Site settings → Environment variables
   - Edit `REACT_APP_API_URL`
   - Trigger new deploy

2. **Update Render:**
   - Environment tab
   - Edit `FRONTEND_ORIGIN`
   - Manual deploy

---

## 📝 Important Notes

1. **Environment Variables:**
   - Must be set **BEFORE** building
   - Changes require a **new build/deploy**
   - No trailing slashes in URLs

2. **Backend URL Format:**
   ```
   ✅ Correct: https://drowsiness-detector-backend-xxxx.onrender.com
   ❌ Wrong: https://drowsiness-detector-backend-xxxx.onrender.com/
   ❌ Wrong: http://drowsiness-detector-backend-xxxx.onrender.com
   ```

3. **Free Tier Limitations:**
   - Render: Services sleep after 15 min inactivity (cold start ~30s)
   - Netlify: Builds may take 2-3 minutes
   - Both: First request after sleep is slower

4. **Testing:**
   - Always test in **incognito/private window** to avoid cache issues
   - Check browser console for detailed error messages
   - Use Network tab to see actual API calls

---

## 🎉 Success Indicators

You'll know everything is working when:

1. ✅ Browser console shows correct API_URL (Render backend)
2. ✅ No 502 or CORS errors
3. ✅ Face detection works
4. ✅ Drowsiness alerts trigger correctly
5. ✅ Network tab shows POST requests to Render backend

---

## 🆘 Still Having Issues?

1. **Check Backend Logs:**
   - Render dashboard → Your service → Logs tab
   - Look for CORS errors or Python exceptions

2. **Check Frontend Logs:**
   - Netlify dashboard → Your site → Deploys → Click latest deploy → View logs
   - Look for build errors

3. **Check Browser Console:**
   - Open DevTools (F12)
   - Console tab: Look for `[CONFIG]` and `[ERROR]` messages
   - Network tab: Check actual API requests and responses

4. **Verify URLs:**
   - Backend: `curl https://your-backend.onrender.com/health`
   - Frontend: Check console for `[CONFIG] API_URL` log

---

## 📞 Quick Commands Reference

```bash
# Test backend health
curl https://your-backend-url.onrender.com/health

# Check if environment variable is set (in Netlify build logs)
# Look for: [CONFIG] API_URL: https://...

# View backend logs (in Render dashboard)
# Go to: Your service → Logs tab

# View frontend build logs (in Netlify dashboard)
# Go to: Your site → Deploys → Latest deploy → View logs
```

---

**Last Updated:** After fixing 502 connection errors
**Status:** ✅ Ready for deployment

