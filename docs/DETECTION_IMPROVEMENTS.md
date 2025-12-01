# Drowsiness Detection Improvements & Debugging Guide

## 🎯 What Was Fixed

### 1. **Threshold Tuning**
- **EAR Threshold**: Increased from `0.25` → `0.28`
  - Most people have EAR around 0.3-0.35 when alert
  - Drowsy EAR is typically 0.2-0.25
  - New threshold catches drowsiness earlier
  
- **Consecutive Frames**: Reduced from `3` → `2` frames
  - Faster detection: 2 seconds instead of 4.5 seconds
  - More responsive to eye closure

### 2. **Frame Processing Rate**
- **Capture Interval**: Reduced from `1500ms` → `1000ms`
  - Faster frame analysis
  - Better real-time tracking
  - Combined with 2-frame threshold = 2 second detection

### 3. **Lighting Conditions**
- Added **brightness detection** in backend
- Provides helpful feedback:
  - "Too dark, improve lighting" (brightness < 50)
  - "Too bright, reduce lighting" (brightness > 200)
  - "Position face in frame" (normal lighting)

### 4. **Debug Mode**
- Backend now logs detailed information:
  ```
  [DEBUG] EAR: 0.285 | Left: 0.290 | Right: 0.280 | Counter: 0
  [DEBUG] Eyes closing detected! Counter: 1/2
  [ALERT] DROWSINESS DETECTED! EAR: 0.245
  ```
- Frontend logs detection results to console
- Helps you tune thresholds for your specific face

### 5. **Calibration Mode** ✨ NEW
- Click "🔧 Calibrate Detection" button
- Keep eyes open for 10-15 seconds
- Shows your personal EAR range:
  - Average EAR when alert
  - Min/Max values
  - Recommendations if values are unusual

### 6. **Better Visual Feedback**
- Yellow box: "SCANNING..." (searching for face)
- Green box: "LOCKED" (face detected, monitoring)
- Red box: "⚠️ WAKE UP!" (drowsiness detected)
- Status shows intermediate states: "Eyes getting heavy..."

## 🔧 How to Use

### First Time Setup
1. Start the app and allow camera access
2. Wait for **yellow box** to appear (searching)
3. Position your face in frame until **green box** appears (locked)
4. Click **"🔧 Calibrate Detection"**
5. Keep eyes OPEN and look at camera for 15 seconds
6. Check your average EAR value:
   - **0.30-0.35**: Perfect! Detection will work well
   - **0.25-0.30**: Okay, but might be sensitive
   - **Below 0.25**: Check lighting and camera angle

### Testing Detection
1. Once calibrated, look at the camera normally
2. Close your eyes slowly and hold for 2-3 seconds
3. You should see:
   - EAR value drop below 0.28
   - Counter increment in console
   - Red box appear after 2 seconds
   - Alert sound play

### Troubleshooting

#### "Not detecting when I'm drowsy"
- **Check your baseline EAR**: Use calibration mode
- **If your alert EAR is below 0.30**: You might need a lower threshold
- **Solution**: Check backend console for your actual EAR values when drowsy

#### "Too many false alerts"
- **Improve lighting**: Face should be well-lit from front
- **Remove glasses**: Can interfere with landmark detection
- **Stable position**: Keep head relatively still
- **Check brightness**: Backend logs brightness value

#### "Yellow box stuck on SCANNING"
- **Lighting issue**: Too dark or too bright
- **Face position**: Look directly at camera
- **Distance**: Move closer or further from camera
- **Backend running**: Check if backend server is active

#### "Detection is slow"
- **Check console**: Backend should respond in < 2 seconds
- **Network**: Ensure backend is on localhost:5001
- **Processing**: MediaPipe face mesh might be throttled on low-power hardware

## 📊 Understanding EAR Values

### Typical EAR Ranges
- **0.35-0.40**: Eyes wide open
- **0.30-0.35**: Normal alert state ✅
- **0.25-0.30**: Getting tired ⚠️
- **0.20-0.25**: Drowsy 🚨
- **Below 0.20**: Eyes nearly closed

