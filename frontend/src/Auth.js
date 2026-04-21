import React, { useState } from "react";

const Auth = ({ mode, onAuthSuccess, onBack }) => {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: ""
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: "", text: "" });

  const handleInputChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage({ type: "", text: "" });

    // Basic validation
    if (mode === "signup") {
      if (!formData.name || !formData.email || !formData.password || !formData.confirmPassword) {
        setMessage({ type: "error", text: "Please fill in all fields" });
        setLoading(false);
        return;
      }
      if (formData.password !== formData.confirmPassword) {
        setMessage({ type: "error", text: "Passwords don't match" });
        setLoading(false);
        return;
      }
      if (formData.password.length < 6) {
        setMessage({ type: "error", text: "Password must be at least 6 characters" });
        setLoading(false);
        return;
      }
    } else {
      if (!formData.email || !formData.password) {
        setMessage({ type: "error", text: "Please fill in all fields" });
        setLoading(false);
        return;
      }
    }

    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      setMessage({ type: "error", text: "Please enter a valid email address" });
      setLoading(false);
      return;
    }

    // Simulate API call
    try {
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Mock successful authentication
      const userData = {
        id: Date.now(),
        name: formData.name || formData.email.split('@')[0],
        email: formData.email,
        avatar: `https://ui-avatars.com/api/?name=${encodeURIComponent(formData.name || formData.email)}&background=667eea&color=fff`
      };

      setMessage({ type: "success", text: `${mode === "signup" ? "Account created" : "Signed in"} successfully!` });
      
      setTimeout(() => {
        onAuthSuccess(userData);
      }, 1000);
      
    } catch (error) {
      setMessage({ type: "error", text: "Authentication failed. Please try again." });
    } finally {
      setLoading(false);
    }
  };

  const switchMode = () => {
    setFormData({ name: "", email: "", password: "", confirmPassword: "" });
    setMessage({ type: "", text: "" });
    // This would typically be handled by parent component
    window.location.reload(); // Simple way to switch modes
  };

  return (
    <div className="auth-page">
      <button className="back-button" onClick={onBack}>
        ← Back to Home
      </button>
      
      <div className="auth-container">
        <div className="auth-header">
          <h1 className="auth-title">
            {mode === "signup" ? "Join AutoStream" : "Welcome Back"}
          </h1>
          <p className="auth-subtitle">
            {mode === "signup" 
              ? "Create your account and start creating amazing videos"
              : "Sign in to continue your creative journey"
            }
          </p>
        </div>

        {message.text && (
          <div className={`message ${message.type}`}>
            {message.text}
          </div>
        )}

        <form className="auth-form" onSubmit={handleSubmit}>
          {mode === "signup" && (
            <div className="form-group">
              <label className="form-label">Full Name</label>
              <input
                type="text"
                name="name"
                className="form-input"
                placeholder="Enter your full name"
                value={formData.name}
                onChange={handleInputChange}
                disabled={loading}
              />
            </div>
          )}

          <div className="form-group">
            <label className="form-label">Email Address</label>
            <input
              type="email"
              name="email"
              className="form-input"
              placeholder="Enter your email"
              value={formData.email}
              onChange={handleInputChange}
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <input
              type="password"
              name="password"
              className="form-input"
              placeholder="Enter your password"
              value={formData.password}
              onChange={handleInputChange}
              disabled={loading}
            />
          </div>

          {mode === "signup" && (
            <div className="form-group">
              <label className="form-label">Confirm Password</label>
              <input
                type="password"
                name="confirmPassword"
                className="form-input"
                placeholder="Confirm your password"
                value={formData.confirmPassword}
                onChange={handleInputChange}
                disabled={loading}
              />
            </div>
          )}

          <button 
            type="submit" 
            className="btn btn-primary auth-submit"
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="loading"></span>
                {mode === "signup" ? "Creating Account..." : "Signing In..."}
              </>
            ) : (
              mode === "signup" ? "Create Account" : "Sign In"
            )}
          </button>
        </form>

        <div className="auth-switch">
          {mode === "signup" ? (
            <>
              Already have an account?{" "}
              <button onClick={() => window.location.href = "/?mode=signin"}>
                Sign In
              </button>
            </>
          ) : (
            <>
              Don't have an account?{" "}
              <button onClick={() => window.location.href = "/?mode=signup"}>
                Sign Up
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default Auth;