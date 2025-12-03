# 🎯 Render Dashboard Configuration - Exact Details

## 📋 Step-by-Step Configuration

Fill in the Render dashboard with these **exact values**:

---

## 1. Basic Information

### Name:
```
drowsiness-detector-backend
```

### Language:
```
Python 3
```
(Already selected ✅)

### Branch:
```
main
```
(Already selected ✅)

### Region:
```
Oregon (US West)
```
(Already selected ✅)

---

## 2. Root Directory ⚠️ IMPORTANT

### Root Directory:
```
backend
```

**Why:** Your backend code is in the `backend/` folder, not the root of the repository.

---

## 3. Build Command

### Build Command:
```bash
pip install -r requirements.txt
```

**What it does:** Installs all Python dependencies before deploying.

---

## 4. Start Command ⚠️ CRITICAL

### Start Command:
```bash
gunicorn api_server:app --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 120 --graceful-timeout 120
```

**Breakdown:**
- `gunicorn` - Production WSGI server
- `api_server:app` - Your Flask app (file: `api_server.py`, variable: `app`)
- `--bind 0.0.0.0:$PORT` - Listen on all interfaces, use Render's PORT
- `--workers 1` - One worker process (free tier)
- `--threads 2` - Two threads per worker
- `--timeout 120` - Request timeout (2 minutes)
- `--graceful-timeout 120` - Graceful shutdown timeout

---

## 5. Environment Variables ⚠️ MUST SET

Click **"+ Add Environment Variable"** and add these **two variables**:

### Variable 1:
```
NAME: PYTHON_VERSION
VALUE: 3.10.14
```

### Variable 2:
```
NAME: FRONTEND_ORIGIN
VALUE: https://prototype201.netlify.app
```

**⚠️ IMPORTANT:** Replace `prototype201.netlify.app` with your **actual Netlify URL**!

**How to find your Netlify URL:**
1. Go to [Netlify Dashboard](https://app.netlify.com)
2. Click on your site
3. Copy the URL from the top (e.g., `https://your-site-name.netlify.app`)

---

## 6. Instance Type

**For Free Tier:**
- Select **Free** instance type (if available)
- Or leave default (usually free tier is automatic)

**Note:** Free tier is sufficient for this application.

---

## 7. Deploy

Click **"Deploy Web Service"** button at the bottom.

---

## ⏱️ What Happens Next

1. **Build Phase** (5-10 minutes first time):
   - Render clones your repository
   - Runs `pip install -r requirements.txt`
   - Installs all dependencies

2. **Deploy Phase** (1-2 minutes):
   - Starts gunicorn server
   - Your backend becomes live

3. **Get Your Backend URL:**
   - After deployment completes
   - Your URL will be: `https://drowsiness-detector-backend-xxxx.onrender.com`
   - **SAVE THIS URL** - you'll need it for Netlify!

---

## ✅ Verification Checklist

After deployment, verify:

1. **Service Status:**
   - Should show "Live" (green)
   - Not "Sleeping" or "Error"

2. **Test Health Endpoint:**
   ```bash
   curl https://drowsiness-detector-backend-xxxx.onrender.com/health
   ```
   Should return: `{"status": "ok"}`

3. **Check Logs:**
   - Click "Logs" tab in Render
   - Should see: `[CORS] Configured origins: ...`
   - Should see: `[CORS] Frontend origin: https://your-netlify-url.netlify.app`
   - No Python errors

---

## 🔧 If Something Goes Wrong

### Build Fails:
- Check "Logs" tab for error messages
- Common issues:
  - Missing `requirements.txt` → Make sure it exists in `backend/` folder
  - Wrong Python version → Verify `PYTHON_VERSION = 3.10.14`
  - Dependency conflicts → Check `requirements.txt` syntax

### Service Won't Start:
- Check "Logs" tab
- Common issues:
  - Wrong start command → Verify gunicorn command matches above
  - Port binding error → Make sure using `$PORT` (not hardcoded)
  - Module not found → Check `api_server.py` exists in `backend/` folder

### CORS Errors:
- Verify `FRONTEND_ORIGIN` matches your Netlify URL **exactly**
- No trailing slashes
- Must be `https://` not `http://`

---

## 📝 Quick Copy-Paste Reference

**Root Directory:**
```
backend
```

**Build Command:**
```
pip install -r requirements.txt
```

**Start Command:**
```
gunicorn api_server:app --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 120 --graceful-timeout 120
```

**Environment Variables:**
```
PYTHON_VERSION = 3.10.14
FRONTEND_ORIGIN = https://prototype201.netlify.app
```
(Replace with your actual Netlify URL!)

---

## 🎯 Next Steps After Render Setup

Once your backend is deployed:

1. **Copy your backend URL** from Render dashboard
2. **Go to Netlify** → Site settings → Environment variables
3. **Add:** `REACT_APP_API_URL = https://your-backend-url.onrender.com`
4. **Rebuild** your Netlify site

See `QUICK_FIX_STEPS.md` for Netlify configuration details.

---

**Status:** ✅ Ready to deploy
**Estimated Time:** 5-10 minutes for first deployment

