# Deployment Guide

This project contains a React frontend (`frontend/`) and a Flask + MediaPipe backend (`backend/`). Follow the sections below to run locally and to deploy everything on a full-stack host such as Render, Railway, Fly.io, or Heroku.

---

## 1. Local Development

### Prerequisites
- Node.js 18+
- Python 3.10+

### Backend
```bash
cd backend
python -m venv .venv
source .venv/bin/activate         # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
python api_server.py               # runs on http://localhost:5001
```

### Frontend
```bash
cd frontend
npm install
npm start                          # runs on http://localhost:3000
```

Environment variables (`frontend/.env.development`) already point the frontend to `http://localhost:5001`, so once both servers are running you can open `http://localhost:3000` and allow camera access.

---

## 2. Production Build (React)

```bash
cd frontend
npm install
npm run build                      # outputs static files to frontend/build
```

The build expects a backend available at `/api` relative to the site origin (configured in `.env.production`).

---

## 3. Full-Stack Hosting (Render / Railway / Fly / Heroku)

Below is an example using **Render**, but the same pattern applies to any full-stack platform:

1. **Repository**
   - Push this repository to GitHub/GitLab.

2. **Backend Service**
   - Create a Render **Web Service** pointing to the repo.
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn api_server:app --bind 0.0.0.0:$PORT`
   - Environment Variables:
     - `FRONTEND_ORIGIN=https://your-app.onrender.com`
     - (Optional) `ADDITIONAL_ORIGINS=https://www.yourcustomdomain.com`

3. **Frontend Service**
   - Create a Render **Static Site**.
   - Root Directory: `frontend`
   - Build Command: `npm install && npm run build`
   - Publish Directory: `build`
   - Set environment variable `REACT_APP_API_URL=/api`
   - Configure a redirect/rewrite so that `/api/*` proxies to the backend service:
     ```
     /api/*    https://your-backend-service.onrender.com/api/*
     ```
     (If your backend routes are defined without `/api`, proxy `/api/detect_drowsiness` → `https://backend.../detect_drowsiness` etc.)

4. **Custom Domains**
   - Point DNS to your hosting provider.
   - Update `FRONTEND_ORIGIN` and `ADDITIONAL_ORIGINS` to match the final domain(s).

---

## 4. Environment Variables Summary

| Location        | Variable             | Description                                    |
|-----------------|----------------------|------------------------------------------------|
| frontend/.env.development | `REACT_APP_API_URL` | Local API root (`http://localhost:5001`)       |
| frontend/.env.production  | `REACT_APP_API_URL` | Production API root (`/api`)                   |
| backend env     | `FRONTEND_ORIGIN`    | Primary allowed origin for CORS                |
| backend env     | `ADDITIONAL_ORIGINS` | Comma-separated extra origins for CORS         |
| backend env     | `PORT`               | (Provided by host) Port Flask should listen on |

---

## 5. Post-Deployment Checklist

1. Visit `https://your-domain/health` (proxied to backend) to confirm backend is responding.
2. Load the frontend domain, open dev tools console:
   - Confirm `Camera active` status appears.
   - Ensure there are no CORS or network errors.
3. Trigger drowsiness detection:
   - Allow camera access.
   - Close eyes for ~3 seconds to confirm alerts fire.

If something fails:
- Check hosting logs for both services.
- Verify environment variables.
- Confirm proxy/rewrite rules forward `/api/*` to the backend.

---

## 6. Alternate Setup (Single Container)

If you prefer to host both services from one container/server:
1. Serve the React build with any static-file server (Nginx, Flask `send_from_directory`, etc.).
2. Proxy `/api` requests to the Flask app internally.
3. Ensure the frontend build still uses `REACT_APP_API_URL=/api`.

This approach is ideal for platforms like Fly.io or custom VPS deployments where you manage the reverse proxy yourself.

---

With these steps, `npm run build` creates assets ready for Netlify or any static host, and the backend can run on any platform that supports Python. Configure rewrites/proxies so `/api` reaches the Flask service and the camera-powered AI will work end-to-end in production.

