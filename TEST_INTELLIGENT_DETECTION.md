# 🧪 Testing the Intelligent Detection System

## Quick Test Guide

Follow these steps to verify the new intelligent detection system is working correctly.

---

## ✅ Test 1: Normal Blinks (Should NOT Alert)

**Purpose:** Verify that normal eye blinks are detected and ignored

**Steps:**
1. Start both backend and frontend servers
2. Position your face in the camera frame (green box should appear)
3. Blink normally 5-10 times in a row
4. Watch the drowsiness score meter

**Expected Results:**
- ✅ Green box stays green
- ✅ Drowsiness score stays at 0-5%
- ✅ Status shows "Alert and monitoring"
- ✅ Console shows: `[DEBUG] Blink detected - score unchanged`
- ✅ No alert triggered

**If This Fails:**
- Check backend console - are blinks being detected?
- Verify your blink duration is < 0.4 seconds
- Improve lighting if blinks aren't being recognized

---

## ✅ Test 2: Brief Eye Closure (Should NOT Alert)

**Purpose:** Verify that opening eyes quickly prevents false alerts

**Steps:**
1. Close your eyes for 1-2 seconds
2. Notice the drowsiness score starting to rise
3. Open your eyes IMMEDIATELY when score reaches 30-40%
4. Watch the score decay

**Expected Results:**
- ✅ Score rises while eyes closed (15-40%)
- ✅ Score decays rapidly when eyes open (visible in meter)
- ✅ Console shows: `[DEBUG] Eyes opened after X.XXs - DROWSY CLOSURE`
- ✅ No alert triggered (score decays before reaching 70%)
- ✅ Box stays green

**If This Fails:**
- Check if score is decaying - should drop ~15-25% per second
- Verify EAR goes above 0.32 when eyes open (shown in console)
- If score reaches 70% too quickly, eyes may not be fully opening

---

## ✅ Test 3: Sustained Drowsiness (SHOULD Alert)

**Purpose:** Verify genuine drowsiness is detected

**Steps:**
1. Close your eyes and keep them closed
2. Count slowly: "1... 2... 3..."
3. Keep eyes closed even as score rises
4. Wait for alert (should come after 2.5-3.5 seconds)

**Expected Results:**
- ✅ Drowsiness score rises steadily: 15% → 30% → 45% → 60% → 75%
- ✅ Status changes: "Monitoring" → "Eyes getting heavy" → "Getting very drowsy"
- ✅ Console shows: `[DEBUG] Drowsiness score reached threshold - starting confirmation period`
- ✅ After 2.5 seconds at high score: `[ALERT] 🚨 DROWSINESS ALERT TRIGGERED!`
- ✅ Red box appears
- ✅ Alert sound plays
- ✅ Suggestions appear
- ✅ Video shakes

**If This Fails:**
- Check if score reaches 70% - if not, eyes may not be fully closed
- Verify confirmation time is being triggered (check console)
- Your EAR might be naturally high - use calibration mode

---

## ✅ Test 4: Recovery & Grace Period

**Purpose:** Verify grace period prevents rapid re-alerting

**Steps:**
1. Trigger an alert (Test 3)
2. Open your eyes immediately when alert sounds
3. Keep eyes open and watch the meter
4. Try closing eyes again within 3 seconds

**Expected Results:**
- ✅ Alert triggered (red box, sound, suggestions)
- ✅ Open eyes → score starts decaying
- ✅ Console shows: `[DEBUG] ✓ Recovery detected - exiting alert state`
- ✅ Grace period active for 3 seconds
- ✅ During grace period: closing eyes does NOT re-trigger alert
- ✅ After grace period and score < 20%: returns to normal monitoring
- ✅ Box turns green when fully recovered

**If This Fails:**
- Check console for grace period messages
- Verify last_alert_time is being set
- Score should decay to < 20% to exit alert state

---

## ✅ Test 5: Rapid Blinking

**Purpose:** Verify multiple blinks don't accumulate score

