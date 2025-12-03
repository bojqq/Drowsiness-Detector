# Netlify 502 Error Fix

## Problem Found
The frontend was trying to POST to `https://team12ien.netlify.app/api/detect_drowsiness` instead of your Render backend, causing **502 Bad Gateway** errors.

## Root Causes

### 1. Broken `_redirects` File
The `frontend/public/_redirects` file had a placeholder:
```
/api/*  https://<your-backend-on-render>.onrender.com/:splat  200
```

This was causing Netlify to try to proxy API requests, but failing because the placeholder wasn't replaced.

### 2. Missing Environment Variable
The `REACT_APP_API_URL` environment variable needs to be set in Netlify **before** building.

## ✅ Fixes Applied

### Fix 1: Updated `_redirects` File
Changed from broken redirect to proper React Router redirect:
```
/*    /index.html   200
```

### Fix 2: Added Debug Logging
Added console logs to help verify API URL is set correctly.

## 🔧 What You Need to Do

### Step 1: Set Environment Variable in Netlify
1. Go to Netlify Dashboard
2. Your Site → **Site settings** → **Environment variables**
3. Click **Add variable**
4. Set:
   - **Key**: `REACT_APP_API_URL`
   - **Value**: `https://your-actual-render-backend-url.onrender.com`
   - **Scopes**: All scopes
   - **Values**: Same value for all deploy contexts
5. Click **Create variable**

### Step 2: Commit and Push Changes
```bash
cd /Users/ilyasmalghamdi/Documents/app2
git add frontend/public/_redirects frontend/src/App.js
git commit -m "Fix Netlify API redirect and add debug logging"
git push origin main
```

### Step 3: Trigger New Build in Netlify
1. Netlify Dashboard → **Deploys**
2. Click **Trigger deploy** → **Deploy site**
3. Wait for build to complete (2-3 minutes)

### Step 4: Verify
1. Open your Netlify site
2. Open browser console (F12)
3. Check for:
   - No more 502 errors
   - API calls going to your Render backend URL
   - Camera detection working

## 🐛 How to Verify It's Fixed

### Check Browser Console
After the new build, you should see:
- ✅ No 502 errors
- ✅ POST requests going to your Render backend (not Netlify domain)
- ✅ Successful API responses

### Test Camera
1. Allow camera permissions
2. Face should be detected
3. Close eyes → Alarm should trigger
4. Open eyes → Alarm should stop

## 📝 Important Notes

### Environment Variables Must Be Set BEFORE Build
- React environment variables are baked into the build at build time
- Setting them after build won't work
- You MUST trigger a new build after setting environment variables

### How React Environment Variables Work
- Only variables starting with `REACT_APP_` are available
- They are replaced at build time (not runtime)
- They must be set in Netlify dashboard before building

## ✅ Expected Behavior After Fix

**Before (Broken)**:
```
POST https://team12ien.netlify.app/api/detect_drowsiness
→ 502 Bad Gateway
```

**After (Fixed)**:
```
POST https://your-backend.onrender.com/detect_drowsiness
→ 200 OK (with detection results)
```

## 🚨 If Still Not Working

1. **Verify Environment Variable**:
   - Check Netlify → Environment Variables
   - Make sure `REACT_APP_API_URL` is set correctly
   - Value should be your full Render backend URL

2. **Check Build Logs**:
   - Netlify → Deploys → Latest deploy → Build log
   - Look for environment variables being loaded
   - Check for any build errors

3. **Verify Backend URL**:
   - Test your Render backend directly:
   ```bash
   curl https://your-backend.onrender.com/health
   ```
   - Should return: `{"status": "ok"}`

4. **Clear Browser Cache**:
   - Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
   - Or clear cache and reload

## 📊 Summary

**Files Changed**:
- ✅ `frontend/public/_redirects` - Fixed broken redirect
- ✅ `frontend/src/App.js` - Added debug logging

**Action Required**:
1. Set `REACT_APP_API_URL` in Netlify
2. Commit and push changes
3. Trigger new Netlify build
4. Test the site

**Result**: Frontend will now correctly connect to your Render backend! 🎉

