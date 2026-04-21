import React, { useState, useRef, useEffect } from "react";
import { sendMessage } from "./api";
import { streamingWS } from "./websocket";
import { voiceManager, isVoiceSupported, cleanTextForSpeech } from "./voice";
import "./Chat.css";

/* ─── Intent badge colours (Dark Theme) ────────────────────────────────────────────── */
const INTENT_STYLES = {
  greeting:    { bg: "rgba(59, 130, 246, 0.15)", color: "#60a5fa", label: "👋 Greeting", border: "rgba(59, 130, 246, 0.3)"    },
  inquiry:     { bg: "rgba(251, 191, 36, 0.15)", color: "#fbbf24", label: "🔍 Inquiry", border: "rgba(251, 191, 36, 0.3)"     },
  high_intent: { bg: "rgba(34, 197, 94, 0.15)", color: "#22c55e", label: "🔥 High Intent", border: "rgba(34, 197, 94, 0.3)" },
};

/* ─── Single message bubble ───────────────────────────────────────────── */
function Message({ msg }) {
  const isUser = msg.role === "user";
  return (
    <div className={`message-container ${isUser ? 'user' : 'assistant'}`}>
      {!isUser && (
        <div className="avatar assistant-avatar">
          <span>🤖</span>
        </div>
      )}
      <div className={`message-bubble ${isUser ? 'user-bubble' : 'assistant-bubble'}`}>
        <span
          dangerouslySetInnerHTML={{
            __html: msg.content
              .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
              .replace(/\n/g, "<br/>"),
          }}
        />
        <div className="message-time">{msg.time}</div>
      </div>
      {isUser && (
        <div className="avatar user-avatar">
          <span>👤</span>
        </div>
      )}
    </div>
  );
}

/* ─── Lead info panel ─────────────────────────────────────────────────── */
function LeadPanel({ leadInfo, leadCaptured }) {
  const fields = [
    { key: "name",     label: "Name", icon: "👤"     },
    { key: "email",    label: "Email", icon: "📧"    },
    { key: "platform", label: "Platform", icon: "🎬" },
  ];
  
  return (
    <div className="lead-panel">
      <div className="lead-header">
        <span className="lead-icon">{leadCaptured ? "✅" : "📋"}</span>
        <span className="lead-title">
          {leadCaptured ? "Lead Captured!" : "Lead Progress"}
        </span>
      </div>
      
      <div className="lead-fields">
        {fields.map(({ key, label, icon }) => (
          <div key={key} className="lead-field">
            <div className="lead-field-label">
              <span className="field-icon">{icon}</span>
              <span>{label}</span>
            </div>
            <div className={`lead-field-value ${leadInfo[key] ? 'filled' : 'empty'}`}>
              {leadInfo[key] || "—"}
            </div>
          </div>
        ))}
      </div>
      
      {leadCaptured && (
        <div className="lead-success-badge">
          <span>🎉</span>
          <span>Successfully captured!</span>
        </div>
      )}
    </div>
  );
}

