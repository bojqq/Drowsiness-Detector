# 🚀 Quick Fix Steps - 502 Error Resolution

## The Problem
Frontend on Netlify can't connect to backend on Render → 502 Bad Gateway errors

## The Solution (3 Steps)

### Step 1: Set Environment Variable in Netlify ⚠️ CRITICAL

1. Go to [Netlify Dashboard](https://app.netlify.com)
2. Your site → **Site settings** → **Environment variables**
3. Add/Edit:
   - **Key**: `REACT_APP_API_URL`
   - **Value**: `https://your-backend-url.onrender.com`
     (Get this from Render dashboard - your backend service URL)
4. **Save**

### Step 2: Rebuild Frontend

1. In Netlify dashboard → **Deploys**
2. Click **Trigger deploy** → **Deploy site**
3. Wait 2-3 minutes

### Step 3: Verify Backend CORS

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Your backend service → **Environment** tab
3. Verify `FRONTEND_ORIGIN` matches your Netlify URL:
   ```
   FRONTEND_ORIGIN = https://prototype201.netlify.app
   ```
4. If changed, click **Manual Deploy**

---

## ✅ Test It Works

1. Open your Netlify site
2. Open browser console (F12)
3. Look for:
   ```
   [CONFIG] API_URL: https://your-backend-url.onrender.com
   ```
4. No 502 errors = ✅ Fixed!

---

## 🐛 Still Not Working?

**Check these:**
- [ ] `REACT_APP_API_URL` is set in Netlify (not empty, no trailing slash)
- [ ] Frontend was rebuilt after setting environment variable
- [ ] Backend is running: `curl https://your-backend.onrender.com/health`
- [ ] `FRONTEND_ORIGIN` in Render matches your Netlify URL exactly

**See full guide:** `COMPLETE_REBUILD_GUIDE.md`

