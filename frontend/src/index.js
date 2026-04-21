import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";

/* Global CSS reset */
const globalStyle = document.createElement("style");
globalStyle.innerHTML = `
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #f8fafc; }

  /* Typing indicator dots */
  span[style*="inline-flex"] span {
    display: inline-block;
    width: 7px; height: 7px;
    border-radius: 50%;
    background: #9ca3af;
    animation: bounce 1.2s infinite;
  }
  span[style*="inline-flex"] span:nth-child(2) { animation-delay: 0.2s; }
  span[style*="inline-flex"] span:nth-child(3) { animation-delay: 0.4s; }

  @keyframes bounce {
    0%, 60%, 100% { transform: translateY(0); }
    30%            { transform: translateY(-6px); }
  }

  textarea:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.15);
  }
`;
document.head.appendChild(globalStyle);

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
