import React, { useState, useEffect } from "react";
import LandingPage from "./LandingPage";
import Chat from "./Chat";
import Auth from "./Auth";
import Register from "./Register";
import "./App.css";

function App() {
  const [page, setPage] = useState("loading"); // loading | landing | auth | register | chat
  const [authMode, setAuthMode] = useState("signin");
  const [user, setUser] = useState(null);
  const [regToken, setRegToken] = useState(null);

  // On mount: check for /register/:token URL or saved session
  useEffect(() => {
    const path = window.location.pathname;
    const registerMatch = path.match(/^\/register\/([a-f0-9]+)$/i);

    if (registerMatch) {
      setRegToken(registerMatch[1]);
      setPage("register");
      return;
    }

    // Check saved session
    const savedToken = localStorage.getItem("autostream_token");
    const savedUser = localStorage.getItem("autostream_user");
    if (savedToken && savedUser) {
      try {
        const userData = JSON.parse(savedUser);
        setUser(userData);
        setPage("chat");
        return;
      } catch {
        localStorage.removeItem("autostream_token");
        localStorage.removeItem("autostream_user");
      }
    }

    setPage("landing");
  }, []);

  function handleAuthSuccess(userData) {
    setUser(userData);
    setPage("chat");
    window.history.pushState({}, "", "/");
  }

  function handleRegisterSuccess(userData) {
    // After registration, go to sign in
    localStorage.setItem("autostream_user", JSON.stringify(userData));
    setUser(userData);
    setPage("chat");
    window.history.pushState({}, "", "/");
  }

  function handleLogout() {
    localStorage.removeItem("autostream_token");
    localStorage.removeItem("autostream_user");
    setUser(null);
    setPage("landing");
  }

  if (page === "loading") return (
    <div style={{
      height: "100vh", display: "flex", alignItems: "center", justifyContent: "center",
      background: "#0a0a0f", color: "rgba(255,255,255,0.5)", fontSize: "1rem",
    }}>
      <span className="loading" style={{ marginRight: "0.75rem" }}></span>
      Loading AutoStream...
    </div>
  );

  return (
    <div className="app">
      {page === "landing" && (
        <LandingPage
          onSignIn={() => { setAuthMode("signin"); setPage("auth"); }}
          onSignUp={() => { setAuthMode("signup"); setPage("auth"); }}
        />
      )}

      {page === "auth" && (
        <Auth
          mode={authMode}
          onAuthSuccess={handleAuthSuccess}
          onBack={() => setPage("landing")}
        />
      )}

      {page === "register" && (
        <Register
          token={regToken}
          onSuccess={handleRegisterSuccess}
          onBack={() => { setPage("landing"); window.history.pushState({}, "", "/"); }}
        />
      )}

      {page === "chat" && (
        <Chat user={user} onLogout={handleLogout} />
      )}
    </div>
  );
}

export default App;
