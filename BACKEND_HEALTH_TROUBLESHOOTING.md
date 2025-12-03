# 🔍 Backend Health Endpoint Troubleshooting

## Problem: `/health` endpoint returns "not found"

The health endpoint exists in your code, so let's diagnose why it's not accessible.

---

## ✅ Step 1: Verify Backend is Deployed

### Check Render Dashboard:

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Find your service: `drowsiness-detector-backend`
3. Check the status:
   - ✅ **"Live"** (green) = Service is running
   - ⚠️ **"Sleeping"** = Service is sleeping (free tier - will wake up on first request)
   - ❌ **"Error"** = Service failed to start

### If Status is "Error":
- Click on the service
- Go to **"Logs"** tab
- Look for error messages
- Common issues:
  - Build failed (check build logs)
  - Start command failed (check if gunicorn command is correct)
  - Port binding error
  - Missing dependencies

---

## ✅ Step 2: Get Your Actual Backend URL

Your backend URL should look like:
```
https://drowsiness-detector-backend-XXXX.onrender.com
```

**Where to find it:**
1. Render Dashboard → Your service
2. Look at the top of the page - there's a URL displayed
3. Or check the "Settings" tab → "Service Details"

**⚠️ Important:** Make sure you're using the **exact URL** from Render, not a placeholder!

---

## ✅ Step 3: Test the Health Endpoint

### Option A: Using Browser
1. Open your browser
2. Go to: `https://your-actual-backend-url.onrender.com/health`
3. You should see: `{"status": "ok"}`

### Option B: Using Terminal/Command Line
```bash
curl https://your-actual-backend-url.onrender.com/health
```

**Expected response:**
```json
{"status": "ok"}
```

### Option C: Using Browser Developer Tools
1. Open your Netlify site
2. Press F12 (Developer Tools)
3. Go to "Console" tab
4. Type:
```javascript
fetch('https://your-backend-url.onrender.com/health')
  .then(r => r.json())
  .then(console.log)
```

---

## 🐛 Common Issues & Solutions

### Issue 1: "404 Not Found"

**Possible causes:**
- ❌ Wrong URL (typo in the URL)
- ❌ Backend not deployed yet
- ❌ Service is sleeping (free tier)

**Solutions:**
1. Double-check the URL from Render dashboard
2. Make sure service status is "Live"
3. If sleeping, wait 30-60 seconds after first request (cold start)

### Issue 2: "502 Bad Gateway"

**Possible causes:**
- ❌ Service crashed
- ❌ Start command is wrong
- ❌ Port binding issue

**Solutions:**
1. Check Render logs for errors
2. Verify start command: `gunicorn api_server:app --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 120 --graceful-timeout 120`
3. Make sure `$PORT` is used (not hardcoded)

### Issue 3: "Connection Refused" or "Cannot reach"

**Possible causes:**
- ❌ Service not deployed
- ❌ Wrong URL
- ❌ Network issue

**Solutions:**
1. Verify service exists in Render dashboard
2. Check the exact URL from Render
3. Try again in a few minutes (free tier cold starts)

### Issue 4: Service Shows "Error" Status

**Check the logs:**
1. Render Dashboard → Your service → **Logs** tab
2. Look for Python errors, import errors, or startup failures

**Common errors:**
- `ModuleNotFoundError` → Missing dependency in `requirements.txt`
- `Port already in use` → Wrong start command (should use `$PORT`)
- `gunicorn: command not found` → Missing gunicorn in requirements.txt

---

## 🔧 Quick Fixes

### Fix 1: Verify Start Command in Render

Go to Render → Your service → **Settings** → **Start Command**

Should be:
```bash
gunicorn api_server:app --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 120 --graceful-timeout 120
```

**NOT:**
```bash
gunicorn api_server:app --config gunicorn_config.py
```
(This uses a config file that might have wrong port binding)

### Fix 2: Check Root Directory

Render → Your service → **Settings** → **Root Directory**

Should be: `backend`

### Fix 3: Verify Health Endpoint Code

The health endpoint should be in `backend/api_server.py`:

```python
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})
```

If it's missing, add it!

### Fix 4: Manual Redeploy

1. Render Dashboard → Your service
2. Click **"Manual Deploy"** → **"Deploy latest commit"**
3. Wait 5-10 minutes
4. Test health endpoint again

---

## ✅ Verification Checklist

Use this checklist to verify everything:

- [ ] Service exists in Render dashboard
- [ ] Service status is "Live" (not "Error")
- [ ] Backend URL copied from Render (not a placeholder)
- [ ] URL format: `https://service-name-XXXX.onrender.com`
- [ ] Health endpoint test: `curl https://your-url.onrender.com/health`
- [ ] Response: `{"status": "ok"}`

---

## 🆘 Still Not Working?

### Check Render Logs:

1. **Build Logs:**
   - Render → Your service → **Logs** tab
   - Scroll to build section
   - Look for errors during `pip install`

2. **Runtime Logs:**
   - Same logs tab, scroll to runtime section
   - Look for:
     - `[CORS] Configured origins: ...` (should appear on startup)
     - `[CORS] Frontend origin: ...` (should show your Netlify URL)
     - Any Python tracebacks or errors

3. **Common Log Messages:**

   **✅ Good (Service Starting):**
   ```
   [INFO] Starting gunicorn
   [INFO] Listening at: http://0.0.0.0:10000
   [CORS] Configured origins: {...}
   ```

   **❌ Bad (Service Failed):**
   ```
   [ERROR] ModuleNotFoundError: No module named 'flask'
   [ERROR] gunicorn: command not found
   [ERROR] Address already in use
   ```

---

## 📝 Test Commands Reference

```bash
# Test health endpoint
curl https://your-backend-url.onrender.com/health

# Test with verbose output (shows headers)
curl -v https://your-backend-url.onrender.com/health

# Test from browser console
fetch('https://your-backend-url.onrender.com/health')
  .then(r => r.json())
  .then(console.log)
  .catch(console.error)
```

---

## 🎯 Next Steps After Health Works

Once `/health` returns `{"status": "ok"}`:

1. ✅ Copy your backend URL
2. ✅ Go to Netlify → Environment variables
3. ✅ Set `REACT_APP_API_URL = https://your-backend-url.onrender.com`
4. ✅ Rebuild Netlify site
5. ✅ Test the full connection

---

**Need more help?** Check the logs in Render dashboard - they usually show exactly what's wrong!

