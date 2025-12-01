😴 Drowsiness Detector

Project Overview

The Drowsiness Detector is a real-time, web-based application designed to monitor user alertness using the device's camera. By analyzing facial features, specifically the state of the eyes, the application can detect signs of fatigue and intervene instantly with auditory and visual alerts, along with actionable suggestions to help the user stay awake.

This application follows a modern client-server architecture, splitting the user interface logic from the intensive artificial intelligence processing.

Architecture

The system is built on two primary layers that communicate over a network connection: a responsive web dashboard built with React (the Client) and a high-performance computer vision engine built with Python (the Server).

Frontend (Client) - React Dashboard

The frontend serves as the user's main point of interaction and is responsible for all display and interaction logic.

Key Responsibilities:

Camera Capture: Uses the browser's navigator.mediaDevices API to access and display the live video stream from the user's laptop camera.

Frame Sampling: Periodically captures still images (frames) from the live video using a hidden HTML Canvas element.

Data Encoding: Converts the raw image frames into a Base64 encoded string format so they can be securely transmitted as text within an API request.

Real-time Display: Displays the camera feed, the current alert status, and recommended wake-up techniques (e.g., "Take a short walk," "Hydrate").

Alert System: Upon receiving a positive detection signal from the backend, the React component triggers immediate visual state changes and plays a disruptive sound effect using the Web Audio API.

Backend (Server) - Python AI Engine

The backend handles all the heavy computational work, ensuring the client remains fast and responsive. We recommend using FastAPI or Flask for the web server framework due to their efficiency.

Key Responsibilities:

API Endpoint: Provides a RESTful endpoint (e.g., /detect_drowsiness) to receive the Base64 image data sent from the React client.

Image Processing: Decodes the Base64 string back into a processable image array (using libraries like OpenCV).

AI/CV Core Logic: Runs the core drowsiness detection algorithm, which includes:

Face detection to locate the user's face.

Landmark detection (using Dlib or similar) to pinpoint the exact location of the eyes.

Calculation of the Eye Aspect Ratio (EAR) to quantify the degree of eye closure.

Classification & Response: Determines if the EAR falls below a predefined threshold for a sustained period and sends a concise JSON response back to the React client, indicating the current alertness state (e.g., {"is_drowsy": true}).

Communication Pipeline

Communication is managed entirely through asynchronous HTTP POST requests:

Request: The React frontend captures a frame, converts it to Base64, and sends it to the Python API endpoint.

Processing: The Python server processes the image data and applies the AI model.

Response: The Python server returns a lightweight JSON object containing the detection result.

Action: The React frontend receives the result and updates the UI accordingly.

Installation and Setup

Prerequisites

Node.js (for React)

Python 3.x (for the AI Engine)

Frontend Setup (React)

# Navigate to the frontend directory
cd frontend/
npm install
npm start


Backend Setup (Python)

# Navigate to the backend directory
cd backend/
pip install -r requirements.txt
# Run the API server
python api_server.py


Note: The server address (e.g., http://localhost:5000) must be consistent between your React fetch calls and your Python server configuration.