**Steps:**
1. Blink rapidly 10-15 times in 5 seconds
2. Watch the drowsiness score meter closely

**Expected Results:**
- ✅ Score stays at 0-5% throughout
- ✅ No score accumulation from multiple blinks
- ✅ Console shows repeated: `[DEBUG] Blink detected - score unchanged`
- ✅ No alert triggered
- ✅ Status remains "Alert and monitoring"

**If This Fails:**
- Blinks may be too slow (> 0.4s) - blink faster
- Check if lighting allows camera to track rapid blinks
- May need to adjust BLINK_DURATION_MAX parameter

---

## ✅ Test 6: Slow Eye Closure (Simulating Drowsiness)

**Purpose:** Verify detection of gradual drowsiness (most realistic scenario)

**Steps:**
1. Start with eyes wide open
2. Slowly close your eyes over 2 seconds
3. Keep them closed for 2 more seconds
4. Watch score and alert

**Expected Results:**
- ✅ Score gradually increases as eyes close
- ✅ NOT detected as blink (closure too slow)
- ✅ Status changes: "Monitoring" → "Eyes heavy" → "Getting drowsy"
- ✅ Confirmation period starts when score hits 70%
- ✅ Alert triggers after 2.5 seconds total at high score
- ✅ Console shows the full progression

**If This Fails:**
- This should be most reliable test case
- If no alert, check calibration - your alert EAR might be low
- Verify EAR drops below 0.27 when eyes closing

---

## 🎛️ Advanced Testing

### Test 7: Calibration Check

**Steps:**
1. Click "🔧 Calibrate Detection" button
2. Keep eyes WIDE OPEN for 15 seconds
3. Look at results

**Expected Results:**
- Average EAR: 0.30-0.35 (ideal)
- Min EAR: > 0.28
- Max EAR: 0.35-0.40

**Interpretation:**
- If Average < 0.30: You may need lower threshold or better lighting
- If Average 0.30-0.35: Perfect! System will work great
- If Average > 0.35: Excellent eye opening, detection very reliable

### Test 8: Lighting Conditions

**Steps:**
1. Test in normal office lighting
2. Test in bright sunlight
3. Test in dim room lighting
4. Test with backlight (window behind you)

**Expected Results:**
- Normal lighting: Best performance
- Bright light: May need to reduce brightness
- Dim light: Backend should report "Too dark" if < 50 brightness
- Backlight: Poor detection - backend may lose face

**Console Check:**
- Look for: `[DEBUG] Brightness: XXX/255`
- Optimal: 100-150
- Too dark: < 50
- Too bright: > 200

---

## 📊 Console Debug Output Examples

### Normal Operation:
```
[DEBUG] ===== Frame Analysis =====
[DEBUG] Brightness: 128.5/255
[DEBUG] Raw EAR: 0.325 | Smoothed: 0.320
[DEBUG] Eyes Closed: False | Blink: False
[DEBUG] Drowsy Score: 0.0/100 | In Grace: False
[DEBUG] Final State: Alert=False | Message='Alert' | Confidence=0%
```

### Blink Detected:
```
[DEBUG] Brightness: 130.2/255
[DEBUG] Raw EAR: 0.210 | Smoothed: 0.218
[DEBUG] Eyes Closed: True | Blink: True
[DEBUG] Blink detected - score unchanged: 0.0
[DEBUG] Drowsy Score: 0.0/100 | In Grace: False
```

### Drowsiness Building:
```
[DEBUG] Raw EAR: 0.245 | Smoothed: 0.250
[DEBUG] Eyes Closed: True | Blink: False
[DEBUG] Eyes closed (EAR: 0.250) - Score increased: 15.0/100
[DEBUG] Drowsy Score: 15.0/100 | In Grace: False
```

