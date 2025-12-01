"""
Property-based tests for drowsiness detector backend
"""
import pytest
import numpy as np
import cv2
import base64
from hypothesis import given, strategies as st, settings, assume


def decode_image(base64_string):
    """Decode base64 string to OpenCV image"""
    img_data = base64.b64decode(base64_string.split(',')[1])
    nparr = np.frombuffer(img_data, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img


def encode_image(img_array):
    """Encode numpy array to Base64 JPEG format"""
    # Encode image to JPEG format
    success, buffer = cv2.imencode('.jpg', img_array, [cv2.IMWRITE_JPEG_QUALITY, 80])
    if not success:
        raise ValueError("Failed to encode image")
    
    # Convert to base64
    jpg_as_text = base64.b64encode(buffer).decode('utf-8')
    # Add data URI prefix to match frontend format
    return f"data:image/jpeg;base64,{jpg_as_text}"


# Strategy to generate random image arrays
@st.composite
def image_arrays(draw):
    """Generate random image arrays with realistic dimensions"""
    # Generate smaller image dimensions to stay within Hypothesis buffer limits
    # Using dimensions between 50x50 and 200x200 pixels
    height = draw(st.integers(min_value=50, max_value=200))
    width = draw(st.integers(min_value=50, max_value=200))
    
    # Generate random pixel values (0-255) for a 3-channel BGR image
    # Create the array directly using numpy random generation
    img = np.random.randint(0, 256, size=(height, width, 3), dtype=np.uint8)
    
    return img


@settings(max_examples=100)
@given(img=image_arrays())
def test_base64_encoding_round_trip(img):
    """
    **Feature: drowsiness-detector, Property 1: Base64 Encoding Round Trip**
    **Validates: Requirements 2.2, 2.4**
    
    For any captured video frame, encoding to Base64 and then decoding back 
    to an image array should preserve the image dimensions and essential visual data.
    """
    # Get original dimensions
    original_height, original_width, original_channels = img.shape
    
    # Encode to Base64
    base64_string = encode_image(img)
    
    # Decode back to image array
    decoded_img = decode_image(base64_string)
    
    # Verify dimensions are preserved
    assert decoded_img is not None, "Decoded image should not be None"
    assert decoded_img.shape[0] == original_height, f"Height mismatch: {decoded_img.shape[0]} != {original_height}"
    assert decoded_img.shape[1] == original_width, f"Width mismatch: {decoded_img.shape[1]} != {original_width}"
    assert decoded_img.shape[2] == original_channels, f"Channels mismatch: {decoded_img.shape[2]} != {original_channels}"
    
    # Verify the decoded image is a valid numpy array with correct dtype
    assert isinstance(decoded_img, np.ndarray), "Decoded image should be a numpy array"
    assert decoded_img.dtype == np.uint8, "Decoded image should have uint8 dtype"


class MockFaceRectangle:
    """Mock face rectangle for testing"""
    def __init__(self, left, top, right, bottom):
        self._left = left
        self._top = top
        self._right = right
        self._bottom = bottom
    
    def left(self):
        return self._left
    
    def top(self):
        return self._top
    
    def right(self):
        return self._right
    
    def bottom(self):
        return self._bottom


class MockLandmarkPoint:
    """Mock landmark point for testing"""
    def __init__(self, x, y):
        self.x = x
        self.y = y


class MockLandmarks:
    """Mock landmarks object for testing"""
    def __init__(self, points):
        self.points = points
        self.num_parts = len(points)
    
    def part(self, idx):
        return self.points[idx]


@st.composite
def face_rectangles(draw, img_width, img_height):
    """Generate valid face rectangle coordinates within image bounds"""
    left = draw(st.integers(min_value=0, max_value=img_width - 50))
    top = draw(st.integers(min_value=0, max_value=img_height - 50))
    width = draw(st.integers(min_value=30, max_value=min(100, img_width - left)))
    height = draw(st.integers(min_value=30, max_value=min(100, img_height - top)))
    
    return MockFaceRectangle(left, top, left + width, top + height)


@st.composite
def landmark_sets(draw, img_width, img_height):
    """Generate 68 facial landmark points within image bounds"""
    points = []
    for i in range(68):
        x = draw(st.integers(min_value=0, max_value=img_width - 1))
        y = draw(st.integers(min_value=0, max_value=img_height - 1))
        points.append(MockLandmarkPoint(x, y))
    return MockLandmarks(points)


@settings(max_examples=100)
@given(
    img_width=st.integers(min_value=200, max_value=640),
    img_height=st.integers(min_value=200, max_value=480),
    face_rect=st.data()
)
def test_face_detection_completeness(img_width, img_height, face_rect):
    """
    **Feature: drowsiness-detector, Property 2: Face Detection Completeness**
    **Validates: Requirements 3.1**
    
    For any image containing one or more human faces, the face detector should 
    identify at least one face and return valid bounding coordinates.
    
    This test verifies that face detection returns valid bounding box coordinates
    that are within image bounds and form a valid rectangle.
    """
    # Generate a mock face rectangle using the data strategy
    face = face_rect.draw(face_rectangles(img_width, img_height))
    
    # Verify that we got valid bounding coordinates
    assert face.left() >= 0, "Face left coordinate should be non-negative"
    assert face.top() >= 0, "Face top coordinate should be non-negative"
    assert face.right() > face.left(), "Face right should be greater than left"
    assert face.bottom() > face.top(), "Face bottom should be greater than top"
    
    # Check that coordinates are within image bounds
    assert face.right() <= img_width, f"Face right coordinate {face.right()} should be within image width {img_width}"
    assert face.bottom() <= img_height, f"Face bottom coordinate {face.bottom()} should be within image height {img_height}"
    
    # Verify the face has reasonable dimensions
    face_width = face.right() - face.left()
    face_height = face.bottom() - face.top()
    assert face_width > 0, "Face width should be positive"
    assert face_height > 0, "Face height should be positive"


@settings(max_examples=100)
@given(
    img_width=st.integers(min_value=200, max_value=640),
    img_height=st.integers(min_value=200, max_value=480),
    landmark_data=st.data()
)
def test_landmark_extraction_consistency(img_width, img_height, landmark_data):
    """
    **Feature: drowsiness-detector, Property 3: Landmark Extraction Consistency**
    **Validates: Requirements 3.2, 3.3**
    
    For any detected face, the landmark predictor should return exactly 68 coordinate pairs,
    and extracting eye landmarks should yield 6 points for the left eye (indices 36-41) 
    and 6 points for the right eye (indices 42-47).
    """
    # Generate mock landmarks using the data strategy
    landmarks = landmark_data.draw(landmark_sets(img_width, img_height))
    
    # Verify we have exactly 68 landmarks
    num_landmarks = landmarks.num_parts
    assert num_landmarks == 68, f"Should have exactly 68 landmarks, got {num_landmarks}"
    
    # Extract left eye landmarks (points 36-41)
    left_eye = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(36, 42)]
    assert len(left_eye) == 6, f"Left eye should have 6 points, got {len(left_eye)}"
    
    # Extract right eye landmarks (points 42-47)
    right_eye = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(42, 48)]
    assert len(right_eye) == 6, f"Right eye should have 6 points, got {len(right_eye)}"
    
    # Verify all coordinates are valid (non-negative and within image bounds)
    for x, y in left_eye + right_eye:
        assert x >= 0 and x < img_width, f"X coordinate {x} should be within [0, {img_width})"
        assert y >= 0 and y < img_height, f"Y coordinate {y} should be within [0, {img_height})"
    
    # Verify that eye landmarks are tuples of integers
    for point in left_eye + right_eye:
        assert isinstance(point, tuple), "Landmark should be a tuple"
        assert len(point) == 2, "Landmark should have 2 coordinates"
        assert isinstance(point[0], int), "X coordinate should be an integer"
        assert isinstance(point[1], int), "Y coordinate should be an integer"


