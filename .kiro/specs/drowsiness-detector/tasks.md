# Implementation Plan

- [x] 1. Set up backend infrastructure and core image processing
  - Create Flask API server with CORS support
  - Implement Base64 image decoding functionality
  - Set up dlib face detector and landmark predictor initialization
  - Implement health check endpoint
  - _Requirements: 10.1, 2.4, 3.1, 3.2_

- [x] 1.1 Write property test for Base64 encoding round trip
  - **Property 1: Base64 Encoding Round Trip**
  - **Validates: Requirements 2.2, 2.4**

- [x] 2. Implement face detection and landmark extraction
  - Implement face detection in grayscale images
  - Extract 68 facial landmark points from detected faces
  - Handle cases with no faces detected
  - Handle cases with multiple faces (process first face)
  - _Requirements: 3.1, 3.2, 3.4, 3.5_

- [x] 2.1 Write property test for face detection completeness
  - **Property 2: Face Detection Completeness**
  - **Validates: Requirements 3.1**

- [x] 2.2 Write property test for landmark extraction consistency
  - **Property 3: Landmark Extraction Consistency**
  - **Validates: Requirements 3.2, 3.3**

- [x] 3. Implement Eye Aspect Ratio (EAR) calculation
  - Extract left eye landmarks (points 36-41)
  - Extract right eye landmarks (points 42-47)
  - Implement EAR calculation function using the formula: EAR = (A + B) / (2.0 * C)
  - Calculate average EAR from both eyes
  - Round EAR to 3 decimal places
  - _Requirements: 3.3, 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 3.1 Write property test for EAR calculation correctness
  - **Property 4: EAR Calculation Correctness**
  - **Validates: Requirements 4.1, 4.2, 4.3, 4.4, 4.5**

- [x] 4. Implement drowsiness detection state management
  - Create global frame counter variable
  - Implement logic to increment counter when EAR < 0.25
  - Implement logic to reset counter when EAR >= 0.25
  - Implement drowsiness detection when counter >= 3
  - Return appropriate detection response with is_drowsy flag
  - _Requirements: 5.1, 5.2, 5.3_

- [x] 4.1 Write property test for frame counter state management
  - **Property 5: Frame Counter State Management**
  - **Validates: Requirements 5.1, 5.2, 5.3**

- [x] 5. Implement backend API endpoint and error handling
  - Create POST /detect_drowsiness endpoint
  - Validate incoming requests for image data
  - Return structured JSON responses with is_drowsy, ear, and message fields
  - Implement error handling for missing image data (HTTP 400)
  - Implement error handling for processing exceptions (HTTP 500)
  - Include descriptive error messages in error responses
  - _Requirements: 2.3, 2.5, 9.1, 9.2, 9.3, 9.5_

- [x] 5.1 Write property test for error response structure
  - **Property 10: Error Response Structure**
  - **Validates: Requirements 9.1, 9.2, 9.3**

- [x] 5.2 Write property test for CORS header presence
  - **Property 12: CORS Header Presence**
  - **Validates: Requirements 10.2**

- [x] 6. Checkpoint - Verify backend functionality
  - Ensure all tests pass, ask the user if questions arise.

- [x] 7. Set up React frontend structure and camera access
  - Create main App component with necessary state variables (isDrowsy, status, ear, cameraActive)
  - Create refs for video, canvas, and audio context
  - Implement camera initialization using getUserMedia API
  - Handle camera permission requests
  - Display live video feed
  - Implement camera resource cleanup on unmount
  - Display appropriate status messages for camera states
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 7.1 Write unit tests for camera initialization
  - Test camera permission request
  - Test video feed display on permission grant
  - Test error message on permission denial
  - Test resource cleanup
  - _Requirements: 1.1, 1.2, 1.3, 1.5_

- [x] 8. Implement frame capture and transmission
  - Create canvas element for frame capture
  - Implement periodic frame capture (1.5 second intervals)
  - Convert captured frames to Base64 JPEG format (80% quality)
  - Implement HTTP POST request to backend /detect_drowsiness endpoint
  - Handle API responses and update component state
  - _Requirements: 2.1, 2.2, 2.3_

- [x] 8.1 Write property test for status update responsiveness
  - **Property 8: Status Update Responsiveness**
  - **Validates: Requirements 7.1, 7.4**

- [x] 9. Implement visual alert system
  - Create CSS styling for alert state (red border)
  - Implement conditional rendering based on isDrowsy state
  - Display drowsiness status messages
  - Display EAR value when available
  - Handle connection error display
  - _Requirements: 5.4, 7.1, 7.2, 7.3, 7.4, 7.5_

- [x] 9.1 Write property test for alert triggering consistency
  - **Property 6: Alert Triggering Consistency**
  - **Validates: Requirements 5.4, 5.5**

- [x] 10. Implement audio alert system
  - Create Web Audio API context
  - Implement alert sound generation using sine wave oscillator
  - Configure oscillator frequency (800 Hz)
  - Configure gain envelope (0.3 initial, exponentially decrease to 0.01)
  - Set alert duration (0.5 seconds)
  - Implement oscillator cleanup after playback
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [x] 10.1 Write property test for audio alert configuration
  - **Property 9: Audio Alert Configuration**
  - **Validates: Requirements 8.1, 8.5**

- [x] 11. Implement wake-up suggestions display
  - Create suggestions array with at least 5 actionable recommendations
  - Implement conditional rendering to show suggestions when drowsy
  - Implement conditional rendering to hide suggestions when alert
  - Style suggestions list for clear visibility
  - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [x] 11.1 Write property test for suggestion display state
  - **Property 7: Suggestion Display State**
  - **Validates: Requirements 6.1, 6.3**

- [x] 11.2 Write unit test for minimum suggestion count
  - Verify suggestions array contains at least 5 items
  - _Requirements: 6.2_

- [x] 12. Implement frontend error handling and logging
  - Add try-catch blocks for camera access errors
  - Add try-catch blocks for API request errors
  - Implement console logging for all errors
  - Display user-friendly error messages
  - Handle network failures gracefully
  - _Requirements: 9.4_

- [x] 12.1 Write property test for error logging
  - **Property 11: Error Logging**
  - **Validates: Requirements 9.4**

- [x] 13. Final checkpoint - End-to-end verification
  - Ensure all tests pass, ask the user if questions arise.
