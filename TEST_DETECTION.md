# 🧪 Testing Your Improved Detection

## Quick Test (2 minutes)

### 1. Start Servers

**Terminal 1 - Backend:**
```bash
cd backend
python api_server.py
```
✅ Look for: `Running on http://0.0.0.0:5001`

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```
✅ Browser opens at `http://localhost:3000`

### 2. Test Face Detection

1. Allow camera access
2. **Yellow box** should appear with "SCANNING..."
3. Position your face in frame
4. **Green box** should appear with "LOCKED"

✅ **Pass**: Green box appears within 2-3 seconds  
❌ **Fail**: See troubleshooting below

### 3. Run Calibration

1. Click **"🔧 Calibrate Detection"** button
2. Keep eyes OPEN and look at camera
3. Wait 15 seconds
4. Check results:
   - Average EAR should be **0.30 or higher**
   - If below 0.30, check lighting

✅ **Pass**: Average EAR >= 0.30  
⚠️ **Warning**: Average EAR 0.25-0.30 (might be sensitive)  
❌ **Fail**: Average EAR < 0.25 (check lighting)

### 4. Test Drowsiness Detection

1. Look at camera normally (green box)
2. **Close your eyes** and hold for 3 seconds
3. Watch for:
   - EAR value drops below 0.28
   - After 2 seconds: **Red box** appears
   - Alert sound plays
   - Status shows "🚨 WAKE UP!"
   - Suggestions appear

✅ **Pass**: Red box and alert within 2-3 seconds  
❌ **Fail**: See troubleshooting below

### 5. Check Console Output

**Backend Terminal:**
```
[DEBUG] EAR: 0.325 | Left: 0.330 | Right: 0.320 | Counter: 0
[DEBUG] Eyes closing detected! Counter: 1/2
[ALERT] DROWSINESS DETECTED! EAR: 0.245
```

**Browser Console (F12):**
```
[DEBUG] EAR: 0.325 | Drowsy: false | Counter: 0
[DEBUG] EAR: 0.245 | Drowsy: true | Counter: 2
```

✅ **Pass**: See debug output in both consoles

## Troubleshooting

### Yellow Box Stuck on "SCANNING"

**Check Backend:**
```bash
# Is backend running?
curl http://localhost:5001/health
# Should return: {"status":"ok"}
```

**Check Lighting:**
- Backend shows brightness in console
- Optimal: 80-180 (out of 255)
- Too dark: < 50
- Too bright: > 200

**Fix:**
- Adjust room lighting
- Face camera directly
- Move closer/further from camera

### Not Detecting Drowsiness

**Check Your Baseline:**
1. Run calibration
2. Note your average EAR
3. If average is 0.28 or below, you need lower threshold

**Temporary Fix:**
Edit `backend/api_server.py`:
```python
EAR_THRESHOLD = 0.26  # Lower for more sensitive
```

**Check Console:**
- Watch EAR values when you close eyes
- Should drop below 0.28
- If not, lighting or face angle issue

### Too Many False Alerts

**Improve Conditions:**
- Better frontal lighting
- Remove glasses
- Keep head stable
- Adjust camera angle

**Adjust Threshold:**
Edit `backend/api_server.py`:
```python
EAR_THRESHOLD = 0.30  # Higher for less sensitive
CONSECUTIVE_FRAMES = 3  # More frames needed
```

## Expected Values

### Normal Operation
- **Alert EAR**: 0.30 - 0.35
- **Drowsy EAR**: 0.20 - 0.25
- **Detection Time**: 2 seconds
- **Frame Rate**: 1 per second

### Console Output Frequency
- Backend: Every frame (1/second)
- Frontend: Every frame (1/second)
- Brightness: Every frame

## Success Criteria

✅ Yellow → Green → Red state transitions work  
✅ Calibration shows EAR >= 0.30  
✅ Drowsiness detected within 2-3 seconds  
✅ Alert sound plays  
✅ Console shows debug output  
✅ Face box tracks face position  

## Next Steps

If all tests pass:
- ✅ Detection is working correctly!
- Use calibration to understand your baseline
- Adjust thresholds if needed for your face

If tests fail:
- See `docs/DETECTION_IMPROVEMENTS.md` for detailed tuning
- Check console output for specific issues
- Verify lighting conditions

## Need Help?

1. Check `docs/QUICK_START.md` for setup
2. Check `docs/DETECTION_IMPROVEMENTS.md` for tuning
3. Check `docs/VISUAL_GUIDE.md` for state diagrams
4. Review console output for specific errors
