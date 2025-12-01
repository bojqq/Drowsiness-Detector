import React from 'react';
import './LandingPage.css';

function LandingPage() {
  const scrollToDetector = () => {
    const detectorSection = document.getElementById('detector-section');
    if (detectorSection) {
      detectorSection.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div className="landing-page">
      {/* Header with Logo */}
      <header className="landing-header">
        <div className="logo-container">
          <img 
            src={require('./assets/logo.png')} 
            alt="Drowsiness Detector Logo" 
            className="logo"
          />
          <span className="brand-name">DrowsyGuard</span>
        </div>
      </header>

      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">Stay Awake. Stay Alive.</h1>
          <p className="hero-subtitle">
            Drowsy driving is a silent killer on our roads
          </p>
          <p className="hero-description">
            Every year, thousands of lives are lost due to driver fatigue. 
            When you're behind the wheel, a moment of drowsiness can be the 
            difference between life and death. It's time for a solution.
          </p>
          <div className="hero-stat">
            <span className="hero-stat-number">100,000+</span>
            <span className="hero-stat-text">crashes annually due to drowsy driving in the US</span>
          </div>
          <button className="cta-button" onClick={scrollToDetector}>
            Try Our AI Detector
          </button>
        </div>
      </section>

      {/* Statistics Section */}
      <section className="stats-section">
        <div className="stats-container">
          <h2 className="section-title">The Alarming Reality</h2>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon">🚗</div>
              <span className="stat-number">6,000+</span>
              <div className="stat-label">Fatal Crashes</div>
              <p className="stat-description">
                Lives lost every year in the United States alone due to drowsy driving
              </p>
            </div>
            <div className="stat-card">
              <div className="stat-icon">⚠️</div>
              <span className="stat-number">1 in 25</span>
              <div className="stat-label">Drivers Affected</div>
              <p className="stat-description">
                Adult drivers report falling asleep while driving in the past month
              </p>
            </div>
            <div className="stat-card">
              <div className="stat-icon">😴</div>
              <span className="stat-number">3-4 Seconds</span>
              <div className="stat-label">Micro-Sleep Duration</div>
              <p className="stat-description">
                At 60mph, you travel 100 yards in just 3 seconds - enough to be fatal
              </p>
            </div>
            <div className="stat-card">
              <div className="stat-icon">🌙</div>
              <span className="stat-number">50%</span>
              <div className="stat-label">Night Risk Increase</div>
              <p className="stat-description">
                Drowsy driving crashes are more likely between midnight and 6 AM
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="how-it-works-section">
        <div className="how-it-works-container">
          <h2 className="section-title">Our AI-Powered Solution</h2>
          <p style={{ 
            textAlign: 'center', 
            fontSize: '1.2rem', 
            color: '#065f46', 
            maxWidth: '800px', 
            margin: '0 auto 20px',
            lineHeight: '1.7'
          }}>
            We've developed an intelligent drowsiness detection system using 
            advanced computer vision and machine learning to keep you safe on the road.
          </p>
          <div className="steps-grid">
            <div className="step-card">
              <div className="step-number">1</div>
              <div className="step-icon">📹</div>
              <h3 className="step-title">Real-Time Monitoring</h3>
              <p className="step-description">
                Your device's camera continuously monitors your face and eye movements 
                while you drive, with complete privacy - all processing happens locally.
              </p>
              <div className="step-tech">Web Camera API</div>
            </div>
            <div className="step-card">
              <div className="step-number">2</div>
              <div className="step-icon">🤖</div>
              <h3 className="step-title">AI Analysis</h3>
              <p className="step-description">
                Our AI calculates your Eye Aspect Ratio (EAR) using MediaPipe facial 
                landmarks. When your eyes stay closed beyond normal blinking, the system 
                detects drowsiness patterns.
              </p>
              <div className="step-tech">MediaPipe + Computer Vision</div>
            </div>
            <div className="step-card">
              <div className="step-number">3</div>
              <div className="step-icon">🚨</div>
              <h3 className="step-title">Instant Alerts</h3>
              <p className="step-description">
                The moment drowsiness is detected, you receive immediate audio and 
                visual alerts, along with actionable suggestions to help you stay awake 
                and safe.
              </p>
              <div className="step-tech">Real-Time Alerts</div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

export default LandingPage;

