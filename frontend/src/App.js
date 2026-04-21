import React, { useState } from "react";
import LandingPage from "./LandingPage";
import Chat from "./Chat";
import Auth from "./Auth";
import "./App.css";

function App() {
  const [currentPage, setCurrentPage] = useState("landing"); // landing, auth, chat
  const [authMode, setAuthMode] = useState("signin"); // signin, signup
  const [user, setUser] = useState(null);

  const handleSignIn = () => {
    setAuthMode("signin");
    setCurrentPage("auth");
  };

  const handleSignUp = () => {
    setAuthMode("signup");
    setCurrentPage("auth");
  };

  const handleAuthSuccess = (userData) => {
    setUser(userData);
    setCurrentPage("chat");
  };

  const handleLogout = () => {
    setUser(null);
    setCurrentPage("landing");
  };

  const handleBackToLanding = () => {
    setCurrentPage("landing");
  };

  return (
    <div className="app">
      {currentPage === "landing" && (
        <LandingPage 
          onSignIn={handleSignIn}
          onSignUp={handleSignUp}
        />
      )}
      
      {currentPage === "auth" && (
        <Auth 
          mode={authMode}
          onAuthSuccess={handleAuthSuccess}
          onBack={handleBackToLanding}
        />
      )}
      
      {currentPage === "chat" && (
        <Chat 
          user={user}
          onLogout={handleLogout}
        />
      )}
    </div>
  );
}

export default App;
