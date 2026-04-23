import React, { useState } from "react";
import { loginUser, checkUserExists } from "./api";

export default function Auth({ mode: initialMode, onAuthSuccess, onBack }) {
  const [mode, setMode] = useState(initialMode); // signin | signup
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: "", text: "" });

  function switchMode(newMode) {
    setMode(newMode);
    setEmail("");
    setPassword("");
    setMessage({ type: "", text: "" });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setMessage({ type: "", text: "" });

    if (!email || !password) {
      setMessage({ type: "error", text: "Please fill in all fields" });
      return;
    }
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setMessage({ type: "error", text: "Please enter a valid email address" });
      return;
    }

    setLoading(true);
    try {
      if (mode === "signin") {
        // Real login
        const result = await loginUser(email, password);
        // Save session token
        localStorage.setItem("autostream_token", result.token);
        localStorage.setItem("autostream_user", JSON.stringify(result.user));
        setMessage({ type: "success", text: "Signed in successfully!" });
        setTimeout(() => onAuthSuccess(result.user), 800);

      } else {
        // Sign up — check if user already registered
        const check = await checkUserExists(email).catch(() => ({ exists: false }));
        if (check.exists) {
          setMessage({ type: "error", text: "An account with this email already exists. Please sign in." });
          setLoading(false);
          return;
        }
        setMessage({
          type: "success",
          text: "To create an account, chat with our AI assistant and provide your details. You'll receive an activation email!",
        });
      }
    } catch (err) {
      setMessage({ type: "error", text: err.message || "Authentication failed. Please try again." });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-page">
      <button className="back-button" onClick={onBack}>← Back to Home</button>

      <div className="auth-container">
        <div className="auth-header">
          <h1 className="auth-title">
            {mode === "signin" ? "Welcome Back" : "Join AutoStream"}
          </h1>
          <p className="auth-subtitle">
            {mode === "signin"
              ? "Sign in to your AutoStream account"
              : "New here? Chat with our AI to get started — you'll receive an activation email."}
          </p>
        </div>

        {message.text && (
          <div className={`message ${message.type}`}>{message.text}</div>
        )}

        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Email Address</label>
            <input type="email" className="form-input" placeholder="Enter your email"
              value={email} onChange={e => setEmail(e.target.value)} disabled={loading} />
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <input type="password" className="form-input" placeholder="Enter your password"
              value={password} onChange={e => setPassword(e.target.value)} disabled={loading} />
          </div>

          <button type="submit" className="btn btn-primary auth-submit" disabled={loading}>
            {loading
              ? <><span className="loading"></span>{mode === "signin" ? "Signing In..." : "Checking..."}</>
              : mode === "signin" ? "Sign In" : "Check Account"
            }
          </button>
        </form>

        <div className="auth-switch">
          {mode === "signin" ? (
            <>Don't have an account?{" "}
              <button onClick={() => switchMode("signup")}>Sign Up</button>
            </>
          ) : (
            <>Already have an account?{" "}
              <button onClick={() => switchMode("signin")}>Sign In</button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