### Your Personal Range
Everyone's face is different! Use calibration to find YOUR range:
1. Calibrate when fully alert
2. Note your average (should be 0.30+)
3. If below 0.30, you may need custom threshold

## 🎛️ Advanced Tuning

### Backend (`backend/api_server.py`)

```python
# Adjust these values based on your needs:
EAR_THRESHOLD = 0.28      # Lower = more sensitive (try 0.26-0.30)
CONSECUTIVE_FRAMES = 2    # Higher = less false alerts (try 2-4)
DEBUG_MODE = True         # Set False to reduce console output
```

### Frontend (`frontend/src/App.js`)

```javascript
// Adjust capture interval:
setInterval(() => {
  captureAndSend();
}, 1000);  // Lower = faster detection (try 800-1500ms)
```

## 🧪 Testing Checklist

- [ ] Yellow box appears when starting
- [ ] Green box appears when face detected
- [ ] EAR value displays and updates
- [ ] Calibration shows reasonable values (0.30+)
- [ ] Closing eyes for 2-3 seconds triggers red box
- [ ] Alert sound plays when drowsy
- [ ] Suggestions appear when drowsy
- [ ] Console shows debug information
- [ ] Backend logs EAR values

## 📝 Debug Console Output

### Backend Console (Terminal)
```
[DEBUG] Image brightness: 128.5/255
[DEBUG] EAR: 0.325 | Left: 0.330 | Right: 0.320 | Counter: 0
[DEBUG] EAR: 0.265 | Left: 0.270 | Right: 0.260 | Counter: 0
[DEBUG] Eyes closing detected! Counter: 1/2
[DEBUG] EAR: 0.245 | Left: 0.250 | Right: 0.240 | Counter: 1
[DEBUG] Eyes closing detected! Counter: 2/2
[ALERT] DROWSINESS DETECTED! EAR: 0.245
```

### Frontend Console (Browser)
```
[DEBUG] EAR: 0.325 | Drowsy: false | Counter: 0
[DEBUG] EAR: 0.265 | Drowsy: false | Counter: 1
[DEBUG] EAR: 0.245 | Drowsy: true | Counter: 2
```

## 🎯 Expected Behavior

1. **Startup** (0-2 seconds)
   - Yellow box with "SCANNING..."
   - Status: "Searching for face..."

2. **Face Detected** (2+ seconds)
   - Green box with "LOCKED"
   - Status: "Face Locked - Alert and monitoring"
   - EAR value displayed (should be 0.30+)

3. **Eyes Closing** (1-2 seconds)
   - Green box remains
   - Status: "Eyes getting heavy..."
   - EAR drops below 0.28
   - Counter increments in console

4. **Drowsiness Detected** (2 seconds of closed eyes)
   - Red box with "⚠️ WAKE UP!"
   - Status: "🚨 WAKE UP! DROWSINESS DETECTED!"
   - Alert sound plays
   - Suggestions appear
   - Video container shakes

5. **Eyes Open Again**
   - Returns to green box
   - Counter resets
   - Suggestions disappear

## 🚀 Next Steps

1. **Test the improvements**: Start both servers and test detection
2. **Run calibration**: Find your personal EAR baseline
3. **Check debug output**: Monitor console for EAR values
4. **Fine-tune if needed**: Adjust thresholds based on your results
5. **Report back**: Let me know if detection works better!

## 💡 Pro Tips

- **Best lighting**: Soft, frontal lighting (not from behind)
- **Camera angle**: Eye level, looking straight at camera
- **Distance**: 1-2 feet from camera works best
- **Glasses**: Remove if possible for better detection
- **Testing**: Close eyes slowly and hold for 3 seconds
- **Calibration**: Do it in your typical working conditions

---

**Need more help?** Check the debug panel in the app or review console output for specific issues.
