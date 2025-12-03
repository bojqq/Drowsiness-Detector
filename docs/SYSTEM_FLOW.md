# 🔄 Intelligent Detection System Flow Diagram

## Visual Overview of How The System Works

---

## 📹 Frame Processing Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                     FRAME CAPTURED (1 sec)                  │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              MediaPipe Face Mesh Detection                  │
│  • Detects 468 facial landmarks                            │
│  • Focuses on eye landmarks (6 per eye)                    │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  Calculate Raw EAR                          │
│  Left Eye:  EAR_L = (vertical1 + vertical2) / (2 * horizontal)│
│  Right Eye: EAR_R = (vertical1 + vertical2) / (2 * horizontal)│
│  Average:   EAR = (EAR_L + EAR_R) / 2                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              Temporal Smoothing (NEW!)                      │
│  • Add to history: [EAR_1, EAR_2, ..., EAR_10]            │
│  • Weighted average: 0.5×recent + 0.3×middle + 0.2×old    │
│  • Smoothed EAR reduces noise                              │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              Blink Detection (NEW!)                         │
│                                                             │
│  IF smoothed_ear < 0.27:                                   │
│    ├─ Track closure duration                               │
│    │                                                        │
│    ├─ IF duration < 0.4s AND ear < 0.22:                  │
│    │   └─> BLINK DETECTED ✓                               │
│    │       • Skip score update                             │
│    │       • Continue monitoring                           │
│    │                                                        │
│    └─ ELSE:                                                │
│        └─> DROWSY CLOSURE                                  │
│            • Continue to score update                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│            Drowsiness Score Update (NEW!)                   │
│                                                             │
│  IF blink detected:                                         │
│    └─> Score unchanged                                     │
│                                                             │
│  ELSE IF eyes closed (EAR < 0.27):                         │
│    ├─ IF deeply closed (EAR < 0.22):                      │
│    │   └─> Score += 22.5 points                           │
│    └─ ELSE:                                                │
│        └─> Score += 15 points                             │
│                                                             │
│  ELSE (eyes open):                                          │
│    ├─ IF wide open (EAR > 0.32):                          │
│    │   └─> Score *= 0.75  (25% decay)                     │
│    └─ ELSE:                                                │
│        └─> Score *= 0.85  (15% decay)                     │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│            Confirmation Logic (NEW!)                        │
│                                                             │
│  IF score >= 70%:                                           │
│    ├─ IF confirmation_start is None:                       │
│    │   └─> Start confirmation timer                        │
│    │                                                        │
│    ├─ IF confirmed for 2.5+ seconds:                       │
│    │   └─> TRIGGER ALERT! 🚨                              │
│    │                                                        │
│    └─ ELSE:                                                │
│        └─> Wait for confirmation...                        │
│                                                             │
│  ELSE (score < 70%):                                        │
│    └─> Reset confirmation timer                            │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              Grace Period Check (NEW!)                      │
│                                                             │
│  IF alert was triggered:                                    │
│    ├─ IF time_since_alert < 3.0s:                         │
│    │   └─> IN GRACE PERIOD                                │
│    │       • Don't trigger new alerts                      │
│    │       • Allow recovery                                │
│    │                                                        │
│    └─ ELSE IF score < 20%:                                 │
│        └─> EXIT ALERT STATE                                │
│            • Resume normal monitoring                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  Send Response to Frontend                  │
│  {                                                          │
│    is_drowsy: boolean,                                      │
│    ear: float (smoothed),                                   │
│    raw_ear: float,                                          │
│    drowsy_score: 0-100,                                     │
│    confidence: int,                                         │
│    message: string,                                         │
│    is_blink: boolean,                                       │
│    in_grace_period: boolean                                 │
│  }                                                          │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              Frontend Visual Update                         │
│  • Update confidence meter (0-100% bar)                    │
│  • Update face box color (Yellow/Green/Red)                │
│  • Update status message                                    │
│  • Play alert sound if triggered                           │
│  • Show suggestions if drowsy                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Score Evolution Examples