### Alert Triggered:
```
[DEBUG] Raw EAR: 0.220 | Smoothed: 0.225
[DEBUG] Eyes Closed: True | Blink: False
[DEBUG] Eyes closed (EAR: 0.225) - Score increased: 75.0/100
[DEBUG] Drowsy Score: 75.0/100 | In Grace: False
[ALERT] 🚨 DROWSINESS ALERT TRIGGERED! Score: 75.0/100
```

### Recovery:
```
[DEBUG] Raw EAR: 0.355 | Smoothed: 0.350
[DEBUG] Eyes Closed: False | Blink: False
[DEBUG] Eyes open (EAR: 0.350) - Score decaying: 75.0 → 56.2
[DEBUG] ✓ Recovery detected - exiting alert state
```

---

## 🐛 Troubleshooting

### Problem: Blinks Still Trigger Alerts

**Diagnosis:**
1. Check console - are blinks being detected?
2. If NO: Blinks may be too slow or lighting is poor
3. If YES but still alerting: Something is wrong with score logic

**Solutions:**
- Increase BLINK_DURATION_MAX to 0.5
- Improve lighting so camera can track fast blinks
- Check that blinks don't accumulate score in console

### Problem: Real Drowsiness Not Detected

**Diagnosis:**
1. Run calibration - what's your alert EAR?
2. Check console when drowsy - does EAR drop below 0.27?
3. If NO: Threshold is too low for you

**Solutions:**
- Lower EAR_THRESHOLD from 0.27 to 0.25 or 0.24
- Check lighting - dark conditions prevent detection
- Verify confirmation period isn't too long (reduce to 2.0s)

### Problem: Alert Won't Clear

**Diagnosis:**
1. Check console for grace period status
2. Check if score is decaying when eyes open
3. Verify EAR rises above 0.27 when eyes open

**Solutions:**
- Improve lighting so camera detects open eyes
- Check camera quality - low FPS may miss eye opening
- Manually reduce GRACE_PERIOD to 2.0 seconds

### Problem: Confidence Meter Not Showing

**Diagnosis:**
1. Check browser console for JavaScript errors
2. Verify API is returning drowsy_score field
3. Check frontend App.js for drowsyScore state

**Solutions:**
- Refresh browser page
- Clear browser cache
- Check that backend is updated with new code

---

## 📋 Quick Checklist

Before reporting issues, verify:

- [ ] Backend server is running (port 5001)
- [ ] Frontend server is running (port 3000)
- [ ] Camera permission granted
- [ ] Face detected (green box visible)
- [ ] Lighting adequate (brightness 100-150 in console)
- [ ] Calibration shows reasonable EAR (0.30+)
- [ ] Console shows debug output from backend
- [ ] Browser console shows frontend debug logs
- [ ] Confidence meter is visible and updating
- [ ] All 6 basic tests pass

---

## 🎯 Success Criteria

The system is working correctly if:

1. ✅ Normal blinks are ignored (score stays 0%)
2. ✅ Brief closures don't trigger alerts (score decays quickly)
3. ✅ Sustained drowsiness triggers alert after 2.5-3.5 seconds
4. ✅ Grace period prevents rapid re-alerting
5. ✅ Confidence meter shows accurate drowsiness level
6. ✅ Console shows blink detection working
7. ✅ No false positives during normal operation

---

## 🚀 Next Steps

After all tests pass:

1. **Use in real conditions** - Test during actual work/study session
2. **Fine-tune if needed** - Adjust parameters based on your personal needs
3. **Monitor false positive rate** - Should be < 5%
4. **Verify detection latency** - Should alert within 3-4 seconds
5. **Test edge cases** - Glasses, different lighting, head angles

---

**Need Help?**

- Check `docs/INTELLIGENT_DETECTION.md` for detailed technical info
- Review backend console output for debugging
- Use calibration mode to understand your personal EAR baseline
- Adjust parameters in `backend/api_server.py` as needed

**Report Issues With:**
- Your calibration results (average EAR)
- Console output during the issue
- Lighting conditions (brightness value)
- Which specific test failed
- Screenshots of confidence meter

---

**Last Updated:** December 2, 2025



