# 😴 Drowsiness Detector - Hackathon Demo

Real-time drowsiness detection using computer vision and React.

## ✨ Recent Improvements (Latest Update)

🎯 **Better Detection Accuracy**
- Increased EAR threshold (0.25 → 0.28) for more sensitive detection
- Faster response time (4.5s → 2s detection)
- Improved frame processing rate (1.5s → 1s intervals)

🔧 **New Features**
- **Calibration Mode**: Find your personal EAR baseline
- **Debug Console**: Real-time EAR values and detection status
- **Lighting Feedback**: Automatic brightness detection and suggestions
- **Visual States**: Yellow (searching) → Green (locked) → Red (drowsy)

📊 **Better Feedback**
- Face tracking box with status labels
- Intermediate warnings ("Eyes getting heavy...")
- Detailed troubleshooting guide
- Console logging for tuning

👉 **See `docs/QUICK_START.md` for testing guide**  
👉 **See `docs/DETECTION_IMPROVEMENTS.md` for detailed changes**

## Quick Start

### Backend Setup

1. Navigate to backend:
```bash
cd backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Start the server:
```bash
python api_server.py
```

### Frontend Setup

1. Navigate to frontend:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the app:
```bash
npm start
```

4. Open http://localhost:3000 and allow camera access

## How It Works

- Camera captures frames every **1 second** (improved from 1.5s)
- Backend calculates Eye Aspect Ratio (EAR) from facial landmarks
- If EAR < **0.28** for **2+ consecutive frames**, drowsiness alert triggers
- Audio alarm + visual warnings + wake-up suggestions appear
- Real-time face tracking with color-coded status (yellow/green/red)

### Detection Flow
1. **Yellow Box** - Searching for face
2. **Green Box** - Face locked, monitoring active
3. **Red Box** - Drowsiness detected, alert triggered!

## Tech Stack

- Frontend: React, Web Audio API, Canvas API
- Backend: Flask, OpenCV, MediaPipe, NumPy
- Communication: REST API with Base64 image encoding

## 🔧 Calibration & Testing

### First Time Setup
1. Start both backend and frontend servers
2. Allow camera access
3. Click **"🔧 Calibrate Detection"** button
4. Keep eyes OPEN for 15 seconds
5. Check your average EAR (should be 0.30+)

### Testing Detection
1. Look at camera normally (green box should appear)
2. Close your eyes and hold for 2-3 seconds
3. Red box and alert should trigger

### Troubleshooting

**Not detecting drowsiness?**
- Run calibration to check your baseline EAR
- Check backend console for actual EAR values
- Improve lighting (face should be well-lit from front)

**Yellow box stuck on "SCANNING"?**
- Adjust lighting (not too dark or bright)
- Face camera directly
- Ensure backend is running on port 5001

**Too many false alerts?**
- Remove glasses if possible
- Improve frontal lighting
- Keep head position stable

**See detailed debug info:**
- Backend terminal shows EAR values and detection events
- Browser console (F12) shows frame-by-frame analysis
- Use calibration mode to understand your personal EAR range

## 📚 Documentation

- `docs/QUICK_START.md` - Fast setup and testing guide
- `docs/DETECTION_IMPROVEMENTS.md` - Detailed changes and tuning guide
- `.kiro/specs/drowsiness-detector/` - Full requirements and design docs
