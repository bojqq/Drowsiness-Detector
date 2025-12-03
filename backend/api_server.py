import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import base64
import mediapipe as mp
from collections import deque
import time

app = Flask(__name__)

# Configure CORS to allow all origins (simplest approach for Netlify deployments)
# This allows any origin including localhost and all Netlify subdomains
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

print("[CORS] Configured to allow all origins (*)")

# ============================================================================
# INTELLIGENT DROWSINESS DETECTION PARAMETERS
# ============================================================================

# Eye Aspect Ratio thresholds - ADJUSTED FOR REAL DROWSINESS DETECTION
# Lower thresholds = only trigger on genuinely closed/very sleepy eyes
EAR_THRESHOLD = 0.24  # Below this = eyes truly closed/very sleepy (was 0.27)
EAR_ALERT_THRESHOLD = 0.28  # Above this = definitely alert (was 0.32)
EAR_PARTIAL_OPEN = 0.24  # Between closed and open = slightly open, don't count as drowsy

# Blink detection - to ignore normal blinks
BLINK_DURATION_MAX = 0.4  # Max duration (seconds) for normal blink
BLINK_EAR_THRESHOLD = 0.18  # Very low EAR indicates full eye closure (was 0.22)

# Drowsiness detection parameters - IMMEDIATE RESPONSE
DROWSY_SCORE_THRESHOLD = 35.0  # Score above this triggers alert (lower = faster response)
DROWSY_CONFIRMATION_TIME = 0.3  # Must maintain high score for this long (0.3s = immediate after blink filter)
GRACE_PERIOD_AFTER_ALERT = 2.0  # Recovery time after opening eyes (seconds)

# Temporal smoothing
EAR_HISTORY_SIZE = 10  # Keep last 10 EAR readings for smoothing
DROWSY_SCORE_DECAY = 0.85  # Score decay when eyes are open (0.85 = 15% decay per frame)
DROWSY_SCORE_INCREMENT = 40.0  # Score increase when eyes closed (DOUBLED for immediate detection)

# Debug mode - set to True to see detailed values in console
DEBUG_MODE = True

# ============================================================================
# GLOBAL STATE - Tracks detection state across frames
# ============================================================================

class DrowsinessState:
    """Maintains temporal state for intelligent drowsiness detection"""
    def __init__(self):
        self.ear_history = deque(maxlen=EAR_HISTORY_SIZE)
        self.drowsy_score = 0.0  # Current drowsiness score (0-100)
        self.eyes_closed_start = None  # Timestamp when eyes closed
        self.last_alert_time = None  # Last time alert was triggered
        self.is_in_alert = False  # Currently in alert state
        self.blink_detected = False  # Was last closure a blink?
        self.confirmation_start = None  # When did score exceed threshold?
        
    def reset(self):
        """Reset state (e.g., when face is lost)"""
        self.ear_history.clear()
        self.drowsy_score = 0.0
        self.eyes_closed_start = None
        self.blink_detected = False
        self.confirmation_start = None
        # Keep last_alert_time and is_in_alert for grace period

state = DrowsinessState()

mp_face_mesh = mp.solutions.face_mesh
face_mesh = None  # Initialize lazily on first request to avoid startup timeout

def get_face_mesh():
    """Lazy-load face mesh model on first use"""
    global face_mesh
    if face_mesh is None:
        face_mesh = mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=False,
            min_detection_confidence=0.3,
            min_tracking_confidence=0.3
        )
    return face_mesh

# Landmark indices for MediaPipe face mesh
LEFT_EYE_IDX = [33, 160, 158, 133, 153, 144]
RIGHT_EYE_IDX = [362, 385, 387, 263, 373, 380]


def euclidean_distance(point1, point2):
    """Calculate Euclidean distance between two points"""
    return np.linalg.norm(np.array(point1) - np.array(point2))


def landmark_to_point(landmark, width, height):
    """Convert normalized MediaPipe landmark to pixel coordinates"""
    return (int(landmark.x * width), int(landmark.y * height))