### Example 1: Normal Blink (Score Stays 0)

```
Time:  0s    0.3s   0.6s   0.9s   1.2s   1.5s
       │     │      │      │      │      │
Eyes:  OPEN  BLINK OPEN   OPEN   BLINK  OPEN
       │     │      │      │      │      │
EAR:   0.35  0.20  0.35   0.35   0.20   0.35
       │     │      │      │      │      │
Score: 0%    0%    0%     0%     0%     0%
       │     │      │      │      │      │
State: ✅    🔍    ✅     ✅     🔍    ✅
      Safe  Blink  Safe   Safe   Blink  Safe
```

**Result:** No false alerts, blinks ignored ✓

---

### Example 2: Brief Closure with Quick Recovery (No Alert)

```
Time:  0s    1s    2s    3s    4s    5s    6s
       │     │     │     │     │     │     │
Eyes:  OPEN  CLOSE CLOSE OPEN  OPEN  OPEN  OPEN
       │     │     │     │     │     │     │
EAR:   0.35  0.24  0.22  0.36  0.36  0.36  0.36
       │     │     │     │     │     │     │
Score: 0%    15%   30%   22%   17%   13%   10%
       │     │     │     │     │     │     │
Meter: ▓░░░  ▓▓░░  ▓▓▓░  ▓▓░░  ▓▓░░  ▓░░░  ▓░░░
       │     │     │     │     │     │     │
State: ✅    ⚠️    ⚠️    ✅    ✅    ✅    ✅
      Safe  Caution Caution Safe  Safe  Safe  Safe
```

**Result:** Score rises then naturally decays, no alert ✓

---

### Example 3: Sustained Drowsiness (Alert Triggered)

```
Time:  0s    1s    2s    3s    4s    5s    6s
       │     │     │     │     │     │     │
Eyes:  OPEN  CLOSE CLOSE CLOSE CLOSE CLOSE CLOSE
       │     │     │     │     │     │     │
EAR:   0.35  0.24  0.22  0.21  0.20  0.19  0.19
       │     │     │     │     │     │     │
Score: 0%    15%   30%   45%   60%   75%   90%
       │     │     │     │     │     │     │
Meter: ░░░░  ▓▓░░  ▓▓▓░  ▓▓▓▓▓ ▓▓▓▓▓ ▓▓▓▓▓ ▓▓▓▓▓
       │     │     │     │     │     │     │
State: ✅    ⚠️    ⚠️    🟠    🟠    🚨    🚨
      Safe  Caution Caution Warn  Warn  ALERT! ALERT!
       │     │     │     │     │     │
Conf:  -     -     -     -     ⏱️0s  ⏱️1s  ⏱️2s → TRIGGER!
```

**Result:** Confirmed drowsiness after 2.5s, alert triggered ✓

---

### Example 4: Recovery with Grace Period

```
Time:  0s    1s    2s    3s    4s    5s    6s    7s
       │     │     │     │     │     │     │     │
Eyes:  CLOSE CLOSE CLOSE OPEN  OPEN  CLOSE CLOSE OPEN
       │     │     │     │     │     │     │     │
Score: 60%   75%   90%   68%   51%   66%   66%   50%
       │     │     │     │     │     │     │     │
Alert: No    No    YES!  YES   YES   YES   YES   No
       │     │     │     │     │     │     │     │
Grace: -     -     Start 1s    2s    3s    End   -
       │     │     │     │     │     │     │     │
State: 🟠    🚨    🚨    🚨    🚨    🚨    🚨    🟠
      Warn  TRIG  ALERT ALERT ALERT ALERT ALERT Warn
```

**Explanation:**
- Frame 2: Alert triggered
- Frame 3-5: Grace period active (3 seconds)
- Frame 5: Try to close again, but grace prevents re-alert
- Frame 6: Grace period ends
- Frame 7: Score < 70%, returns to normal monitoring

**Result:** Grace period prevents harassment during recovery ✓

---

