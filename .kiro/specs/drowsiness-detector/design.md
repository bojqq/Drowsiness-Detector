# Design Document

## Overview

The Drowsiness Detector is a real-time monitoring system that uses computer vision to detect signs of user fatigue and provide immediate alerts. The system employs a client-server architecture where a React-based frontend handles user interaction and video capture, while a Python-based backend performs intensive computer vision processing using dlib and OpenCV.

The core detection mechanism relies on calculating the Eye Aspect Ratio (EAR), a geometric metric derived from facial landmark positions that quantifies eye closure. When the EAR falls below a threshold (0.25) for consecutive frames (3+), the system triggers multi-modal alerts including visual indicators, auditory signals, and actionable suggestions.

## Architecture

### System Architecture

The application follows a two-tier client-server architecture with clear separation of concerns:

```
┌─────────────────────────────────────┐
│         React Frontend              │
│  ┌──────────────────────────────┐  │
│  │  Camera Capture Module       │  │
│  │  - getUserMedia API          │  │
│  │  - Canvas-based frame capture│  │
│  └──────────────────────────────┘  │
│  ┌──────────────────────────────┐  │
│  │  Alert System                │  │
│  │  - Visual alerts (CSS)       │  │
│  │  - Audio alerts (Web Audio)  │  │
│  │  - Suggestion display        │  │
│  └──────────────────────────────┘  │
│  ┌──────────────────────────────┐  │
│  │  API Client                  │  │
│  │  - Base64 encoding           │  │
│  │  - HTTP POST requests        │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
              │
              │ HTTP/JSON
              │ (Base64 images)
              ▼
┌─────────────────────────────────────┐
│         Python Backend              │
│  ┌──────────────────────────────┐  │
│  │  Flask API Server            │  │
│  │  - CORS enabled              │  │
│  │  - /detect_drowsiness        │  │
│  │  - /health                   │  │
│  └──────────────────────────────┘  │
│  ┌──────────────────────────────┐  │
│  │  Image Processing Pipeline   │  │
│  │  - Base64 decoder            │  │
│  │  - Grayscale conversion      │  │
│  └──────────────────────────────┘  │
│  ┌──────────────────────────────┐  │
│  │  Computer Vision Engine      │  │
│  │  - dlib face detector        │  │
│  │  - 68-point landmark model   │  │
│  │  - EAR calculator            │  │
│  └──────────────────────────────┘  │
│  ┌──────────────────────────────┐  │
│  │  State Management            │  │
│  │  - Frame counter             │  │
│  │  - Threshold configuration   │  │
│  └──────────────────────────────┘  │
└─────────────────────────────────────┘
```

### Communication Flow

1. **Frame Capture**: Frontend captures video frame every 1.5 seconds using Canvas API
2. **Encoding**: Frame is converted to Base64 JPEG format (80% quality)
3. **Transmission**: Base64 string sent via HTTP POST to `/detect_drowsiness` endpoint
4. **Decoding**: Backend decodes Base64 to NumPy array
5. **Processing**: Image processed through face detection → landmark detection → EAR calculation
6. **Response**: JSON response with `is_drowsy`, `ear`, and `message` fields
7. **Action**: Frontend updates UI and triggers alerts based on response

## Components and Interfaces

### Frontend Components

#### App Component (React)
Main application component managing state and orchestrating all frontend functionality.

**State:**
- `isDrowsy: boolean` - Current drowsiness status
- `status: string` - Display message for user
- `ear: number | null` - Current Eye Aspect Ratio value
- `cameraActive: boolean` - Camera initialization status

**Refs:**
- `videoRef` - Reference to video element displaying camera feed
- `canvasRef` - Hidden canvas for frame capture
- `audioContextRef` - Web Audio API context for alert sounds

**Methods:**
- `startCamera()` - Initializes camera access via getUserMedia
- `startDetection()` - Begins periodic frame capture (1.5s interval)
- `captureAndSend()` - Captures frame, encodes to Base64, sends to backend
- `playAlert()` - Generates and plays 800Hz sine wave alert tone