def eye_aspect_ratio_from_landmarks(landmark_list, width, height, indices):
    """Calculate EAR using MediaPipe landmark indices"""
    points = [landmark_to_point(landmark_list[idx], width, height) for idx in indices]
    A = euclidean_distance(points[1], points[5])
    B = euclidean_distance(points[2], points[4])
    C = euclidean_distance(points[0], points[3])
    if C == 0:
        return 0.0
    return (A + B) / (2.0 * C)


def calc_face_box(landmark_list, width, height):
    xs = [int(lm.x * width) for lm in landmark_list]
    ys = [int(lm.y * height) for lm in landmark_list]
    return {
        'left': max(min(xs), 0),
        'top': max(min(ys), 0),
        'right': min(max(xs), width),
        'bottom': min(max(ys), height)
    }


def get_smoothed_ear(current_ear):
    """
    Get temporally smoothed EAR value using rolling average
    This reduces noise and prevents false alerts from momentary fluctuations
    """
    state.ear_history.append(current_ear)
    
    if len(state.ear_history) < 3:
        # Not enough history yet, return current value
        return current_ear
    
    # Use weighted average: recent values matter more
    # Weights: [0.5, 0.3, 0.2] for last 3 values
    recent_ears = list(state.ear_history)[-3:]
    weights = [0.5, 0.3, 0.2]
    smoothed = sum(ear * w for ear, w in zip(reversed(recent_ears), weights))
    
    return smoothed


def detect_blink(smoothed_ear, current_time):
    """
    Detect if current eye closure is a normal blink or potential drowsiness
    Uses SMOOTHED EAR to prevent false classifications from noise
    
    EAR Ranges:
    - >= 0.28: Eyes fully open/alert (normal state)
    - 0.24-0.28: Eyes slightly smaller (OK, not drowsy - could be natural)
    - 0.21-0.24: Eyes very sleepy/barely open (borderline)
    - < 0.21: Eyes closed/very drowsy (ALERT!)
    
    Returns: (is_blink, is_eyes_closed)
    """
    # Use smoothed EAR for more reliable detection
    # Only truly closed eyes (< 0.21) count as "closed"
    is_eyes_closed = smoothed_ear < EAR_THRESHOLD
    
    # Safety check: If EAR is alert or even partially open, force eyes_open state
    if smoothed_ear >= EAR_ALERT_THRESHOLD:
        # Eyes are definitely open - clear any closure tracking
        if state.eyes_closed_start is not None:
            if DEBUG_MODE:
                closure_duration = current_time - state.eyes_closed_start
                print(f"[DEBUG] ✅ Eyes ALERT/OPEN (EAR: {smoothed_ear:.3f}) after {closure_duration:.2f}s")
            state.eyes_closed_start = None
            state.blink_detected = False
        return False, False  # Not blink, eyes are open
    
    # Partial open check: Eyes smaller than normal but NOT drowsy (0.24-0.28 range)
    if smoothed_ear >= EAR_PARTIAL_OPEN and smoothed_ear < EAR_ALERT_THRESHOLD:
        # Eyes are partially open - this is OK, could be natural eye size
        if state.eyes_closed_start is not None:
            if DEBUG_MODE:
                print(f"[DEBUG] 👁️ Eyes partially open (EAR: {smoothed_ear:.3f}) - Natural state, clearing closure")
            state.eyes_closed_start = None
            state.blink_detected = False
        return False, False  # Not drowsy, just natural smaller eyes
    
    # Track eye closure duration (only for truly closed/very sleepy eyes < 0.21)
    if is_eyes_closed:
        if state.eyes_closed_start is None:
            state.eyes_closed_start = current_time
            if DEBUG_MODE:
                print(f"[DEBUG] ⚠️ Eye closure/very sleepy detected (EAR: {smoothed_ear:.3f})")
            
        closure_duration = current_time - state.eyes_closed_start
        
        # Very low EAR and quick closure/opening = blink
        if smoothed_ear < BLINK_EAR_THRESHOLD and closure_duration < BLINK_DURATION_MAX:
            state.blink_detected = True
            return True, True  # is_blink=True, is_eyes_closed=True
    else:
        # Eyes are in the sleepy zone (0.21-0.24) but not fully closed
        if state.eyes_closed_start is not None:
            # Just opened from closure - check if it was a blink
            closure_duration = current_time - state.eyes_closed_start
            was_blink = closure_duration < BLINK_DURATION_MAX
            
            if DEBUG_MODE:
                print(f"[DEBUG] Eyes no longer closed after {closure_duration:.2f}s - {'BLINK' if was_blink else 'DROWSY CLOSURE'}")
            
            state.eyes_closed_start = None
            state.blink_detected = False
    
    return False, is_eyes_closed


