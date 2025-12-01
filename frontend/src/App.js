import React, { useRef, useEffect, useState } from 'react';
import './App.css';
import LandingPage from './LandingPage';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';

function App() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const audioContextRef = useRef(null);
  
  const [isDrowsy, setIsDrowsy] = useState(false);
  const [status, setStatus] = useState('Initializing...');
  const [ear, setEar] = useState(null);
  const [cameraActive, setCameraActive] = useState(false);
  const [faceBox, setFaceBox] = useState(null);
  const [faceState, setFaceState] = useState('searching'); // 'searching', 'locked', 'drowsy'
  const [showCalibration, setShowCalibration] = useState(false);
  const [calibrationData, setCalibrationData] = useState({ min: null, max: null, avg: null, count: 0 });

  const suggestions = [
    '☕ Take a coffee break',
    '🚶 Walk around for 5 minutes',
    '💧 Drink some water',
    '🪟 Open a window for fresh air',
    '🧘 Do some stretches',
    '😴 Consider taking a power nap'
  ];

  useEffect(() => {
    startCamera();
    return () => {
      if (videoRef.current && videoRef.current.srcObject) {
        videoRef.current.srcObject.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { width: 640, height: 480 } 
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setCameraActive(true);
        setStatus('Camera active');
        setTimeout(() => startDetection(), 2000);
      }
    } catch (err) {
      setStatus('Camera access denied');
      console.error('Camera error:', err);
    }
  };

  const startDetection = () => {
    // Reduced from 1500ms to 1000ms for faster detection
    // This means 2 consecutive frames = 2 seconds instead of 3 seconds
    setInterval(() => {
      captureAndSend();
    }, 1000);
  };

  const captureAndSend = async () => {
    if (!videoRef.current || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const video = videoRef.current;
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);
    
    const imageData = canvas.toDataURL('image/jpeg', 0.8);

    try {
      const response = await fetch(`${API_URL}/detect_drowsiness`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: imageData })
      });

      const result = await response.json();
      
      // Handle error responses from the API
      if (result.error || (response.ok === false)) {
        const errorMessage = result.error || `HTTP ${response.status} error`;
        console.error('API error:', new Error(errorMessage));
        setStatus('Connection error');
        setFaceBox(null);
        setFaceState('searching');
        return;
      }
      
      // Debug logging to help tune detection
      console.log(`[DEBUG] EAR: ${result.ear} | Drowsy: ${result.is_drowsy} | Counter: ${result.frame_counter || 0}`);
      
      // Update face box
      if (result.face_box) {
        setFaceBox(result.face_box);
        
        if (result.is_drowsy) {
          setIsDrowsy(true);
          setFaceState('drowsy');
          playAlert();
          setStatus('🚨 WAKE UP! DROWSINESS DETECTED!');
        } else {
          setIsDrowsy(false);
          setFaceState('locked');
          // Show more detailed status based on EAR value
          const earValue = result.ear;
          if (earValue < 0.30) {
            setStatus('⚠️ Face Locked - Eyes getting heavy...');
          } else {
            setStatus('✅ Face Locked - Alert and monitoring');
          }
        }
      } else {
        setFaceBox(null);
        setFaceState('searching');
        setIsDrowsy(false);
        setStatus('🔍 Searching for face...');
      }
      
      if (result.ear) {
        setEar(result.ear);
        
        // Track calibration data
        if (showCalibration && result.face_box) {
          setCalibrationData(prev => {
            const newMin = prev.min === null ? result.ear : Math.min(prev.min, result.ear);
            const newMax = prev.max === null ? result.ear : Math.max(prev.max, result.ear);
            const newCount = prev.count + 1;
            const newAvg = prev.avg === null ? result.ear : (prev.avg * prev.count + result.ear) / newCount;
            return { min: newMin, max: newMax, avg: newAvg, count: newCount };
          });
        }
      }
    } catch (err) {
      setStatus('Connection error');
      console.error('API error:', err);
      setFaceBox(null);
    }
  };

  const playAlert = () => {
    if (!audioContextRef.current) {
      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
    }
    
    const ctx = audioContextRef.current;
    const oscillator = ctx.createOscillator();
    const gainNode = ctx.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(ctx.destination);
    
    oscillator.frequency.value = 800;
    oscillator.type = 'sine';
    
    gainNode.gain.setValueAtTime(0.3, ctx.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.5);
    
    oscillator.start(ctx.currentTime);
    oscillator.stop(ctx.currentTime + 0.5);
  };

  return (
    <div className="App">
      <LandingPage />
      
      <section id="detector-section" className="detector-section">
        <div className="detector-intro">
          <h2>Try It Now - Live Demo</h2>
          <p>
            Experience our AI-powered drowsiness detection in action. 
            Allow camera access and see how the technology works in real-time.
          </p>
        </div>
        
        <div className="container">
          <h1>😴 Drowsiness Detector</h1>
        
        <div className={`video-container ${isDrowsy ? 'alert' : ''}`}>
          <video 
            ref={videoRef} 
            autoPlay 
            playsInline 
            muted
          />
          {/* Face tracking box - always visible */}
          <div 
            className={`face-box ${faceState}`}
            style={faceBox ? {
              left: `${(faceBox.left / 640) * 100}%`,
              top: `${(faceBox.top / 480) * 100}%`,
              width: `${((faceBox.right - faceBox.left) / 640) * 100}%`,
              height: `${((faceBox.bottom - faceBox.top) / 480) * 100}%`,
            } : {
              left: '25%',
              top: '15%',
              width: '50%',
              height: '70%',
            }}
          >
            {faceState === 'searching' && <span className="scanning-text">SCANNING...</span>}
            {faceState === 'locked' && <span className="locked-text">LOCKED</span>}
            {faceState === 'drowsy' && <span className="alert-text">⚠️ WAKE UP!</span>}
          </div>
          <canvas ref={canvasRef} style={{ display: 'none' }} />
        </div>

        <div className={`status-panel ${isDrowsy ? 'drowsy' : 'alert'}`}>
          <h2>{status}</h2>
          {ear && <p className="ear-value">EAR: {ear}</p>}
        </div>

        {isDrowsy && (
          <div className="suggestions">
            <h3>Wake Up Suggestions:</h3>
            <ul>
              {suggestions.map((suggestion, index) => (
                <li key={index}>{suggestion}</li>
              ))}
            </ul>
          </div>
        )}

        {!cameraActive && (
          <div className="warning">
            <p>Please allow camera access to start monitoring</p>
          </div>
        )}

        {/* Calibration Panel */}
        <div className="calibration-panel">
          <button 
            className="calibration-btn"
            onClick={() => {
              setShowCalibration(!showCalibration);
              if (!showCalibration) {
                setCalibrationData({ min: null, max: null, avg: null, count: 0 });
              }
            }}
          >
            {showCalibration ? '✓ Stop Calibration' : '🔧 Calibrate Detection'}
          </button>
          
          {showCalibration && (
            <div className="calibration-info">
              <h4>📊 Calibration Mode Active</h4>
              <p>Keep your eyes OPEN and look at the camera normally for 10-15 seconds</p>
              {calibrationData.count > 5 && (
                <div className="calibration-results">
                  <p><strong>Your EAR Range:</strong></p>
                  <p>Average (Alert): {calibrationData.avg?.toFixed(3)}</p>
                  <p>Min: {calibrationData.min?.toFixed(3)} | Max: {calibrationData.max?.toFixed(3)}</p>
                  <p className="calibration-tip">
                    💡 Tip: If your average is below 0.30, detection might be too sensitive. 
                    Check your lighting and camera angle!
                  </p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Debug Info Panel */}
        <div className="debug-panel">
          <details>
            <summary>🔍 Debug Info & Tuning Guide</summary>
            <div className="debug-content">
              <h4>Current Settings:</h4>
              <ul>
                <li>EAR Threshold: 0.28 (drowsy if below this)</li>
                <li>Detection Speed: 1 second per frame</li>
                <li>Alert Trigger: 2 consecutive frames (2 seconds)</li>
              </ul>
              
              <h4>Troubleshooting:</h4>
              <ul>
                <li><strong>Not detecting drowsiness?</strong> Your EAR might be naturally low. Check calibration above.</li>
                <li><strong>Too many false alerts?</strong> Improve lighting or adjust camera angle.</li>
                <li><strong>Yellow box stuck?</strong> Ensure good lighting and face the camera directly.</li>
                <li><strong>Detection too slow?</strong> Backend is processing - check console for timing.</li>
              </ul>
              
              <h4>Optimal Conditions:</h4>
              <ul>
                <li>✓ Good frontal lighting (not backlit)</li>
                <li>✓ Face camera directly</li>
                <li>✓ Remove glasses if possible (can affect detection)</li>
                <li>✓ Stable head position</li>
              </ul>
            </div>
          </details>
        </div>
      </div>
      </section>
    </div>
  );
}

export default App;
