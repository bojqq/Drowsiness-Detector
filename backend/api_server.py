import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
import base64
import mediapipe as mp

app = Flask(__name__)

# Configure CORS to allow localhost during dev and a configurable production origin.
default_origin = 'http://localhost:3000'
frontend_origin = os.environ.get('FRONTEND_ORIGIN', default_origin)
additional_origins = os.environ.get('ADDITIONAL_ORIGINS', '')

allowed_origins = {default_origin, 'http://127.0.0.1:3000', 'https://localhost:3000', frontend_origin}
if additional_origins:
    allowed_origins.update({origin.strip() for origin in additional_origins.split(',') if origin.strip()})

CORS(app, resources={r"/*": {"origins": list(allowed_origins)}})

# Eye aspect ratio threshold - TUNED FOR BETTER DETECTION
# Increased from 0.25 to 0.28 for more sensitive drowsiness detection
# Most people have EAR around 0.3-0.35 when alert, 0.2-0.25 when drowsy
EAR_THRESHOLD = 0.28
# Reduced from 3 to 2 frames for faster detection (3 seconds instead of 4.5)
CONSECUTIVE_FRAMES = 2
frame_counter = 0

# Debug mode - set to True to see detailed EAR values in console
DEBUG_MODE = True

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
    global frame_counter
    
    try:
        data = request.json
        image_data = data.get('image')
        
        if not image_data:
            return jsonify({'error': 'No image provided'}), 400
        
        # Decode image
        frame, original_shape = decode_image(image_data)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Calculate scaling factors for coordinate conversion
        scale_x = original_shape[1] / frame.shape[1]  # original_width / resized_width
        scale_y = original_shape[0] / frame.shape[0]  # original_height / resized_height
        
        # Check image quality (brightness)
        avg_brightness = np.mean(gray)
        if DEBUG_MODE:
            print(f"[DEBUG] Image brightness: {avg_brightness:.1f}/255")
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mesh = get_face_mesh()
        results = mesh.process(rgb_frame)

        if not results.multi_face_landmarks:
            # Provide helpful feedback based on brightness
            if avg_brightness < 50:
                message = 'No face detected - Too dark, improve lighting'
            elif avg_brightness > 200:
                message = 'No face detected - Too bright, reduce lighting'
            else:
                message = 'No face detected - Position face in frame'
            
            return jsonify({
                'is_drowsy': False, 
                'message': message,
                'brightness': round(avg_brightness, 1)
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
        ear = (left_ear + right_ear) / 2.0
        
        # Debug logging to help tune thresholds
        if DEBUG_MODE:
            print(f"[DEBUG] EAR: {ear:.3f} | Left: {left_ear:.3f} | Right: {right_ear:.3f} | Counter: {frame_counter}")
        
        # Check if drowsy
        if ear < EAR_THRESHOLD:
            frame_counter += 1
            if DEBUG_MODE:
                print(f"[DEBUG] Eyes closing detected! Counter: {frame_counter}/{CONSECUTIVE_FRAMES}")
            
            if frame_counter >= CONSECUTIVE_FRAMES:
                if DEBUG_MODE:
                    print(f"[ALERT] DROWSINESS DETECTED! EAR: {ear:.3f}")
                return jsonify({
                    'is_drowsy': True,
                    'ear': round(ear, 3),
                    'message': 'Drowsiness detected!',
                    'face_box': face_box,
                    'frame_counter': frame_counter
                })
        else:
            if frame_counter > 0 and DEBUG_MODE:
                print(f"[DEBUG] Eyes opened, resetting counter from {frame_counter}")
            frame_counter = 0
        
        return jsonify({
            'is_drowsy': False,
            'ear': round(ear, 3),
            'message': 'Alert',
            'face_box': face_box,
            'frame_counter': frame_counter
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