def update_drowsy_score(is_eyes_closed, is_blink, smoothed_ear, current_time):
    """
    Update drowsiness score based on current eye state
    Uses exponential decay for gradual recovery and intelligent increment for closures
    Returns: (drowsy_score, is_confirmed_drowsy)
    """
    # SAFETY CHECK: If eyes are clearly wide open, score should NEVER increase
    if smoothed_ear >= EAR_ALERT_THRESHOLD:
        # Eyes are definitely open - only decay, never increase
        old_score = state.drowsy_score
        
        if state.is_in_alert:
            # In alert - decay very fast
            state.drowsy_score = max(0.0, state.drowsy_score * 0.50)
        else:
            # Normal decay
            state.drowsy_score = max(0.0, state.drowsy_score * 0.75)
        
        if DEBUG_MODE and old_score > 5:
            print(f"[DEBUG] 👁️ Eyes WIDE OPEN (EAR: {smoothed_ear:.3f}) - Score decaying: {old_score:.1f} → {state.drowsy_score:.1f}")
        
        # Reset confirmation if score drops
        if state.drowsy_score < DROWSY_SCORE_THRESHOLD and state.confirmation_start is not None:
            state.confirmation_start = None
        
        return state.drowsy_score, False
    
    # If it's just a blink, don't increase score much
    if is_blink:
        if DEBUG_MODE:
            print(f"[DEBUG] Blink detected - score unchanged: {state.drowsy_score:.1f}")
        return state.drowsy_score, False
    
    # Update score based on eye state
    if is_eyes_closed:
        # Eyes truly closed or very sleepy (EAR < 0.21) - increase score
        # Increase more if EAR is very low (deeply closed)
        increment = DROWSY_SCORE_INCREMENT
        if smoothed_ear < BLINK_EAR_THRESHOLD:
            # Deeply closed (< 0.18) - very drowsy!
            increment *= 2.0  # DOUBLE for deeply closed eyes = IMMEDIATE alert
            if DEBUG_MODE:
                print(f"[DEBUG] 🚨 Eyes DEEPLY CLOSED (EAR: {smoothed_ear:.3f}) - Score increased: {state.drowsy_score:.1f} + {increment:.1f}")
        else:
            if DEBUG_MODE:
                print(f"[DEBUG] ⚠️ Eyes very sleepy/closed (EAR: {smoothed_ear:.3f}) - Score increased: {state.drowsy_score:.1f} + {increment:.1f}")
        
        state.drowsy_score = min(100.0, state.drowsy_score + increment)
        
        if DEBUG_MODE:
            print(f"[DEBUG] → New Score: {state.drowsy_score:.1f}/100")
    else:
        # Eyes open - decay score gradually
        # Determine decay rate based on how open eyes are
        if state.is_in_alert and smoothed_ear >= EAR_ALERT_THRESHOLD:
            # Super fast decay when recovering from alert - 50% per frame!
            decay_rate = 0.50  # 50% decay per frame = very responsive
            if DEBUG_MODE:
                print(f"[DEBUG] 🚀 RAPID RECOVERY MODE - Wide awake after alert!")
        elif smoothed_ear >= EAR_ALERT_THRESHOLD:
            # Eyes fully alert (>= 0.28) - decay faster
            decay_rate = 0.70  # 30% decay per frame
        elif smoothed_ear >= EAR_PARTIAL_OPEN:
            # Eyes partially open (0.24-0.28) - moderate decay (not drowsy, just smaller eyes)
            decay_rate = 0.75  # 25% decay per frame
        else:
            # Eyes in sleepy zone (0.21-0.24) but not closed - slow decay
            decay_rate = DROWSY_SCORE_DECAY  # 15% decay per frame
        
        old_score = state.drowsy_score
        state.drowsy_score = max(0.0, state.drowsy_score * decay_rate)
        
        if DEBUG_MODE and old_score > 10:
            print(f"[DEBUG] Eyes open (EAR: {smoothed_ear:.3f}) - Score decaying: {old_score:.1f} → {state.drowsy_score:.1f}")
    
    # Check if score is high enough for drowsiness detection
    if state.drowsy_score >= DROWSY_SCORE_THRESHOLD:
        if state.confirmation_start is None:
            state.confirmation_start = current_time
            if DEBUG_MODE:
                print(f"[DEBUG] Drowsiness score reached threshold - starting confirmation period")
        
        confirmation_duration = current_time - state.confirmation_start
        
        # Must maintain high score for confirmation period
        if confirmation_duration >= DROWSY_CONFIRMATION_TIME:
            if DEBUG_MODE:
                print(f"[ALERT] DROWSINESS CONFIRMED after {confirmation_duration:.1f}s - Score: {state.drowsy_score:.1f}/100")
            return state.drowsy_score, True
    else:
        # Score dropped below threshold - reset confirmation
        if state.confirmation_start is not None:
            if DEBUG_MODE:
                print(f"[DEBUG] Score dropped below threshold - resetting confirmation")
            state.confirmation_start = None
    
    return state.drowsy_score, False