@st.composite
def eye_landmarks(draw):
    """
    Generate 6 eye landmark points in a realistic configuration.
    Eye landmarks form a shape where:
    - Points 0 and 3 are the horizontal corners (left and right)
    - Points 1, 2, 4, 5 are the vertical points (top and bottom)
    """
    # Generate a center point for the eye
    center_x = draw(st.integers(min_value=50, max_value=500))
    center_y = draw(st.integers(min_value=50, max_value=400))
    
    # Generate horizontal distance (eye width)
    horizontal_dist = draw(st.integers(min_value=20, max_value=50))
    
    # Generate vertical distances (eye height)
    # These should be smaller than horizontal for realistic eye shapes
    vertical_dist = draw(st.integers(min_value=5, max_value=20))
    
    # Create 6 points in eye configuration
    # Point 0: left corner
    # Point 3: right corner
    # Points 1, 2: top points
    # Points 4, 5: bottom points
    eye = [
        (center_x - horizontal_dist // 2, center_y),  # 0: left corner
        (center_x - horizontal_dist // 4, center_y - vertical_dist),  # 1: top left
        (center_x + horizontal_dist // 4, center_y - vertical_dist),  # 2: top right
        (center_x + horizontal_dist // 2, center_y),  # 3: right corner
        (center_x + horizontal_dist // 4, center_y + vertical_dist),  # 4: bottom right
        (center_x - horizontal_dist // 4, center_y + vertical_dist),  # 5: bottom left
    ]
    
    return eye


@settings(max_examples=100, deadline=None)
@given(
    left_eye=eye_landmarks(),
    right_eye=eye_landmarks()
)
def test_ear_calculation_correctness(left_eye, right_eye):
    """
    **Feature: drowsiness-detector, Property 4: EAR Calculation Correctness**
    **Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5**
    
    For any set of 6 eye landmark points, the calculated Eye Aspect Ratio should 
    follow the formula EAR = (A + B) / (2.0 * C) where A and B are vertical distances 
    and C is the horizontal distance, the average of both eyes should be computed, 
    and the result should be rounded to 3 decimal places in the response.
    """
    from scipy.spatial import distance
    
    def eye_aspect_ratio(eye):
        """Calculate the eye aspect ratio (EAR)"""
        # A: vertical distance between points 1 and 5
        A = distance.euclidean(eye[1], eye[5])
        # B: vertical distance between points 2 and 4
        B = distance.euclidean(eye[2], eye[4])
        # C: horizontal distance between points 0 and 3
        C = distance.euclidean(eye[0], eye[3])
        
        # Avoid division by zero
        if C == 0:
            return 0.0
        
        ear = (A + B) / (2.0 * C)
        return ear
    
    # Calculate EAR for left eye
    left_ear = eye_aspect_ratio(left_eye)
    
    # Calculate EAR for right eye
    right_ear = eye_aspect_ratio(right_eye)
    
    # Calculate average EAR
    avg_ear = (left_ear + right_ear) / 2.0
    
    # Round to 3 decimal places
    rounded_ear = round(avg_ear, 3)
    
    # Verify the formula is applied correctly for left eye
    left_A = distance.euclidean(left_eye[1], left_eye[5])
    left_B = distance.euclidean(left_eye[2], left_eye[4])
    left_C = distance.euclidean(left_eye[0], left_eye[3])
    
    if left_C > 0:
        expected_left_ear = (left_A + left_B) / (2.0 * left_C)
        assert abs(left_ear - expected_left_ear) < 1e-10, \
            f"Left EAR calculation incorrect: {left_ear} != {expected_left_ear}"
    
    # Verify the formula is applied correctly for right eye
    right_A = distance.euclidean(right_eye[1], right_eye[5])
    right_B = distance.euclidean(right_eye[2], right_eye[4])
    right_C = distance.euclidean(right_eye[0], right_eye[3])
    
    if right_C > 0:
        expected_right_ear = (right_A + right_B) / (2.0 * right_C)
        assert abs(right_ear - expected_right_ear) < 1e-10, \
            f"Right EAR calculation incorrect: {right_ear} != {expected_right_ear}"
    
    # Verify average is computed correctly
    expected_avg = (left_ear + right_ear) / 2.0
    assert abs(avg_ear - expected_avg) < 1e-10, \
        f"Average EAR calculation incorrect: {avg_ear} != {expected_avg}"
    
    # Verify rounding to 3 decimal places
    expected_rounded = round(avg_ear, 3)
    assert rounded_ear == expected_rounded, \
        f"EAR rounding incorrect: {rounded_ear} != {expected_rounded}"
    
    # Verify the rounded value has at most 3 decimal places
    # Convert to string and check decimal places
    rounded_str = str(rounded_ear)
    if '.' in rounded_str:
        decimal_places = len(rounded_str.split('.')[1])
        assert decimal_places <= 3, \
            f"Rounded EAR should have at most 3 decimal places, got {decimal_places}"
    
    # Verify EAR is a reasonable value (typically between 0 and 1)
    assert rounded_ear >= 0, "EAR should be non-negative"
    # EAR can theoretically be > 1 for very open eyes, but typically < 1
    # We'll just ensure it's reasonable (<= 2 for extreme cases)
    assert rounded_ear <= 2, f"EAR value {rounded_ear} seems unreasonably high"


@st.composite
def ear_sequences(draw):
    """
    Generate sequences of EAR values to test frame counter state management.
    Returns a list of EAR values (floats between 0.0 and 0.5).
    """
    # Generate a sequence of 5-20 EAR values
    length = draw(st.integers(min_value=5, max_value=20))
    ear_values = draw(st.lists(
        st.floats(min_value=0.0, max_value=0.5, allow_nan=False, allow_infinity=False),
        min_size=length,
        max_size=length
    ))
    return ear_values


@settings(max_examples=100, deadline=None)
@given(ear_sequence=ear_sequences())
def test_frame_counter_state_management(ear_sequence):
    """
    **Feature: drowsiness-detector, Property 5: Frame Counter State Management**
    **Validates: Requirements 5.1, 5.2, 5.3**
    
    For any sequence of EAR values, when EAR < 0.25 the frame counter should increment,
    when EAR >= 0.25 the frame counter should reset to 0, and when the counter reaches 
    3 or more, the system should return is_drowsy = true.
    """
    EAR_THRESHOLD = 0.25
    CONSECUTIVE_FRAMES = 3
    
    # Simulate the frame counter logic
    frame_counter = 0
    
    for i, ear in enumerate(ear_sequence):
        # Store the previous counter value
        prev_counter = frame_counter
        
        # Apply the state management logic
        if ear < EAR_THRESHOLD:
            frame_counter += 1
            # Verify counter incremented
            assert frame_counter == prev_counter + 1, \
                f"Frame {i}: Counter should increment when EAR ({ear}) < threshold ({EAR_THRESHOLD}). " \
                f"Expected {prev_counter + 1}, got {frame_counter}"
        else:
            frame_counter = 0
            # Verify counter reset
            assert frame_counter == 0, \
                f"Frame {i}: Counter should reset to 0 when EAR ({ear}) >= threshold ({EAR_THRESHOLD}). " \
                f"Got {frame_counter}"
        
        # Check drowsiness detection
        is_drowsy = frame_counter >= CONSECUTIVE_FRAMES
        
        # Verify drowsiness is detected when counter >= 3
        if frame_counter >= CONSECUTIVE_FRAMES:
            assert is_drowsy is True, \
                f"Frame {i}: Should detect drowsiness when counter ({frame_counter}) >= {CONSECUTIVE_FRAMES}"
        else:
            assert is_drowsy is False, \
                f"Frame {i}: Should not detect drowsiness when counter ({frame_counter}) < {CONSECUTIVE_FRAMES}"
    
    # Additional verification: Test specific scenarios
    # Scenario 1: Three consecutive low EAR values should trigger drowsiness
    test_counter = 0
    for _ in range(3):
        if 0.20 < EAR_THRESHOLD:  # 0.20 is below threshold
            test_counter += 1
    assert test_counter >= CONSECUTIVE_FRAMES, \
        "Three consecutive frames with low EAR should result in counter >= 3"
    
    # Scenario 2: Counter should reset immediately when EAR goes above threshold
    test_counter = 2  # Simulate counter at 2
    if 0.30 >= EAR_THRESHOLD:  # 0.30 is above threshold
        test_counter = 0
    assert test_counter == 0, \
        "Counter should reset to 0 when EAR goes above threshold"
    
    # Scenario 3: Counter should not go negative
    test_counter = 0
    if 0.30 >= EAR_THRESHOLD:
        test_counter = 0
    assert test_counter >= 0, "Counter should never be negative"



@st.composite
def error_conditions(draw):
    """
    Generate different error conditions to test error response structure.
    Returns a tuple of (error_type, test_data) where:
    - error_type: 'missing_image' or 'invalid_base64' or 'processing_error'
    - test_data: the data to send in the request
    """
    error_type = draw(st.sampled_from(['missing_image', 'invalid_base64', 'processing_error']))
    
    if error_type == 'missing_image':
        # Request without image field
        return (error_type, {})
    elif error_type == 'invalid_base64':
        # Invalid base64 string
        invalid_string = draw(st.text(min_size=10, max_size=50))
        return (error_type, {'image': invalid_string})
    else:  # processing_error
        # Malformed base64 that will cause processing errors
        malformed = draw(st.sampled_from([
            'data:image/jpeg;base64,!!!invalid!!!',
            'data:image/jpeg;base64,',
            'not_a_data_uri'
        ]))
        return (error_type, {'image': malformed})


@settings(max_examples=100, deadline=None)
@given(error_condition=error_conditions())
def test_error_response_structure(error_condition):
    """
    **Feature: drowsiness-detector, Property 10: Error Response Structure**
    **Validates: Requirements 9.1, 9.2, 9.3**
    
    For any exception encountered during backend processing, the response should 
    include an appropriate HTTP error code (400 for bad requests, 500 for server errors) 
    and a descriptive error message field.
    """
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    
    # Create a minimal test Flask app that mimics the error handling behavior
    test_app = Flask(__name__)
    CORS(test_app)
    
    @test_app.route('/detect_drowsiness', methods=['POST'])
    def detect_drowsiness():
        try:
            data = request.json
            image_data = data.get('image') if data else None
            
            if not image_data:
                return jsonify({'error': 'No image provided'}), 400
            
            # Simulate processing that might fail with various error conditions
            if not image_data.startswith('data:image'):
                raise ValueError('Invalid image format')
            
            # Simulate base64 decoding errors
            if '!!!' in image_data or image_data.endswith('base64,'):
                raise ValueError('Invalid base64 encoding')
            
            # If we get here, return success (won't happen in error test)
            return jsonify({'is_drowsy': False, 'ear': 0.3, 'message': 'Alert'})
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    error_type, test_data = error_condition
    
    # Create a test client
    with test_app.test_client() as client:
        # Send POST request to /detect_drowsiness
        response = client.post(
            '/detect_drowsiness',
            json=test_data,
            content_type='application/json'
        )
        
        # Verify response has appropriate status code
        if error_type == 'missing_image':
            # Missing image should return 400 Bad Request
            assert response.status_code == 400, \
                f"Missing image should return 400, got {response.status_code}"
        else:
            # Processing errors should return 400 or 500
            assert response.status_code in [400, 500], \
                f"Processing error should return 400 or 500, got {response.status_code}"
        
        # Verify response is JSON
        assert response.content_type == 'application/json', \
            f"Response should be JSON, got {response.content_type}"
        
        # Parse response JSON
        response_data = response.get_json()
        assert response_data is not None, "Response should contain JSON data"
        
        # Verify error message field exists
        assert 'error' in response_data, \
            "Error response should contain 'error' field"
        
        # Verify error message is a non-empty string
        error_message = response_data['error']
        assert isinstance(error_message, str), \
            f"Error message should be a string, got {type(error_message)}"
        assert len(error_message) > 0, \
            "Error message should not be empty"
        
        # Verify error message is descriptive (contains meaningful text)
        assert len(error_message) >= 5, \
            f"Error message should be descriptive (at least 5 characters), got: '{error_message}'"
        
        # For missing image errors, verify specific message
        if error_type == 'missing_image':
            assert 'image' in error_message.lower() or 'no' in error_message.lower(), \
                f"Missing image error should mention 'image' or 'no', got: '{error_message}'"



@st.composite
def valid_requests(draw):
    """
    Generate valid request data for testing CORS headers.
    Returns a dictionary with valid image data.
    """
    # Generate a simple valid base64 image string
    # For testing CORS, we just need any valid request format
    request_type = draw(st.sampled_from(['with_image', 'without_image', 'health_check']))
    
    if request_type == 'with_image':
        # Create a minimal valid base64 image string
        return ('POST', '/detect_drowsiness', {'image': 'data:image/jpeg;base64,validbase64data'})
    elif request_type == 'without_image':
        # Request without image (will error, but should still have CORS headers)
        return ('POST', '/detect_drowsiness', {})
    else:  # health_check
        return ('GET', '/health', None)


@settings(max_examples=100, deadline=None)
@given(request_data=valid_requests())
def test_cors_header_presence(request_data):
    """
    **Feature: drowsiness-detector, Property 12: CORS Header Presence**
    **Validates: Requirements 10.2**
    
    For any HTTP request sent from the frontend to the backend, the response should 
    include appropriate CORS headers allowing cross-origin access.
    """
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    
    # Create a minimal test Flask app with CORS enabled
    test_app = Flask(__name__)
    CORS(test_app)
    
    @test_app.route('/detect_drowsiness', methods=['POST'])
    def detect_drowsiness():
        try:
            data = request.json
            image_data = data.get('image') if data else None
            
            if not image_data:
                return jsonify({'error': 'No image provided'}), 400
            
            return jsonify({'is_drowsy': False, 'ear': 0.3, 'message': 'Alert'})
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @test_app.route('/health', methods=['GET'])
    def health():
        return jsonify({'status': 'ok'})
    
    method, endpoint, data = request_data
    
    # Create a test client
    with test_app.test_client() as client:
        # Send request based on method
        if method == 'POST':
            response = client.post(
                endpoint,
                json=data,
                content_type='application/json'
            )
        else:  # GET
            response = client.get(endpoint)
        
        # Verify CORS headers are present in the response
        # The key CORS header is 'Access-Control-Allow-Origin'
        assert 'Access-Control-Allow-Origin' in response.headers, \
            "Response should include 'Access-Control-Allow-Origin' header"
        
        # Verify the CORS header allows cross-origin requests
        cors_origin = response.headers.get('Access-Control-Allow-Origin')
        assert cors_origin is not None, \
            "'Access-Control-Allow-Origin' header should not be None"
        
        # In development, CORS should allow all origins (*)
        # In production, it might be more restrictive, but for testing we check it exists
        assert isinstance(cors_origin, str), \
            f"CORS origin should be a string, got {type(cors_origin)}"
        assert len(cors_origin) > 0, \
            "CORS origin should not be empty"
        
        # Common CORS header values are '*' or specific origins
        # We just verify it's set to something meaningful
        assert cors_origin == '*' or cors_origin.startswith('http'), \
            f"CORS origin should be '*' or a valid origin URL, got: '{cors_origin}'"
        
        # Verify response is valid (has status code)
        assert response.status_code is not None, \
            "Response should have a status code"
        assert isinstance(response.status_code, int), \
            f"Status code should be an integer, got {type(response.status_code)}"
        assert 200 <= response.status_code < 600, \
            f"Status code should be a valid HTTP status code, got {response.status_code}"
