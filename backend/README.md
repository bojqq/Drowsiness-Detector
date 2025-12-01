# Backend Setup

## Prerequisites
- Python 3.7+
- pip

## Installation

1. Install dependencies (MediaPipe + OpenCV are included):
```bash
pip install -r requirements.txt
```

## Run

```bash
python api_server.py
```

Server will run on http://localhost:5001

## Manual Verification

1. Start the backend with `python api_server.py`.
2. Kick off the React frontend and allow it to stream camera frames.
3. Place your face clearly in frame with normal lighting—the API response should report `is_drowsy: false`.
4. Cover your face or close your eyes for a few seconds—the API should flip to `is_drowsy: true` once the eye-aspect ratio drops below the configured threshold.
5. Check the backend logs (`DEBUG_MODE` is enabled) to see live EAR values and brightness hints if no face is detected. This helps course graders confirm the detector is running on real camera data.
