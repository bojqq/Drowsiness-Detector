# 📍 Exact Steps in Netlify - Where to Click

## Your Netlify Site: prototype201

You're currently on the **Deploys** page. Here's exactly where to go:

---

## Step 1: Go to Environment Variables

### From where you are now (Deploys page):

1. Look at the **left sidebar** (where you see "Deploys" highlighted)
2. Scroll down in that sidebar
3. Look for a **gear/settings icon** ⚙️ or text that says **"Site settings"**
4. Click on **"Site settings"**

### OR use the top navigation:

1. Look at the top of the page where it says "Projects / prototype201"
2. Click on **"Site settings"** (should be in the top navigation bar)

---

## Step 2: Find Environment Variables

Once you're in **Site settings**:

1. Look at the left sidebar menu
2. Scroll down until you see **"Environment variables"**
3. Click on **"Environment variables"**

---

## Step 3: Add the Variable

On the Environment variables page:

1. You'll see a button that says **"Add a variable"** or **"Add variable"**
2. Click that button
3. A form will appear with two fields:
   - **Key**: Type `REACT_APP_API_URL`
   - **Value**: Type `https://drowsiness-detector-1-hfyu.onrender.com`
4. Make sure **"Same value for all deploy contexts"** is selected
5. Click **"Create variable"** or **"Save"**

---

## Step 4: Trigger New Deploy

After saving the variable:

1. Go back to the **"Deploys"** page (click "Deploys" in left sidebar)
2. At the top right, you'll see a button **"Trigger deploy"**
3. Click **"Trigger deploy"** → Select **"Deploy site"**
4. Wait 2-3 minutes for the build to complete

---

## Visual Guide

```
Netlify Dashboard (prototype201)
│
├── Deploys ← (You are here)
├── Logs
├── Metrics
├── Web security
├── Domain management
├── Forms
├── Blobs
│
└── [Scroll down in left sidebar]
    │
    ├── Site settings ← (Click this first!)
    │   │
    │   └── Build & deploy
    │   └── Domain management
    │   └── Environment variables ← (Then click this!)
    │       │
    │       └── [Add variable button] ← (Click to add REACT_APP_API_URL)
    │
    └── [After adding variable]
        │
        └── Back to Deploys → Trigger deploy ← (Final step!)
```

---

## Quick Navigation Path

**Current location** → **Site settings** → **Environment variables** → **Add variable**

Then: **Deploys** → **Trigger deploy**

---

## What to Enter

```
Key: REACT_APP_API_URL
Value: https://drowsiness-detector-1-hfyu.onrender.com
```

**⚠️ No trailing slash! Copy exactly as shown.**

---

## After Deploy Completes

1. Click **"Open production deploy"** button (the teal/cyan button)
2. Press **F12** to open Developer Console
3. Look for: `[CONFIG] API_URL: https://drowsiness-detector-1-hfyu.onrender.com`
4. Test the app!

---

**Let me know when you've added the variable and triggered the deploy!**

