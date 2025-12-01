# Requirements Document

## Introduction

The Drowsiness Detector is a real-time web-based monitoring system that detects signs of user fatigue by analyzing facial features through camera input. The system calculates Eye Aspect Ratio (EAR) to determine drowsiness levels and provides immediate alerts with actionable suggestions to help users maintain alertness. The application uses a client-server architecture with a React frontend for user interaction and a Python backend for computer vision processing.

## Glossary

- **System**: The complete Drowsiness Detector application including frontend and backend components
- **Frontend**: The React-based web client that captures video and displays alerts
- **Backend**: The Python-based API server that processes images and detects drowsiness
- **EAR (Eye Aspect Ratio)**: A numerical metric calculated from eye landmark coordinates that indicates the degree of eye closure
- **Frame**: A single still image captured from the video stream
- **Landmark**: A specific coordinate point on a detected face (e.g., eye corners, nose tip)
- **Base64 Encoding**: A method of converting binary image data into text format for transmission
- **Drowsiness State**: A condition where the user's EAR falls below the threshold for a consecutive number of frames
- **Alert**: A combination of visual and auditory notifications triggered when drowsiness is detected
- **Face Detector**: The dlib-based algorithm that locates faces in an image
- **Landmark Predictor**: The dlib model that identifies 68 facial landmark points

## Requirements

### Requirement 1

**User Story:** As a user, I want the system to access my camera and display a live video feed, so that I can verify the monitoring is active.

#### Acceptance Criteria

1. WHEN the application starts THEN the System SHALL request camera permissions from the user
2. WHEN camera permissions are granted THEN the System SHALL display a live video feed from the user's camera
3. WHEN camera permissions are denied THEN the System SHALL display an error message indicating camera access is required
4. WHEN the video feed is active THEN the System SHALL display a status indicator showing "Camera active"
5. WHEN the user closes the application THEN the System SHALL release all camera resources

### Requirement 2

**User Story:** As a user, I want the system to continuously monitor my alertness, so that I can be warned before I become dangerously drowsy.

#### Acceptance Criteria

1. WHEN the camera is active THEN the Frontend SHALL capture frames at regular intervals of 1.5 seconds
2. WHEN a frame is captured THEN the Frontend SHALL encode the image data as Base64 format
3. WHEN image data is encoded THEN the Frontend SHALL send the data to the Backend via HTTP POST request
4. WHEN the Backend receives image data THEN the Backend SHALL decode the Base64 string into a processable image array
5. WHEN the Backend processes a request THEN the Backend SHALL return a response within 2 seconds

### Requirement 3

**User Story:** As a user, I want the system to accurately detect my face and eyes, so that drowsiness detection is reliable.

#### Acceptance Criteria

1. WHEN the Backend receives an image THEN the Backend SHALL detect all faces present in the image
2. WHEN a face is detected THEN the Backend SHALL identify 68 facial landmark points on the face
3. WHEN facial landmarks are identified THEN the Backend SHALL extract the coordinates for both left eye landmarks (points 36-41) and right eye landmarks (points 42-47)
4. WHEN no face is detected in an image THEN the Backend SHALL return a response indicating no face was found
5. WHEN multiple faces are detected THEN the Backend SHALL process the first detected face

### Requirement 4

**User Story:** As a user, I want the system to calculate how closed my eyes are, so that drowsiness can be quantified objectively.

#### Acceptance Criteria

1. WHEN eye landmarks are extracted THEN the Backend SHALL calculate the Eye Aspect Ratio for the left eye
2. WHEN eye landmarks are extracted THEN the Backend SHALL calculate the Eye Aspect Ratio for the right eye
3. WHEN both eye EARs are calculated THEN the Backend SHALL compute the average EAR value
4. WHEN the EAR is calculated THEN the Backend SHALL use the formula: EAR = (A + B) / (2.0 * C) where A and B are vertical eye distances and C is the horizontal eye distance
5. WHEN the Backend returns a response THEN the response SHALL include the calculated EAR value rounded to 3 decimal places