def check_grace_period(current_time):
    """
    Check if we're in grace period after an alert
    This prevents rapid re-alerting when user is recovering
    """
    if state.last_alert_time is None:
        return False
    
    time_since_alert = current_time - state.last_alert_time
    in_grace = time_since_alert < GRACE_PERIOD_AFTER_ALERT
    
    # Exit alert state if drowsy score is very low and grace period over
    if not in_grace and state.drowsy_score < 20:
        state.is_in_alert = False
    
    return in_grace

def decode_image(base64_string):
    """Decode base64 string to OpenCV image"""
    img_data = base64.b64decode(base64_string.split(',')[1])
    nparr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    original_shape = img.shape  # Store original dimensions
    # Resize to smaller dimensions for faster processing
    img = cv2.resize(img, (320, 240))
    return img, original_shape

@app.route('/detect_drowsiness', methods=['POST'])
def detect_drowsiness():
    """
    Intelligent drowsiness detection with temporal smoothing and blink detection
    """
    try:
        current_time = time.time()
        data = request.json
        image_data = data.get('image')
        
        if not image_data:
            return jsonify({'error': 'No image provided'}), 400
        
        # Decode image
        frame, original_shape = decode_image(image_data)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Calculate scaling factors for coordinate conversion
        scale_x = original_shape[1] / frame.shape[1]
        scale_y = original_shape[0] / frame.shape[0]
        
        # Check image quality (brightness)
        avg_brightness = np.mean(gray)
        if DEBUG_MODE:
            print(f"\n[DEBUG] ===== Frame Analysis =====")
            print(f"[DEBUG] Brightness: {avg_brightness:.1f}/255")
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mesh = get_face_mesh()
        results = mesh.process(rgb_frame)

        if not results.multi_face_landmarks:
            # Face lost - reset state but keep alert status for grace period
            if DEBUG_MODE:
                print(f"[DEBUG] No face detected - resetting detection state")
            
            state.reset()
            
            # Provide helpful feedback based on brightness
            if avg_brightness < 50:
                message = 'No face detected - Too dark, improve lighting'
            elif avg_brightness > 200:
                message = 'No face detected - Too bright, reduce lighting'
            else:
                message = 'No face detected - Position face in frame'
            
            return jsonify({
                'is_drowsy': state.is_in_alert,  # Keep alert if in grace period
                'message': message,
                'brightness': round(avg_brightness, 1),
                'drowsy_score': 0,
                'confidence': 0
            })
        
        # Process first detected face
        face_landmarks = results.multi_face_landmarks[0].landmark
        height, width = gray.shape

        # Calculate face box on resized image
        face_box = calc_face_box(face_landmarks, width, height)
        
        # Scale face box coordinates back to original image dimensions
        face_box = {
            'left': int(face_box['left'] * scale_x),
            'top': int(face_box['top'] * scale_y),
            'right': int(face_box['right'] * scale_x),
            'bottom': int(face_box['bottom'] * scale_y)
        }

        # Calculate EAR for both eyes
        left_ear = eye_aspect_ratio_from_landmarks(face_landmarks, width, height, LEFT_EYE_IDX)
        right_ear = eye_aspect_ratio_from_landmarks(face_landmarks, width, height, RIGHT_EYE_IDX)
        raw_ear = (left_ear + right_ear) / 2.0
        
        # Get temporally smoothed EAR
        smoothed_ear = get_smoothed_ear(raw_ear)
        
        # Detect blinks vs drowsiness
        is_blink, is_eyes_closed = detect_blink(smoothed_ear, current_time)
        
        # Update drowsiness score with intelligent logic
        drowsy_score, is_confirmed_drowsy = update_drowsy_score(
            is_eyes_closed, is_blink, smoothed_ear, current_time
        )
        
        # Check grace period
        in_grace_period = check_grace_period(current_time)
        
        if DEBUG_MODE:
            print(f"[DEBUG] Raw EAR: {raw_ear:.3f} | Smoothed: {smoothed_ear:.3f}")
            print(f"[DEBUG] Eyes Closed: {is_eyes_closed} | Blink: {is_blink}")
            print(f"[DEBUG] Drowsy Score: {drowsy_score:.1f}/100 | In Grace: {in_grace_period}")
        
        # Determine alert state
        should_alert = False
        message = 'Alert'
        confidence = int(drowsy_score)
        
        if is_confirmed_drowsy and not in_grace_period:
            # Confirmed drowsiness - trigger alert
            should_alert = True
            state.is_in_alert = True
            state.last_alert_time = current_time
            message = 'Drowsiness detected!'
            
            if DEBUG_MODE:
                print(f"[ALERT] 🚨 DROWSINESS ALERT TRIGGERED! Score: {drowsy_score:.1f}/100")
        
        elif state.is_in_alert:
            # Currently in alert state
            # Quick recovery detection: If eyes are wide open OR score drops significantly
            if smoothed_ear >= EAR_ALERT_THRESHOLD or drowsy_score < 40:
                # Immediate recovery - exit alert
                state.is_in_alert = False
                should_alert = False
                message = 'Recovered!' if drowsy_score < 20 else 'Recovering...'
                if DEBUG_MODE:
                    print(f"[DEBUG] ✓ IMMEDIATE RECOVERY - EAR: {smoothed_ear:.3f}, Score: {drowsy_score:.1f}")
            else:
                # Still in alert - eyes not fully open yet
                should_alert = True
                message = 'Wake up! Still drowsy!' if drowsy_score < 50 else 'Drowsiness detected!'
        
        elif drowsy_score > 50:
            # Warning state - getting very drowsy
            message = 'Getting very drowsy...'
        
        elif drowsy_score > 30:
            # Caution - slight drowsiness building
            message = 'Eyes getting heavy...'
        
        elif smoothed_ear < EAR_PARTIAL_OPEN:
            # Eyes in sleepy zone (0.21-0.24) but score not high yet
            message = 'Eyes look sleepy...'
        
        elif smoothed_ear < EAR_ALERT_THRESHOLD:
            # Eyes partially open (0.24-0.28) - could be natural, just monitoring
            message = 'Monitoring...'
        
        if DEBUG_MODE:
            print(f"[DEBUG] Final State: Alert={should_alert} | Message='{message}' | Confidence={confidence}%")
            print(f"[DEBUG] ========================\n")
        
        return jsonify({
            'is_drowsy': should_alert,
            'ear': round(smoothed_ear, 3),
            'raw_ear': round(raw_ear, 3),
            'message': message,
            'face_box': face_box,
            'drowsy_score': round(drowsy_score, 1),
            'confidence': confidence,
            'is_blink': is_blink,
            'in_grace_period': in_grace_period
        })
        
    except Exception as e:
        if DEBUG_MODE:
            import traceback
            print(f"[ERROR] Exception in detect_drowsiness: {str(e)}")
            traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/', methods=['GET'])
def index():
    """Root endpoint - API info"""
    return jsonify({
        'api': 'Drowsiness Detection API',
        'version': '1.0',
        'endpoints': {
            '/health': 'GET - Health check',
            '/detect_drowsiness': 'POST - Detect drowsiness from image'
        }
    })

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
