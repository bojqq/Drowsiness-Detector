<!-- 5fd585f7-60e9-4f93-9822-588ee4e46432 e7f919fe-13ef-4eca-8367-a0498ce6b42b -->
# Fix Netlify Redirect

## Goal

Ensure the `_redirects` file points `/api/*` requests to the correct Render backend URL so the hosted frontend can reach the API.

## Steps

1. Update [`frontend/public/_redirects`](frontend/public/_redirects) to replace the placeholder domain with `https://drowsiness-detector-ctvt.onrender.com`.
2. Rebuild the frontend (as part of deployment) so the updated `_redirects` file is included in the Netlify upload.
3. Redeploy the Netlify site and verify `/api/*` requests reach the backend.

### To-dos

- [ ] Update index.css with light green/white theme and modern base styles
- [ ] Create LandingPage.js with hero, statistics, and how-it-works sections
- [ ] Create LandingPage.css with modern styling and animations
- [ ] Integrate landing page into App.js with scroll functionality
- [ ] Update App.css to match light green/white theme throughout
- [ ] Create .env.development and .env.production files with API URLs