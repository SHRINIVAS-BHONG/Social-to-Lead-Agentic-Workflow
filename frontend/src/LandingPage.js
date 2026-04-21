import React from "react";

const LandingPage = ({ onSignIn, onSignUp }) => {
  return (
    <div className="landing-page">
      {/* Header */}
      <header className="header">
        <div className="logo">
          AutoStream
        </div>
        <div className="auth-buttons">
          <button className="btn btn-outline" onClick={onSignIn}>
            Sign In
          </button>
          <button className="btn btn-primary" onClick={onSignUp}>
            Sign Up
          </button>
        </div>
      </header>

      {/* Hero Section */}
      <section className="hero">
        <div className="hero-content">
          <h1 className="hero-title">
            Transform Your Content with{" "}
            <span className="gradient-text">AI Magic</span>
          </h1>
          <p className="hero-subtitle">
            AutoStream revolutionizes video editing for content creators. 
            Create stunning videos in minutes with our AI-powered platform. 
            From YouTube to TikTok, we've got your creative journey covered.
          </p>
          <div className="hero-cta">
            <button className="btn btn-primary btn-hero" onClick={onSignUp}>
              Start Creating Free
            </button>
            <button className="btn btn-outline btn-hero" onClick={onSignIn}>
              Watch Demo
            </button>
          </div>
        </div>

        <div className="hero-image">
          <div className="hero-visual">
            <div className="visual-content">
              <div className="visual-icon">🎬</div>
              <div className="visual-text">AI-Powered Video Editing</div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;