#### Camera Capture Module
Handles video stream acquisition and frame extraction.

**Interface:**
```javascript
interface CameraCapture {
  startCamera(): Promise<void>
  captureFrame(): string  // Returns Base64 encoded JPEG
  stopCamera(): void
  isActive(): boolean
}
```

#### Alert System Module
Manages visual and auditory alert presentation.

**Interface:**
```javascript
interface AlertSystem {
  showVisualAlert(): void
  hideVisualAlert(): void
  playAudioAlert(): void
  displaySuggestions(suggestions: string[]): void
  hideSuggestions(): void
}
```

### Backend Components

#### Flask API Server
RESTful API server handling drowsiness detection requests.

**Endpoints:**

`POST /detect_drowsiness`
- **Input**: `{ image: string }` (Base64 encoded image)
- **Output**: `{ is_drowsy: boolean, ear: number, message: string }`
- **Errors**: 400 (missing image), 500 (processing error)

`GET /health`
- **Output**: `{ status: string }`
- **Purpose**: Health check endpoint

#### Image Processing Pipeline

**Interface:**
```python
def decode_image(base64_string: str) -> np.ndarray:
    """Decode Base64 string to OpenCV image array"""
    pass

def preprocess_image(image: np.ndarray) -> np.ndarray:
    """Convert to grayscale for face detection"""
    pass
```

#### Computer Vision Engine

**Face Detection:**
```python
detector: dlib.fhog_object_detector
# Detects faces in grayscale images
# Returns list of rectangle objects
```

**Landmark Prediction:**
```python
predictor: dlib.shape_predictor
# Requires: shape_predictor_68_face_landmarks.dat model file
# Returns 68 (x, y) coordinate pairs for facial features
```

**EAR Calculation:**
```python
def eye_aspect_ratio(eye: List[Tuple[int, int]]) -> float:
    """
    Calculate Eye Aspect Ratio from 6 eye landmark points
    
    Formula: EAR = (||p2 - p6|| + ||p3 - p5||) / (2 * ||p1 - p4||)
    
    Where:
    - p1, p4 are horizontal eye corners
    - p2, p3, p5, p6 are vertical eye points
    """
    pass
```

#### State Management

**Global State:**
- `frame_counter: int` - Tracks consecutive frames with low EAR
- `EAR_THRESHOLD: float = 0.25` - Threshold for drowsiness detection
- `CONSECUTIVE_FRAMES: int = 3` - Required consecutive frames for alert

**State Transitions:**
```
Alert State:
  EAR >= threshold → frame_counter = 0
  EAR < threshold → frame_counter += 1
  frame_counter >= 3 → is_drowsy = True
```

## Data Models

### Frontend Data Models

#### DetectionResponse
```typescript
interface DetectionResponse {
  is_drowsy: boolean;
  ear: number;
  message: string;
  error?: string;
}
```

#### CameraConfig
```typescript
interface CameraConfig {
  video: {
    width: number;    // 640
    height: number;   // 480
  }
}
```

#### AlertConfig
```typescript
interface AlertConfig {
  frequency: number;        // 800 Hz
  duration: number;         // 0.5 seconds
  initialGain: number;      // 0.3
  finalGain: number;        // 0.01
  waveType: OscillatorType; // 'sine'
}
```

### Backend Data Models

#### EyeLandmarks
```python
# Left eye: landmarks 36-41 (6 points)
# Right eye: landmarks 42-47 (6 points)
EyeLandmarks = List[Tuple[int, int]]
```

#### DetectionRequest
```python
class DetectionRequest:
    image: str  # Base64 encoded JPEG
```

#### DetectionResult
```python
class DetectionResult:
    is_drowsy: bool
    ear: float
    message: str
```

### Configuration Constants

