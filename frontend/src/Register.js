import React, { useState, useEffect } from "react";
import { checkRegistrationToken, registerUser } from "./api";

const PLATFORMS = ["Instagram", "TikTok", "YouTube"];

const PLATFORM_ICONS = { Instagram: "📷", TikTok: "🎵", YouTube: "▶️" };
const PLATFORM_COLORS = {
  Instagram: "linear-gradient(45deg,#f09433,#e6683c,#dc2743,#cc2366,#bc1888)",
  TikTok: "linear-gradient(45deg,#FF0050,#00F2EA)",
  YouTube: "linear-gradient(45deg,#FF0000,#CC0000)",
};

export default function Register({ token, onSuccess, onBack }) {
  const [step, setStep] = useState("loading"); // loading | setup | social | done | error
  const [userInfo, setUserInfo] = useState(null);
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [socialAccounts, setSocialAccounts] = useState({});
  const [currentPlatform, setCurrentPlatform] = useState(null);
  const [platformInput, setPlatformInput] = useState({ username: "", password: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Validate token on mount
  useEffect(() => {
    if (!token) { setStep("error"); return; }
    checkRegistrationToken(token)
      .then(data => { setUserInfo(data); setStep("setup"); })
      .catch(() => setStep("error"));
  }, [token]);

  async function handleSetupSubmit(e) {
    e.preventDefault();
    setError("");
    if (password.length < 6) { setError("Password must be at least 6 characters"); return; }
    if (password !== confirmPassword) { setError("Passwords don't match"); return; }
    setStep("social");
  }

  function handleConnectPlatform(platform) {
    setCurrentPlatform(platform);
    setPlatformInput({ username: "", password: "" });
  }

  function handleSavePlatform() {
    if (!platformInput.username || !platformInput.password) {
      setError("Please enter username and password"); return;
    }
    setSocialAccounts(prev => ({
      ...prev,
      [currentPlatform]: {
        username: platformInput.username,
        connected: true,
        connected_at: new Date().toISOString(),
      }
    }));
    setCurrentPlatform(null);
    setError("");
  }

  async function handleFinish() {
    setLoading(true);
    setError("");
    try {
      const result = await registerUser(token, password, socialAccounts);
      onSuccess(result.user);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  // ── Render ──────────────────────────────────────────────────────────────────

  if (step === "loading") return (
    <div className="auth-page">
      <div className="auth-container" style={{ textAlign: "center" }}>
        <div className="loading" style={{ margin: "0 auto 1rem" }}></div>
        <p style={{ color: "rgba(255,255,255,0.6)" }}>Verifying your activation link...</p>
      </div>
    </div>
  );

  if (step === "error") return (
    <div className="auth-page">
      <div className="auth-container" style={{ textAlign: "center" }}>
        <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>❌</div>
        <h2 className="auth-title">Invalid Link</h2>
        <p style={{ color: "rgba(255,255,255,0.6)", marginBottom: "2rem" }}>
          This activation link is invalid or has already been used.
        </p>
        <button className="btn btn-primary" onClick={onBack}>Back to Home</button>
      </div>
    </div>
  );

  if (step === "setup") return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="auth-header">
          <div style={{ fontSize: "2.5rem", marginBottom: "0.5rem" }}>🎉</div>
          <h1 className="auth-title">Activate Your Account</h1>
          <p className="auth-subtitle">
            Welcome, <strong style={{ color: "#a5b4fc" }}>{userInfo?.name}</strong>!
            Set a password to activate your <strong style={{ color: "#a5b4fc" }}>{userInfo?.plan}</strong> plan.
          </p>
        </div>

        {/* Plan badge */}
        <div style={{
          background: "rgba(99,102,241,0.12)", border: "1px solid rgba(99,102,241,0.3)",
          borderRadius: "10px", padding: "0.875rem 1rem", marginBottom: "1.5rem",
          display: "flex", alignItems: "center", gap: "0.75rem"
        }}>
          <span style={{ fontSize: "1.5rem" }}>🚀</span>
          <div>
            <div style={{ fontWeight: 700, color: "#a5b4fc", fontSize: "0.9rem" }}>{userInfo?.plan}</div>
            <div style={{ fontSize: "0.75rem", color: "rgba(255,255,255,0.5)" }}>
              7-day free trial · {userInfo?.platform} creator
            </div>
          </div>
        </div>

        {error && <div className="message error">{error}</div>}

        <form className="auth-form" onSubmit={handleSetupSubmit}>
          <div className="form-group">
            <label className="form-label">Email</label>
            <input className="form-input" value={userInfo?.email || ""} disabled
              style={{ opacity: 0.6 }} />
          </div>
          <div className="form-group">
            <label className="form-label">Create Password</label>
            <input type="password" className="form-input" placeholder="Min. 6 characters"
              value={password} onChange={e => setPassword(e.target.value)} />
          </div>
          <div className="form-group">
            <label className="form-label">Confirm Password</label>
            <input type="password" className="form-input" placeholder="Repeat password"
              value={confirmPassword} onChange={e => setConfirmPassword(e.target.value)} />
          </div>
          <button type="submit" className="btn btn-primary auth-submit">
            Continue → Connect Social Accounts
          </button>
        </form>
      </div>
    </div>
  );

  if (step === "social") return (
    <div className="auth-page">
      <div className="auth-container" style={{ maxWidth: "520px" }}>
        <div className="auth-header">
          <div style={{ fontSize: "2rem", marginBottom: "0.5rem" }}>📱</div>
          <h1 className="auth-title">Connect Your Accounts</h1>
          <p className="auth-subtitle">
            Connect your social media accounts so AutoStream can post content automatically.
          </p>
        </div>

        {error && <div className="message error">{error}</div>}

        {/* Platform list */}
        <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem", marginBottom: "1.5rem" }}>
          {PLATFORMS.map(platform => {
            const connected = socialAccounts[platform];
            const isActive = currentPlatform === platform;
            return (
              <div key={platform}>
                <div style={{
                  display: "flex", alignItems: "center", gap: "0.875rem",
                  padding: "0.875rem 1rem",
                  background: connected ? "rgba(34,197,94,0.08)" : "rgba(255,255,255,0.04)",
                  border: `1px solid ${connected ? "rgba(34,197,94,0.3)" : isActive ? "rgba(99,102,241,0.4)" : "rgba(255,255,255,0.1)"}`,
                  borderRadius: "12px", cursor: "pointer",
                  transition: "all 0.2s ease",
                }} onClick={() => !connected && handleConnectPlatform(platform)}>
                  <div style={{
                    width: "36px", height: "36px", borderRadius: "10px",
                    background: PLATFORM_COLORS[platform],
                    display: "flex", alignItems: "center", justifyContent: "center",
                    fontSize: "1.1rem", flexShrink: 0,
                  }}>
                    {PLATFORM_ICONS[platform]}
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontWeight: 700, fontSize: "0.9rem", color: "#fff" }}>{platform}</div>
                    {connected
                      ? <div style={{ fontSize: "0.75rem", color: "#22c55e" }}>✅ {connected.username}</div>
                      : <div style={{ fontSize: "0.75rem", color: "rgba(255,255,255,0.4)" }}>Click to connect</div>
                    }
                  </div>
                  {!connected && (
                    <span style={{ fontSize: "0.75rem", color: "#6366f1", fontWeight: 600 }}>
                      {isActive ? "▲" : "Connect →"}
                    </span>
                  )}
                </div>

                {/* Inline connect form */}
                {isActive && (
                  <div style={{
                    padding: "1rem", background: "rgba(99,102,241,0.06)",
                    border: "1px solid rgba(99,102,241,0.2)", borderTop: "none",
                    borderRadius: "0 0 12px 12px",
                  }}>
                    <div style={{ marginBottom: "0.75rem" }}>
                      <label className="form-label" style={{ fontSize: "0.78rem" }}>
                        {platform} Username / Handle
                      </label>
                      <input className="form-input" placeholder={`@your_${platform.toLowerCase()}_handle`}
                        value={platformInput.username}
                        onChange={e => setPlatformInput(p => ({ ...p, username: e.target.value }))}
                        style={{ marginTop: "0.35rem" }} />
                    </div>
                    <div style={{ marginBottom: "0.875rem" }}>
                      <label className="form-label" style={{ fontSize: "0.78rem" }}>
                        {platform} Password
                      </label>
                      <input type="password" className="form-input" placeholder="Your password"
                        value={platformInput.password}
                        onChange={e => setPlatformInput(p => ({ ...p, password: e.target.value }))}
                        style={{ marginTop: "0.35rem" }} />
                    </div>
                    <div style={{ display: "flex", gap: "0.5rem" }}>
                      <button className="btn btn-primary" style={{ flex: 1, padding: "0.6rem" }}
                        onClick={handleSavePlatform}>
                        Connect {platform}
                      </button>
                      <button className="btn btn-outline" style={{ padding: "0.6rem 1rem" }}
                        onClick={() => { setCurrentPlatform(null); setError(""); }}>
                        Cancel
                      </button>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        <div style={{ display: "flex", gap: "0.75rem" }}>
          <button className="btn btn-primary" style={{ flex: 1 }}
            onClick={handleFinish} disabled={loading}>
            {loading ? <><span className="loading"></span>Activating...</> : "🎉 Activate Account"}
          </button>
          {Object.keys(socialAccounts).length === 0 && (
            <button className="btn btn-outline" style={{ padding: "0.875rem 1.25rem" }}
              onClick={handleFinish} disabled={loading}>
              Skip
            </button>
          )}
        </div>
        <p style={{ textAlign: "center", fontSize: "0.75rem", color: "rgba(255,255,255,0.35)", marginTop: "0.75rem" }}>
          You can connect more accounts later from your profile.
        </p>
      </div>
    </div>
  );

  return null;
}