## 🎯 State Machine Diagram

```
                    ┌──────────────┐
                    │   STARTUP    │
                    │  (Searching) │
                    └──────┬───────┘
                           │
                   Face Detected
                           │
                           ▼
                    ┌──────────────┐
         ┌─────────►│   MONITORING │◄─────────┐
         │          │    (Green)   │          │
         │          └──────┬───────┘          │
         │                 │                   │
         │         Score < 40%                 │
         │                 │                   │
         │                 ▼                   │
         │          ┌──────────────┐          │
         │          │   CAUTION    │          │
    Score < 20%     │   (Yellow)   │    Eyes Open
         │          └──────┬───────┘    Fast Decay
         │                 │                   │
         │         Score 40-70%                │
         │                 │                   │
         │                 ▼                   │
         │          ┌──────────────┐          │
         │          │   WARNING    │          │
         │          │   (Orange)   │          │
         │          └──────┬───────┘          │
         │                 │                   │
         │         Score >= 70%                │
         │         Hold 2.5s                   │
         │                 │                   │
         │                 ▼                   │
         │          ┌──────────────┐          │
         │          │  CONFIRMING  │          │
         │          │   (Orange)   │──────────┘
         │          └──────┬───────┘   Score < 70%
         │                 │
         │         Confirmed!
         │                 │
         │                 ▼
         │          ┌──────────────┐
         │          │  ALERT MODE  │
         └──────────┤     (Red)    │
    Recovery        └──────┬───────┘
    Complete               │
    (Grace + Low Score)    │
                           │
                    3s Grace Period
                    Score decaying
                           │
                           │
                      (loops back)
```

---

## 🧮 Mathematical Model

### EAR Calculation
```
         vertical_dist_1 + vertical_dist_2
EAR = ──────────────────────────────────────
              2 × horizontal_dist

Where:
  vertical_dist_1 = distance between top and bottom of eye (inner)
  vertical_dist_2 = distance between top and bottom of eye (outer)
  horizontal_dist = distance between left and right corners of eye
```

### Smoothed EAR
```
smoothed_ear = 0.5 × ear[t] + 0.3 × ear[t-1] + 0.2 × ear[t-2]

Where:
  ear[t] = current frame EAR
  ear[t-1] = previous frame EAR
  ear[t-2] = two frames ago EAR
```

### Score Update Function
```python
def update_score(current_score, eyes_closed, ear):
    if is_blink(ear):
        return current_score  # No change
    
    elif eyes_closed:
        if ear < 0.22:  # Deeply closed
            increment = 22.5
        else:
            increment = 15.0
        return min(100.0, current_score + increment)
    
    else:  # Eyes open
        if ear > 0.32:  # Wide awake
            decay = 0.75
        else:  # Partially open
            decay = 0.85
        return max(0.0, current_score * decay)
```

### Confirmation Logic
```python
def should_alert(score, confirmation_start, current_time, in_grace):
    if in_grace:
        return False  # Grace period active
    
    if score >= 70:
        if confirmation_start is None:
            confirmation_start = current_time
            return False
        
        duration = current_time - confirmation_start
        if duration >= 2.5:  # seconds
            return True
    else:
        confirmation_start = None
        return False
```

---

## 🎨 UI State Visual Guide

