# 🚀 Quick Start Guide - Improved Drowsiness Detection

## What Was Fixed

Your drowsiness detection now has:

✅ **Better sensitivity** - EAR threshold increased from 0.25 → 0.28  
✅ **Faster detection** - 2 seconds instead of 4.5 seconds  
✅ **Lighting feedback** - Tells you if it's too dark/bright  
✅ **Debug mode** - See real-time EAR values in console  
✅ **Calibration tool** - Find your personal EAR baseline  
✅ **Better visual feedback** - Yellow → Green → Red states  

## How to Start

### 1. Start Backend (Terminal 1)
```bash
cd backend
python api_server.py
```

You should see:
```
[DEBUG] mode enabled
* Running on http://0.0.0.0:5001
```

### 2. Start Frontend (Terminal 2)
```bash
cd frontend
npm start
```

Browser opens at `http://localhost:3000`

### 3. Test Detection

1. **Allow camera** - Yellow box appears "SCANNING..."
2. **Position face** - Green box appears "LOCKED"
3. **Click "🔧 Calibrate Detection"**
4. **Keep eyes open** for 15 seconds
5. **Check your EAR** - Should be 0.30 or higher
6. **Test drowsiness** - Close eyes for 3 seconds
7. **Red box appears** - "⚠️ WAKE UP!"

## Debug Console

### Backend Terminal
Watch for:
```
[DEBUG] EAR: 0.325 | Left: 0.330 | Right: 0.320 | Counter: 0
[DEBUG] Eyes closing detected! Counter: 1/2
[ALERT] DROWSINESS DETECTED! EAR: 0.245
```

### Browser Console (F12)
Watch for:
```
[DEBUG] EAR: 0.325 | Drowsy: false | Counter: 0
[DEBUG] EAR: 0.245 | Drowsy: true | Counter: 2
```

## Troubleshooting

### "Not detecting drowsiness"
- Run calibration - check if your alert EAR is below 0.30
- Improve lighting - face should be well-lit
- Check console - see actual EAR values when you close eyes

### "Yellow box stuck"
- Too dark/bright - adjust lighting
- Face camera directly
- Check backend is running on port 5001

### "Too many false alerts"
- Remove glasses if possible
- Improve frontal lighting
- Keep head stable

## Need More Help?

See `DETECTION_IMPROVEMENTS.md` for detailed tuning guide.

---

**Key Settings Changed:**
- EAR Threshold: 0.25 → 0.28 (more sensitive)
- Consecutive Frames: 3 → 2 (faster)
- Capture Interval: 1500ms → 1000ms (faster)
- Debug Mode: Enabled (see console output)