/* ─── Main Chat component ─────────────────────────────────────────────── */
export default function Chat({ user, onLogout }) {
  const [messages,     setMessages]     = useState([]);
  const [input,        setInput]        = useState("");
  const [loading,      setLoading]      = useState(false);
  const [sessionId,    setSessionId]    = useState(null);
  const [intent,       setIntent]       = useState("");
  const [leadInfo,     setLeadInfo]     = useState({});
  const [leadCaptured, setLeadCaptured] = useState(false);
  const [error,        setError]        = useState("");
  const [isStreaming,  setIsStreaming]  = useState(false);
  const [streamingMessage, setStreamingMessage] = useState("");
  const [isListening,  setIsListening]  = useState(false);
  const [isSpeaking,   setIsSpeaking]   = useState(false);
  const [voiceSupported, setVoiceSupported] = useState(false);
  const [interimTranscript, setInterimTranscript] = useState("");
  const bottomRef = useRef(null);

  /* Scroll to bottom on new messages */
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, streamingMessage]);

  /* Welcome message on mount */
  useEffect(() => {
    const userName = user?.name || "there";
    setMessages([{
      role: "assistant",
      content: `👋 Hi **${userName}**! I'm the AutoStream AI assistant. I can help you with pricing, features, and getting started. How can I help you today?`,
      time: now(),
    }]);
    
    // Check voice support
    setVoiceSupported(isVoiceSupported());
  }, [user]);

  /* Voice event handlers */
  useEffect(() => {
    voiceManager.onListeningStart = () => {
      setIsListening(true);
      setInterimTranscript("");
    };
    
    voiceManager.onListeningEnd = () => {
      setIsListening(false);
      setInterimTranscript("");
    };
    
    voiceManager.onTranscript = (final, interim) => {
      if (final) {
        setInput(final);
        setInterimTranscript("");
        // Auto-send if we got a complete sentence
        if (final.trim().length > 0) {
          setTimeout(() => handleSend(), 100);
        }
      } else {
        setInterimTranscript(interim);
      }
    };
    
    voiceManager.onSpeakStart = () => {
      setIsSpeaking(true);
    };
    
    voiceManager.onSpeakEnd = () => {
      setIsSpeaking(false);
    };
    
    voiceManager.onError = (error) => {
      setError(`Voice error: ${error}`);
      setIsListening(false);
    };
    
    return () => {
      // Cleanup voice handlers
      voiceManager.onListeningStart = null;
      voiceManager.onListeningEnd = null;
      voiceManager.onTranscript = null;
      voiceManager.onSpeakStart = null;
      voiceManager.onSpeakEnd = null;
      voiceManager.onError = null;
    };
  }, []);

  /* WebSocket event handlers */
  useEffect(() => {
    const handleTyping = () => {
      setIsStreaming(true);
      setStreamingMessage("");
      setLoading(false);
    };

    const handleStream = (data) => {
      setStreamingMessage(data.content);
      setIntent(data.intent);
      setLeadInfo(data.lead_info || {});
      if (data.lead_captured) setLeadCaptured(true);
    };

    const handleComplete = (data) => {
      setIsStreaming(false);
      setStreamingMessage("");
      
      if (!sessionId) setSessionId(data.session_id);
      setIntent(data.intent);
      setLeadInfo(data.lead_info || {});
      if (data.lead_captured) setLeadCaptured(true);

      setMessages(prev => [
        ...prev,
        { role: "assistant", content: data.content, time: now() },
      ]);
      
      // Speak the response if voice is enabled
      if (voiceSupported && !isSpeaking) {
        const cleanText = cleanTextForSpeech(data.content);
        voiceManager.speak(cleanText);
      }
    };

    const handleError = (data) => {
      setIsStreaming(false);
      setStreamingMessage("");
      setLoading(false);
      setError(data.message || "Connection error occurred");
    };

    // Register WebSocket handlers
    streamingWS.on('typing', handleTyping);
    streamingWS.on('stream', handleStream);
    streamingWS.on('complete', handleComplete);
    streamingWS.on('error', handleError);

    // Cleanup
    return () => {
      streamingWS.off('typing', handleTyping);
      streamingWS.off('stream', handleStream);
      streamingWS.off('complete', handleComplete);
      streamingWS.off('error', handleError);
    };
  }, [sessionId]);

  function now() {
    return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  }

  async function handleSend() {
    const text = input.trim();
    if (!text || loading || isStreaming) return;

    const userMsg = { role: "user", content: text, time: now() };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setLoading(true);
    setError("");

    // Try WebSocket first, fallback to HTTP
    const sent = streamingWS.sendMessage(text, sessionId);
    
    if (!sent) {
      // Fallback to HTTP API
      try {
        const data = await sendMessage(text, sessionId);

        if (!sessionId) setSessionId(data.session_id);
        setIntent(data.intent);
        setLeadInfo(data.lead_info || {});
        if (data.lead_captured) setLeadCaptured(true);

        setMessages(prev => [
          ...prev,
          { role: "assistant", content: data.response, time: now() },
        ]);
      } catch (err) {
        setError(`Error: ${err.message}`);
      } finally {
        setLoading(false);
      }
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  function handleNewChat() {
    // Reset all state to start fresh
    setMessages([{
      role: "assistant",
      content: `👋 Hi **${user?.name || "there"}**! I'm the AutoStream AI assistant. I can help you with pricing, features, and getting started. How can I help you today?`,
      time: now(),
    }]);
    setInput("");
    setSessionId(null);
    setIntent("");
    setLeadInfo({});
    setLeadCaptured(false);
    setError("");
    setIsStreaming(false);
    setStreamingMessage("");
    setIsListening(false);
    setIsSpeaking(false);
    setInterimTranscript("");
    voiceManager.stopSpeaking();
    voiceManager.stopListening();
  }

  function toggleVoiceInput() {
    if (isListening) {
      voiceManager.stopListening();
    } else {
      voiceManager.stopSpeaking(); // Stop AI speaking when user wants to talk
      voiceManager.startListening();
    }
  }

  function toggleSpeaking() {
    if (isSpeaking) {
      voiceManager.stopSpeaking();
    } else {
      // Speak the last AI message
      const lastAIMessage = messages.slice().reverse().find(msg => msg.role === 'assistant');
      if (lastAIMessage) {
        const cleanText = cleanTextForSpeech(lastAIMessage.content);
        voiceManager.speak(cleanText);
      }
    }
  }

  const intentStyle = INTENT_STYLES[intent] || {};

  return (
    <div className="chat-root">
      {/* ── Header ── */}
      <div className="chat-header">
        <div className="header-left">
          <div className="header-logo">
            <span className="logo-gradient">AutoStream</span>
          </div>
          <div className="header-info">
            <div className="header-title">AI Assistant</div>
            <div className="header-subtitle">Your intelligent video editing companion</div>
          </div>
        </div>
        
        <div className="header-right">
          {intent && (
            <div 
              className="intent-badge"
              style={{ 
                backgroundColor: intentStyle.bg, 
                color: intentStyle.color,
                border: `1px solid ${intentStyle.border}`
              }}
            >
              {intentStyle.label}
            </div>
          )}
          
          {user && (
            <div className="user-section">
              <div className="user-info">
                <div className="user-name">{user.name}</div>
                <div className="user-email">{user.email}</div>
              </div>
              <button className="logout-btn" onClick={onLogout}>
                <span>🚪</span>
                <span>Logout</span>
              </button>
            </div>
          )}
        </div>
      </div>

      {/* ── Body ── */}
      <div className="chat-body">
        {/* Messages */}
        <div className="messages-container">
          {messages.map((msg, i) => <Message key={i} msg={msg} />)}
          
          {/* Streaming message */}
          {isStreaming && streamingMessage && (
            <div className="message-container assistant">
              <div className="avatar assistant-avatar">
                <span>🤖</span>
              </div>
              <div className="message-bubble assistant-bubble streaming-bubble">
                <span
                  dangerouslySetInnerHTML={{
                    __html: streamingMessage
                      .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
                      .replace(/\n/g, "<br/>"),
                  }}
                />
                <div className="streaming-cursor">|</div>
              </div>
            </div>
          )}
          
          {loading && !isStreaming && (
            <div className="message-container assistant">
              <div className="avatar assistant-avatar">
                <span>🤖</span>
              </div>
              <div className="message-bubble assistant-bubble typing-bubble">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
          
          {error && (
            <div className="error-banner">
              <span>⚠️</span>
              <span>{error}</span>
            </div>
          )}
          
          <div ref={bottomRef} />
        </div>

        {/* Lead panel (sidebar) */}
        <LeadPanel leadInfo={leadInfo} leadCaptured={leadCaptured} />
      </div>

      {/* ── Input ── */}
      <div className="chat-input-container">
        {/* Voice controls */}
        {voiceSupported && (
          <div className="voice-controls">
            <button
              className={`voice-btn ${isListening ? 'listening' : ''}`}
              onClick={toggleVoiceInput}
              title={isListening ? "Stop listening" : "Start voice input"}
              disabled={loading || isStreaming}
            >
              <span className="voice-icon">🎤</span>
            </button>
            <button
              className={`voice-btn ${isSpeaking ? 'speaking' : ''}`}
              onClick={toggleSpeaking}
              title={isSpeaking ? "Stop speaking" : "Speak last message"}
            >
              <span className="voice-icon">🔊</span>
            </button>
          </div>
        )}
        
        <textarea
          className="chat-textarea"
          value={input + (interimTranscript ? ` ${interimTranscript}` : '')}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={isListening ? "Listening... speak now" : "Type your message... (Press Enter to send)"}
          rows={1}
          disabled={loading || isListening}
        />
        <button
          className={`send-btn ${(!input.trim() || loading || isStreaming) ? 'disabled' : ''}`}
          onClick={handleSend}
          disabled={loading || !input.trim() || isStreaming}
        >
          <span className="send-icon">✈️</span>
          <span>Send</span>
        </button>
      </div>
    </div>
  );
}
