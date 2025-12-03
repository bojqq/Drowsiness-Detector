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

      {/* Minimal Hero Section */}
      <section className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">AI-Powered Drowsiness Detection</h1>
          <button className="cta-button" onClick={scrollToDetector}>
            Start Detection
          </button>
        </div>
      </section>
    </div>
  );
}

export default LandingPage;

