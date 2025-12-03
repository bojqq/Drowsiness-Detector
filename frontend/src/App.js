import React, { useRef, useEffect, useState, useCallback } from 'react';
import './App.css';
import LandingPage from './LandingPage';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';

function App() {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const audioContextRef = useRef(null);
  const alertIntervalRef = useRef(null); // Track alert loop interval
  const alarmActiveRef = useRef(false); // True when alarm loop is running
  
  const [isDrowsy, setIsDrowsy] = useState(false);
  const [status, setStatus] = useState('Initializing...');
  const [ear, setEar] = useState(null);
  const [cameraActive, setCameraActive] = useState(false);
  const [faceBox, setFaceBox] = useState(null);
  const [faceState, setFaceState] = useState('searching'); // 'searching', 'locked', 'drowsy'
  const [showCalibration, setShowCalibration] = useState(false);
  const [calibrationData, setCalibrationData] = useState({ min: null, max: null, avg: null, count: 0 });
  const [drowsyScore, setDrowsyScore] = useState(0);
  const [confidence, setConfidence] = useState(0);
  const [wasAlertActive, setWasAlertActive] = useState(false);
  const [isAlertPlaying, setIsAlertPlaying] = useState(false);
  
  const captureAndSendRef = useRef(null);
  const detectionIntervalRef = useRef(null);

  const suggestions = [
    '☕ Take a coffee break',
    '🚶 Walk around for 5 minutes',
    '💧 Drink some water',
    '🪟 Open a window for fresh air',
    '🧘 Do some stretches',
    '😴 Consider taking a power nap'
  ];

  // Define callbacks first before using them
  const startDetection = useCallback(() => {
    // Reduced from 1500ms to 1000ms for faster detection
    if (detectionIntervalRef.current) {
      clearInterval(detectionIntervalRef.current);
    }
    
    detectionIntervalRef.current = setInterval(() => {
      if (captureAndSendRef.current) {
        captureAndSendRef.current();
      }
    }, 1000);
  }, []);

  const startCamera = useCallback(async () => {
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
  }, [startDetection]);

  const playAlertBeep = useCallback(() => {
    if (!audioContextRef.current) return;
    
    const ctx = audioContextRef.current;
    
    // Create LOUD multi-tone alarm sound
    const frequencies = [1000, 1400, 800]; // Three tones for urgency
    
    frequencies.forEach((freq, index) => {
      const oscillator = ctx.createOscillator();
      const gainNode = ctx.createGain();
      
      oscillator.connect(gainNode);
      gainNode.connect(ctx.destination);
      
      oscillator.frequency.value = freq;
      oscillator.type = 'square'; // Square wave is louder and more jarring
      
      const startTime = ctx.currentTime + (index * 0.1);
      
      // LOUD volume - 0.6 (60% volume)
      gainNode.gain.setValueAtTime(0.6, startTime);
      gainNode.gain.exponentialRampToValueAtTime(0.01, startTime + 0.3);
      
      oscillator.start(startTime);
      oscillator.stop(startTime + 0.3);
    });
  }, []);
  
  const playAlert = useCallback(() => {
    // Prevent duplicate intervals by checking ref state (instant, no async lag)
    if (alarmActiveRef.current) {
      return;
    }
    
    alarmActiveRef.current = true;
    setIsAlertPlaying(true);
    console.log('[ALERT] 🚨 Starting LOUD continuous alarm!');
    
    if (!audioContextRef.current) {
      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
    }
    
    // Play loud alert immediately
    playAlertBeep();
    
    // Continue playing every 800ms until stopped
    alertIntervalRef.current = setInterval(() => {
      playAlertBeep();
    }, 800);
  }, [playAlertBeep]);
  
  const stopAlert = useCallback(() => {
    if (!alarmActiveRef.current && !alertIntervalRef.current) {
      setIsAlertPlaying(false);
      return; // Already stopped
    }
    
    console.log('[ALERT] ✅ Stopping alarm - user woke up or face lost');
    
    alarmActiveRef.current = false;
    
    if (alertIntervalRef.current) {
      clearInterval(alertIntervalRef.current);
      alertIntervalRef.current = null;
      console.log('[ALERT] 🔇 Interval cleared');
    }
    
    setIsAlertPlaying(false);
  }, []);

  const captureAndSend = useCallback(async () => {
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
      
      // Enhanced debug logging
      console.log(`[DEBUG] EAR: ${result.ear} | Raw: ${result.raw_ear} | Drowsy: ${result.is_drowsy} | Score: ${result.drowsy_score}/100 | Blink: ${result.is_blink}`);
      
      // Update drowsiness metrics
      if (result.drowsy_score !== undefined) {
        setDrowsyScore(result.drowsy_score);
        setConfidence(result.confidence || 0);
      }
      
      // Update face box and state
      if (result.face_box) {
        setFaceBox(result.face_box);
        
        if (result.is_drowsy) {
          // DROWSY STATE - start alarm via state flag
          if (!isDrowsy) {
            console.log('[ALERT] 🚨 Backend reported drowsiness - will trigger alarm');
          }
          setIsDrowsy(true);
          setFaceState('drowsy');
          setWasAlertActive(true);
          setStatus('🚨 WAKE UP! DROWSINESS DETECTED!');
        } else {
          if (isDrowsy) {
            console.log('[ALERT] ✅ Backend cleared drowsiness - stopping alarm');
          }
          setIsDrowsy(false);
          setFaceState('locked');
          
          // Dynamic status based on drowsiness score and message
          const score = result.drowsy_score || 0;
          const msg = result.message || '';
          
          if (msg === 'Recovered!' || msg === 'Recovering...') {
            setStatus(`✅ ${msg}`);
          } else if (score > 60) {
            setStatus('⚠️ Warning - Getting very drowsy!');
          } else if (score > 40) {
            setStatus('⚠️ Face Locked - Eyes getting heavy...');
          } else if (score > 20) {
            setStatus('✅ Face Locked - Slight fatigue detected');
          } else if (msg === 'Eyes heavy...') {
            setStatus('✅ Face Locked - Monitoring...');
          } else {
            setStatus('✅ Face Locked - Alert and monitoring');
          }
        }
      } else {
        if (isDrowsy || wasAlertActive) {
          console.log('[ALERT] ⚠️ Face lost - forcing alarm stop');
        }
        
        setIsDrowsy(false);
        setFaceBox(null);
        setFaceState('searching');
        setStatus(result.message || '🔍 Searching for face...');
        setDrowsyScore(0);
        setConfidence(0);
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
  }, [isDrowsy, wasAlertActive, showCalibration]);
  
  useEffect(() => {
    captureAndSendRef.current = captureAndSend;
  }, [captureAndSend]);

  // Mount effect - start camera
  useEffect(() => {
    startCamera();
    return () => {
      // Cleanup on unmount
      if (videoRef.current && videoRef.current.srcObject) {
        videoRef.current.srcObject.getTracks().forEach(track => track.stop());
      }
      
      if (detectionIntervalRef.current) {
        clearInterval(detectionIntervalRef.current);
        detectionIntervalRef.current = null;
      }
      
      stopAlert(); // Stop any playing alerts
    };
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Centralized effect to start/stop alarm based on drowsy state
  useEffect(() => {
    if (isDrowsy) {
      playAlert();
    } else {
      stopAlert();
      
      if (wasAlertActive) {
        console.log('[ALERT] 💤 Alarm recovered - resetting alert state');
        setWasAlertActive(false);
      }
    }
  }, [isDrowsy, wasAlertActive, playAlert, stopAlert]);

  return (
    <div className="App">
      {/* Alarm Indicator - Fixed position */}
      {isAlertPlaying && (
        <div className="alarm-indicator">
          ALARM PLAYING - WAKE UP!
        </div>
      )}
      
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
          
          {/* Drowsiness Confidence Meter */}
          {faceBox && (
            <div className="confidence-meter">
              <div className="confidence-label">
                <span>Drowsiness Level</span>
                <span className="confidence-value">{drowsyScore.toFixed(0)}%</span>
              </div>
              <div className="confidence-bar-container">
                <div 
                  className={`confidence-bar ${
                    drowsyScore > 70 ? 'critical' : 
                    drowsyScore > 40 ? 'warning' : 
                    drowsyScore > 20 ? 'caution' : 'safe'
                  }`}
                  style={{ width: `${Math.min(drowsyScore, 100)}%` }}
                >
                  <div className="confidence-bar-glow"></div>
                </div>
              </div>
              <div className="confidence-legend">
                <span className="legend-item safe">Safe (0-20%)</span>
                <span className="legend-item caution">Caution (20-40%)</span>
                <span className="legend-item warning">Warning (40-70%)</span>
                <span className="legend-item critical">Critical (70-100%)</span>
              </div>
            </div>
          )}
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
            <summary>🔍 Debug Info & Intelligent Detection Guide</summary>
            <div className="debug-content">
              <h4>🧠 Intelligent Detection Features:</h4>
              <ul>
                <li>✓ <strong>Blink Detection:</strong> Automatically ignores normal blinks (under 0.4 seconds)</li>
                <li>✓ <strong>Temporal Smoothing:</strong> Uses rolling average to reduce false alerts</li>
                <li>✓ <strong>Drowsiness Score:</strong> 0-100 scale that decays gradually when eyes open</li>
                <li>✓ <strong>Confirmation Period:</strong> Must maintain high score for 2.5 seconds before alert</li>
                <li>✓ <strong>Grace Period:</strong> 3-second recovery time after opening eyes</li>
              </ul>
              
              <h4>Current Settings:</h4>
              <ul>
                <li>EAR Threshold: 0.27 (eyes potentially closing)</li>
                <li>Alert EAR: 0.32 (definitely alert)</li>
                <li>Detection Speed: 1 second per frame</li>
                <li>Alert Trigger: Score ≥ 70/100 for 2.5 seconds</li>
                <li>Score Decay: 15% per frame when eyes open</li>
              </ul>
              
              <h4>How It Works:</h4>
              <ul>
                <li><strong>Normal Blink:</strong> Detected and ignored - score unchanged</li>
                <li><strong>Eyes Closing:</strong> Score increases by 15-22 points per frame</li>
                <li><strong>Eyes Opening:</strong> Score decays gradually (15-25% per frame)</li>
                <li><strong>Alert Trigger:</strong> Score stays above 70 for 2.5 seconds</li>
                <li><strong>Recovery:</strong> 3-second grace period prevents re-alerting</li>
              </ul>
              
              <h4>Troubleshooting:</h4>
              <ul>
                <li><strong>Not detecting drowsiness?</strong> Check if your EAR drops below 0.27 when drowsy (use calibration)</li>
                <li><strong>Still getting false alerts?</strong> Improve lighting - backend logs will show blink detection</li>
                <li><strong>Yellow box stuck?</strong> Ensure good frontal lighting and face camera directly</li>
                <li><strong>Detection too sensitive?</strong> Check console - normal blinks should be detected</li>
              </ul>
              
              <h4>Optimal Conditions:</h4>
              <ul>
                <li>✓ Good frontal lighting (not backlit)</li>
                <li>✓ Face camera directly at eye level</li>
                <li>✓ Remove glasses if detection is poor</li>
                <li>✓ Keep head relatively stable</li>
                <li>✓ Distance: 1-2 feet from camera</li>
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