### Requirement 5

**User Story:** As a user, I want to be alerted when I show signs of drowsiness, so that I can take action to stay safe.

#### Acceptance Criteria

1. WHEN the average EAR falls below 0.25 THEN the Backend SHALL increment a consecutive frame counter
2. WHEN the consecutive frame counter reaches 3 or more THEN the Backend SHALL return a drowsiness detection response
3. WHEN the average EAR is 0.25 or above THEN the Backend SHALL reset the consecutive frame counter to zero
4. WHEN a drowsiness detection response is received THEN the Frontend SHALL display a visual alert with red border styling
5. WHEN a drowsiness detection response is received THEN the Frontend SHALL play an auditory alert sound

### Requirement 6

**User Story:** As a user, I want to receive actionable suggestions when drowsy, so that I know how to improve my alertness.

#### Acceptance Criteria

1. WHEN drowsiness is detected THEN the Frontend SHALL display a list of wake-up suggestions
2. WHEN displaying suggestions THEN the Frontend SHALL include at least 5 different actionable recommendations
3. WHEN drowsiness is no longer detected THEN the Frontend SHALL hide the suggestions list
4. WHEN suggestions are displayed THEN the suggestions SHALL include diverse activities such as taking breaks, hydrating, and physical movement

### Requirement 7

**User Story:** As a user, I want to see my current alertness status, so that I can understand how the system is evaluating me.

#### Acceptance Criteria

1. WHEN the Frontend receives a detection response THEN the Frontend SHALL display the current status message
2. WHEN drowsiness is detected THEN the Frontend SHALL display the status "⚠️ DROWSINESS DETECTED!"
3. WHEN the user is alert THEN the Frontend SHALL display the status "Monitoring..." or "Alert"
4. WHEN the Backend returns an EAR value THEN the Frontend SHALL display the EAR value to the user
5. WHEN a connection error occurs THEN the Frontend SHALL display the status "Connection error"

### Requirement 8

**User Story:** As a user, I want the alert sound to be noticeable but not jarring, so that I am awakened without being startled.

#### Acceptance Criteria

1. WHEN an alert is triggered THEN the Frontend SHALL generate an audio tone using the Web Audio API
2. WHEN generating the alert tone THEN the Frontend SHALL use a sine wave oscillator at 800 Hz frequency
3. WHEN playing the alert THEN the Frontend SHALL set the initial gain to 0.3 and exponentially decrease to 0.01
4. WHEN playing the alert THEN the Frontend SHALL limit the duration to 0.5 seconds
5. WHEN the alert completes THEN the Frontend SHALL stop the oscillator and release audio resources

### Requirement 9

**User Story:** As a system administrator, I want the backend to handle errors gracefully, so that the system remains stable during unexpected conditions.

#### Acceptance Criteria

1. WHEN the Backend encounters an exception during processing THEN the Backend SHALL return an HTTP 500 error response
2. WHEN the Backend receives a request without image data THEN the Backend SHALL return an HTTP 400 error response
3. WHEN an error response is returned THEN the response SHALL include a descriptive error message
4. WHEN the Frontend receives an error response THEN the Frontend SHALL log the error to the console
5. WHEN the Backend fails to load the landmark predictor model THEN the Backend SHALL fail to start and display an error message

### Requirement 10

**User Story:** As a developer, I want the system to support cross-origin requests, so that the frontend and backend can communicate when hosted separately.

#### Acceptance Criteria

1. WHEN the Backend starts THEN the Backend SHALL enable CORS (Cross-Origin Resource Sharing) for all routes
2. WHEN the Frontend sends a request to the Backend THEN the Backend SHALL include appropriate CORS headers in the response
3. WHEN CORS is enabled THEN the Backend SHALL accept requests from any origin during development
4. WHEN the Backend receives a preflight OPTIONS request THEN the Backend SHALL respond with appropriate CORS headers