```
┌────────────────────────────────────────────────────────┐
│  😴 Drowsiness Detector                                │
├────────────────────────────────────────────────────────┤
│                                                        │
│  ┌──────────────────────────────────────────────┐    │
│  │                                              │    │
│  │           [VIDEO FEED]                       │    │
│  │                                              │    │
│  │    ┌─────────────────────┐                  │    │
│  │    │  FACE BOX           │  ◄─── Color indicates state │
│  │    │  • Yellow = Searching │                │    │
│  │    │  • Green  = Monitoring│                │    │
│  │    │  • Red    = Alert!   │                 │    │
│  │    └─────────────────────┘                  │    │
│  │                                              │    │
│  └──────────────────────────────────────────────┘    │
│                                                        │
│  ┌──────────────────────────────────────────────┐    │
│  │  Status: ✅ Alert and monitoring             │    │
│  │  EAR: 0.325                                  │    │
│  │                                              │    │
│  │  Drowsiness Level          0%               │    │
│  │  ▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░   │    │
│  │   Safe  Caution  Warning  Critical          │    │
│  └──────────────────────────────────────────────┘    │
│                                                        │
│  [🔧 Calibrate Detection]                            │
│                                                        │
└────────────────────────────────────────────────────────┘

           Score: 0-20%     Score: 20-40%
          ┌──────────┐     ┌──────────┐
          │  SAFE    │     │ CAUTION  │
          │  ▓▓░░░   │     │ ▓▓▓▓░░   │
          │  Green   │     │  Yellow  │
          └──────────┘     └──────────┘

        Score: 40-70%      Score: 70-100%
       ┌──────────┐       ┌──────────┐
       │ WARNING  │       │ CRITICAL │
       │ ▓▓▓▓▓▓░░ │       │ ▓▓▓▓▓▓▓▓ │
       │  Orange  │       │   Red    │
       └──────────┘       └──────────┘
```

---

## 🔍 Debug Console Output Flow

```
[Frame N]
   │
   ├─ [DEBUG] ===== Frame Analysis =====
   ├─ [DEBUG] Brightness: 128.5/255
   │
   ├─ [DEBUG] Raw EAR: 0.325 | Smoothed: 0.320
   ├─ [DEBUG] Eyes Closed: False | Blink: False
   │
   ├─ [DEBUG] Drowsy Score: 0.0/100 | In Grace: False
   └─ [DEBUG] Final State: Alert=False | Message='Alert' | Confidence=0%
   
[Frame N+1] (Eyes closing)
   │
   ├─ [DEBUG] Raw EAR: 0.245 | Smoothed: 0.250
   ├─ [DEBUG] Eyes Closed: True | Blink: False
   │
   ├─ [DEBUG] Eyes closed (EAR: 0.250) - Score increased: 15.0/100
   └─ [DEBUG] Drowsy Score: 15.0/100 | In Grace: False

[Frame N+2] (Blink detected)
   │
   ├─ [DEBUG] Raw EAR: 0.210 | Smoothed: 0.215
   ├─ [DEBUG] Eyes Closed: True | Blink: True
   │
   ├─ [DEBUG] Blink detected - score unchanged: 15.0
   └─ [DEBUG] Drowsy Score: 15.0/100 | In Grace: False

[Frame N+3] (Score building)
   │
   ├─ [DEBUG] Raw EAR: 0.220 | Smoothed: 0.225
   ├─ [DEBUG] Eyes Closed: True | Blink: False
   │
   ├─ [DEBUG] Eyes closed (EAR: 0.225) - Score increased: 30.0/100
   └─ [DEBUG] Drowsy Score: 30.0/100 | In Grace: False

... (score continues building) ...

[Frame N+K] (Alert triggered)
   │
   ├─ [DEBUG] Raw EAR: 0.220 | Smoothed: 0.225
   ├─ [DEBUG] Eyes closed (EAR: 0.225) - Score increased: 75.0/100
   │
   ├─ [ALERT] 🚨 DROWSINESS ALERT TRIGGERED! Score: 75.0/100
   └─ [DEBUG] Final State: Alert=True | Message='Drowsiness detected!' | Confidence=75%
```

---

## Summary

This flow diagram shows how the intelligent detection system:

1. ✅ **Processes each frame** through multiple intelligent stages
2. ✅ **Smooths temporal noise** with weighted averaging
3. ✅ **Detects and filters blinks** automatically
4. ✅ **Maintains drowsiness score** with gradual decay
5. ✅ **Confirms alerts** before triggering
6. ✅ **Provides grace periods** for recovery
7. ✅ **Visualizes state** clearly to user

All working together to create a **reliable, intelligent, production-ready drowsiness detection system**! 🎉

---

**Last Updated:** December 2, 2025