```python
# Backend Configuration
EAR_THRESHOLD = 0.25          # Eye closure threshold
CONSECUTIVE_FRAMES = 3        # Frames needed for alert
MODEL_PATH = "shape_predictor_68_face_landmarks.dat"
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 5000

# Frontend Configuration
API_URL = "http://localhost:5000"
CAPTURE_INTERVAL = 1500       # milliseconds
JPEG_QUALITY = 0.8            # 80% quality
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Base64 Encoding Round Trip
*For any* captured video frame, encoding to Base64 and then decoding back to an image array should preserve the image dimensions and essential visual data.
**Validates: Requirements 2.2, 2.4**

### Property 2: Face Detection Completeness
*For any* image containing one or more human faces, the face detector should identify at least one face and return valid bounding coordinates.
**Validates: Requirements 3.1**

### Property 3: Landmark Extraction Consistency
*For any* detected face, the landmark predictor should return exactly 68 coordinate pairs, and extracting eye landmarks should yield 6 points for the left eye (indices 36-41) and 6 points for the right eye (indices 42-47).
**Validates: Requirements 3.2, 3.3**

### Property 4: EAR Calculation Correctness
*For any* set of 6 eye landmark points, the calculated Eye Aspect Ratio should follow the formula EAR = (A + B) / (2.0 * C) where A and B are vertical distances and C is the horizontal distance, the average of both eyes should be computed, and the result should be rounded to 3 decimal places in the response.
**Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5**

### Property 5: Frame Counter State Management
*For any* sequence of EAR values, when EAR < 0.25 the frame counter should increment, when EAR >= 0.25 the frame counter should reset to 0, and when the counter reaches 3 or more, the system should return is_drowsy = true.
**Validates: Requirements 5.1, 5.2, 5.3**

### Property 6: Alert Triggering Consistency
*For any* detection response where is_drowsy is true, the frontend should both display visual alerts (red border styling) and trigger the audio alert sound.
**Validates: Requirements 5.4, 5.5**

### Property 7: Suggestion Display State
*For any* drowsiness state change, suggestions should be visible when is_drowsy is true and hidden when is_drowsy is false.
**Validates: Requirements 6.1, 6.3**

### Property 8: Status Update Responsiveness
*For any* detection response received from the backend, the frontend should update the displayed status message and EAR value to reflect the current response data.
**Validates: Requirements 7.1, 7.4**

### Property 9: Audio Alert Configuration
*For any* alert trigger, the Web Audio API should generate a sine wave oscillator, and upon completion, the oscillator should be stopped and resources released.
**Validates: Requirements 8.1, 8.5**

### Property 10: Error Response Structure
*For any* exception encountered during backend processing, the response should include an appropriate HTTP error code (400 for bad requests, 500 for server errors) and a descriptive error message field.
**Validates: Requirements 9.1, 9.2, 9.3**

### Property 11: Error Logging
*For any* error response received by the frontend, the error details should be logged to the browser console.
**Validates: Requirements 9.4**

### Property 12: CORS Header Presence
*For any* HTTP request sent from the frontend to the backend, the response should include appropriate CORS headers allowing cross-origin access.
**Validates: Requirements 10.2**

## Error Handling

### Frontend Error Handling

**Camera Access Errors:**
- Catch `getUserMedia` exceptions
- Display user-friendly error message: "Camera access denied"
- Set `cameraActive` state to false
- Log detailed error to console for debugging

**Network Errors:**
- Catch fetch request failures
- Display status: "Connection error"
- Log error details to console
- Continue attempting detection on subsequent intervals

**API Response Errors:**
- Handle HTTP 400/500 status codes
- Parse error message from response body
- Display generic error status to user
- Log full error details for debugging

### Backend Error Handling

**Missing Image Data:**
- Validate request contains `image` field
- Return HTTP 400 with error message: "No image provided"
- Do not process request further

**Image Decoding Errors:**
- Catch Base64 decoding exceptions
- Catch OpenCV image decoding failures
- Return HTTP 500 with descriptive error message
- Log full stack trace for debugging

**Face Detection Failures:**
- When no faces detected, return success response with:
  - `is_drowsy: false`
  - `message: "No face detected"`
- Do not treat as error condition
- Allow frontend to continue monitoring

**Model Loading Errors:**
- Validate `shape_predictor_68_face_landmarks.dat` exists at startup
- If missing, raise exception and prevent server start
- Display clear error message indicating model file is required
- Include download instructions in error message

**Processing Exceptions:**
- Catch all unexpected exceptions in detection endpoint
- Return HTTP 500 with error message
- Log full exception details including stack trace
- Reset frame counter to prevent state corruption

### Error Recovery Strategies

**Transient Failures:**
- Frontend continues periodic capture attempts
- Backend resets state on successful request after error
- No manual intervention required

**Persistent Failures:**
- Frontend displays persistent error status
- User can refresh page to reinitialize
- Backend logs errors for administrator review

## Testing Strategy

### Unit Testing

The system will employ unit tests to verify specific behaviors and edge cases:

**Frontend Unit Tests:**
- Camera initialization with mocked `getUserMedia`
- Frame capture and Base64 encoding
- Status message updates for specific states
- Alert triggering on drowsy responses
- Error handling for network failures
- Audio context creation and cleanup

**Backend Unit Tests:**
- Base64 image decoding
- Request validation (missing image data)
- Response formatting
- Error response structure
- CORS header configuration
- Health endpoint functionality

**Edge Cases:**
- Images with no faces detected
- Images with multiple faces
- Empty or malformed Base64 strings
- Requests missing required fields
- Model file not found at startup

### Property-Based Testing

The system will employ property-based testing to verify universal correctness properties across many randomly generated inputs. Each property test should run a minimum of 100 iterations to ensure statistical confidence.

**Testing Framework:**
- **Frontend**: Use `fast-check` library for JavaScript/TypeScript property-based testing
- **Backend**: Use `Hypothesis` library for Python property-based testing

**Property Test Requirements:**
- Each property test MUST be tagged with a comment explicitly referencing the correctness property from this design document
- Tag format: `**Feature: drowsiness-detector, Property {number}: {property_text}**`
- Each correctness property MUST be implemented by a SINGLE property-based test
- Configure each test to run minimum 100 iterations

**Frontend Property Tests:**

1. **Base64 Encoding Round Trip** (Property 1)
   - Generate random image data
   - Encode to Base64, decode back
   - Verify dimensions preserved

2. **Alert Triggering Consistency** (Property 6)
   - Generate random drowsy responses
   - Verify both visual and audio alerts trigger

3. **Suggestion Display State** (Property 7)
   - Generate random drowsiness state changes
   - Verify suggestions visibility matches state

4. **Status Update Responsiveness** (Property 8)
   - Generate random detection responses
   - Verify status and EAR display updates

5. **Audio Alert Configuration** (Property 9)
   - Generate random alert triggers
   - Verify oscillator creation and cleanup

6. **Error Logging** (Property 11)
   - Generate random error responses
   - Verify console logging occurs

**Backend Property Tests:**

1. **Landmark Extraction Consistency** (Property 3)
   - Generate random face images
   - Verify 68 landmarks returned
   - Verify eye landmark indices correct

2. **EAR Calculation Correctness** (Property 4)
   - Generate random eye landmark coordinates
   - Verify EAR formula applied correctly
   - Verify rounding to 3 decimals

3. **Frame Counter State Management** (Property 5)
   - Generate random EAR sequences
   - Verify counter increments/resets correctly
   - Verify drowsy threshold at 3 frames

4. **Error Response Structure** (Property 10)
   - Generate random error conditions
   - Verify correct HTTP status codes
   - Verify error message presence

5. **CORS Header Presence** (Property 12)
   - Generate random valid requests
   - Verify CORS headers in all responses

### Integration Testing

**End-to-End Flow:**
- Start both frontend and backend servers
- Simulate camera feed with test images
- Verify complete detection pipeline
- Test drowsy and alert scenarios
- Verify alert triggering and display

**API Contract Testing:**
- Verify request/response formats
- Test all endpoint paths
- Validate error responses
- Check CORS functionality

### Performance Testing

**Response Time:**
- Measure backend processing time per frame
- Target: < 2 seconds per detection request
- Test with various image sizes

**Resource Usage:**
- Monitor memory usage during extended operation
- Verify camera resources properly released
- Check for memory leaks in audio context

**Stress Testing:**
- Test with rapid consecutive requests
- Verify frame counter state consistency
- Test with poor quality images

### Test Data

**Test Images:**
- Faces with eyes open (high EAR)
- Faces with eyes closed (low EAR)
- Faces with partial eye closure
- Multiple faces in frame
- No faces in frame
- Poor lighting conditions
- Various face angles and positions

**Mock Responses:**
- Drowsy detection responses
- Alert responses
- No face detected responses
- Error responses (400, 500)
- Various EAR values (0.1 to 0.4)

## Implementation Notes

### Frontend Implementation

**Technology Stack:**
- React 18+ with functional components and hooks
- Web Audio API for alert sounds
- Canvas API for frame capture
- Fetch API for HTTP requests

**Key Considerations:**
- Use `useRef` for video, canvas, and audio context to avoid re-renders
- Use `useEffect` for camera initialization and cleanup
- Implement proper cleanup in component unmount
- Handle browser compatibility for `getUserMedia`
- Optimize Base64 encoding with appropriate JPEG quality

### Backend Implementation

**Technology Stack:**
- Flask 2+ for REST API
- Flask-CORS for cross-origin support
- OpenCV (cv2) for image processing
- dlib for face detection and landmarks
- NumPy for array operations
- SciPy for distance calculations

**Key Considerations:**
- Load dlib models at server startup, not per request
- Use grayscale conversion for faster face detection
- Maintain frame counter as global state (consider thread safety for production)
- Implement proper exception handling at all levels
- Validate all inputs before processing
- Use appropriate HTTP status codes

### Deployment Considerations

**Development:**
- Frontend: `npm start` on port 3000
- Backend: `python api_server.py` on port 5000
- CORS enabled for localhost

**Production:**
- Use HTTPS for camera access (browser requirement)
- Configure CORS for specific allowed origins
- Use production WSGI server (Gunicorn, uWSGI)
- Implement rate limiting on API endpoints
- Add authentication if needed
- Consider containerization (Docker)
- Implement proper logging and monitoring

### Model Requirements

**Required Files:**
- `shape_predictor_68_face_landmarks.dat` (99.7 MB)
- Download from: http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
- Must be placed in backend directory
- Verify file integrity before use

### Configuration Tuning

**Sensitivity Adjustment:**
- Decrease `EAR_THRESHOLD` (e.g., 0.20) for more sensitive detection
- Increase `EAR_THRESHOLD` (e.g., 0.30) for less sensitive detection
- Adjust `CONSECUTIVE_FRAMES` for faster/slower alerts

**Performance Tuning:**
- Adjust `CAPTURE_INTERVAL` for more/less frequent checks
- Modify `JPEG_QUALITY` to balance image quality vs. transmission size
- Consider reducing video resolution for slower devices

### Browser Compatibility

**Supported Browsers:**
- Chrome 53+
- Firefox 36+
- Safari 11+
- Edge 79+

**Required Features:**
- `getUserMedia` API
- Web Audio API
- Canvas API
- Fetch API
- ES6+ JavaScript support

### Security Considerations

**Privacy:**
- All processing happens locally (no cloud transmission)
- Camera feed not recorded or stored
- Images transmitted only to local backend
- No persistent storage of user images

**Input Validation:**
- Validate Base64 format before decoding
- Limit image size to prevent memory exhaustion
- Sanitize error messages to prevent information leakage

**CORS Configuration:**
- Restrict allowed origins in production
- Implement proper authentication if deployed publicly
- Use HTTPS to prevent man-in-the-middle attacks
