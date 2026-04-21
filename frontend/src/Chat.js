import React, { useState, useRef, useEffect } from "react";
import { sendMessage } from "./api";

/* ─── Intent badge colours ────────────────────────────────────────────── */
const INTENT_STYLES = {
  greeting:    { bg: "#e0f2fe", color: "#0369a1", label: "👋 Greeting"    },
  inquiry:     { bg: "#fef9c3", color: "#854d0e", label: "🔍 Inquiry"     },
  high_intent: { bg: "#dcfce7", color: "#166534", label: "🔥 High Intent" },
};

/* ─── Single message bubble ───────────────────────────────────────────── */
function Message({ msg }) {
  const isUser = msg.role === "user";
  return (
    <div
      style={{
        display: "flex",
        justifyContent: isUser ? "flex-end" : "flex-start",
        marginBottom: 12,
      }}
    >
      {!isUser && (
        <div style={styles.avatar}>AS</div>
      )}
      <div
        style={{
          ...styles.bubble,
          backgroundColor: isUser ? "#6366f1" : "#ffffff",
          color:           isUser ? "#ffffff" : "#1e293b",
          borderRadius:    isUser ? "18px 18px 4px 18px" : "18px 18px 18px 4px",
          boxShadow: isUser
            ? "0 2px 8px rgba(99,102,241,0.35)"
            : "0 2px 8px rgba(0,0,0,0.08)",
        }}
      >
        {/* Render markdown-style bold (**text**) */}
        <span
          dangerouslySetInnerHTML={{
            __html: msg.content
              .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
              .replace(/\n/g, "<br/>"),
          }}
        />
        <div style={{ fontSize: 11, opacity: 0.6, marginTop: 4, textAlign: "right" }}>
          {msg.time}
        </div>
      </div>
      {isUser && (
        <div style={{ ...styles.avatar, backgroundColor: "#6366f1", marginLeft: 8, marginRight: 0 }}>
          You
        </div>
      )}
    </div>
  );
}

/* ─── Lead info panel ─────────────────────────────────────────────────── */
function LeadPanel({ leadInfo, leadCaptured }) {
  const fields = [
    { key: "name",     label: "Name"     },
    { key: "email",    label: "Email"    },
    { key: "platform", label: "Platform" },
  ];
  return (
    <div style={styles.leadPanel}>
      <div style={{ fontWeight: 700, fontSize: 13, marginBottom: 8, color: "#374151" }}>
        {leadCaptured ? "✅ Lead Captured!" : "📋 Lead Progress"}
      </div>
      {fields.map(({ key, label }) => (
        <div key={key} style={styles.leadRow}>
          <span style={{ color: "#6b7280", fontSize: 12 }}>{label}:</span>
          <span style={{ fontSize: 12, fontWeight: 600, color: leadInfo[key] ? "#166534" : "#9ca3af" }}>
            {leadInfo[key] || "—"}
          </span>
        </div>
      ))}
    </div>
  );
}

/* ─── Main Chat component ─────────────────────────────────────────────── */
export default function Chat() {
  const [messages,     setMessages]     = useState([]);
  const [input,        setInput]        = useState("");
  const [loading,      setLoading]      = useState(false);
  const [sessionId,    setSessionId]    = useState(null);
  const [intent,       setIntent]       = useState("");
  const [leadInfo,     setLeadInfo]     = useState({});
  const [leadCaptured, setLeadCaptured] = useState(false);
  const [error,        setError]        = useState("");
  const bottomRef = useRef(null);

  /* Scroll to bottom on new messages */
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  /* Welcome message on mount */
  useEffect(() => {
    setMessages([{
      role: "assistant",
      content: "👋 Hi! I'm the AutoStream AI assistant. I can help you with pricing, features, and getting started. How can I help you today?",
      time: now(),
    }]);
  }, []);

  function now() {
    return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  }

  async function handleSend() {
    const text = input.trim();
    if (!text || loading) return;

    const userMsg = { role: "user", content: text, time: now() };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setLoading(true);
    setError("");

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

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  const intentStyle = INTENT_STYLES[intent] || {};

  return (
    <div style={styles.root}>
      {/* ── Header ── */}
      <div style={styles.header}>
        <div style={styles.headerLeft}>
          <div style={styles.logo}>AS</div>
          <div>
            <div style={{ fontWeight: 700, fontSize: 16 }}>AutoStream AI</div>
            <div style={{ fontSize: 12, opacity: 0.75 }}>Powered by Claude · LangGraph</div>
          </div>
        </div>
        {intent && (
          <div style={{ ...styles.intentBadge, backgroundColor: intentStyle.bg, color: intentStyle.color }}>
            {intentStyle.label}
          </div>
        )}
      </div>

      {/* ── Body ── */}
      <div style={styles.body}>
        {/* Messages */}
        <div style={styles.messages}>
          {messages.map((msg, i) => <Message key={i} msg={msg} />)}
          {loading && (
            <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "4px 0" }}>
              <div style={styles.avatar}>AS</div>
              <div style={{ ...styles.bubble, backgroundColor: "#f3f4f6" }}>
                <span style={styles.typing}>
                  <span /><span /><span />
                </span>
              </div>
            </div>
          )}
          {error && (
            <div style={styles.errorBanner}>{error}</div>
          )}
          <div ref={bottomRef} />
        </div>

        {/* Lead panel (sidebar) */}
        <LeadPanel leadInfo={leadInfo} leadCaptured={leadCaptured} />
      </div>

      {/* ── Input ── */}
      <div style={styles.inputRow}>
        <textarea
          style={styles.textarea}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a message… (Enter to send)"
          rows={1}
          disabled={loading}
        />
        <button
          style={{
            ...styles.sendBtn,
            opacity: loading || !input.trim() ? 0.5 : 1,
            cursor:  loading || !input.trim() ? "not-allowed" : "pointer",
          }}
          onClick={handleSend}
          disabled={loading || !input.trim()}
        >
          Send
        </button>
      </div>
    </div>
  );
}

/* ─── Styles ─────────────────────────────────────────────────────────── */
const styles = {
  root: {
    display:       "flex",
    flexDirection: "column",
    height:        "100vh",
    maxWidth:      900,
    margin:        "0 auto",
    fontFamily:    "'Inter', 'Segoe UI', sans-serif",
    background:    "#f8fafc",
  },
  header: {
    display:        "flex",
    alignItems:     "center",
    justifyContent: "space-between",
    padding:        "14px 20px",
    background:     "#4f46e5",
    color:          "#fff",
    boxShadow:      "0 2px 12px rgba(79,70,229,0.4)",
  },
  headerLeft: {
    display:    "flex",
    alignItems: "center",
    gap:        12,
  },
  logo: {
    width:          40,
    height:         40,
    borderRadius:   10,
    background:     "rgba(255,255,255,0.25)",
    display:        "flex",
    alignItems:     "center",
    justifyContent: "center",
    fontWeight:     800,
    fontSize:       14,
  },
  intentBadge: {
    padding:      "4px 12px",
    borderRadius: 20,
    fontSize:     12,
    fontWeight:   600,
  },
  body: {
    display:  "flex",
    flex:     1,
    overflow: "hidden",
  },
  messages: {
    flex:         1,
    overflowY:    "auto",
    padding:      "20px 16px",
  },
  avatar: {
    width:          34,
    height:         34,
    borderRadius:   "50%",
    background:     "#e0e7ff",
    color:          "#4f46e5",
    display:        "flex",
    alignItems:     "center",
    justifyContent: "center",
    fontWeight:     700,
    fontSize:       10,
    flexShrink:     0,
    marginRight:    8,
  },
  bubble: {
    maxWidth:   "72%",
    padding:    "10px 14px",
    lineHeight: 1.5,
    fontSize:   14,
  },
  leadPanel: {
    width:         220,
    flexShrink:    0,
    borderLeft:    "1px solid #e5e7eb",
    padding:       20,
    background:    "#fff",
    overflowY:     "auto",
  },
  leadRow: {
    display:        "flex",
    justifyContent: "space-between",
    marginBottom:   8,
    gap:            6,
  },
  inputRow: {
    display:      "flex",
    gap:          10,
    padding:      "12px 16px",
    borderTop:    "1px solid #e5e7eb",
    background:   "#fff",
    alignItems:   "flex-end",
  },
  textarea: {
    flex:        1,
    padding:     "10px 14px",
    borderRadius: 12,
    border:      "1.5px solid #d1d5db",
    fontSize:    14,
    resize:      "none",
    outline:     "none",
    fontFamily:  "inherit",
    lineHeight:  1.5,
  },
  sendBtn: {
    padding:      "10px 22px",
    borderRadius: 12,
    background:   "#4f46e5",
    color:        "#fff",
    border:       "none",
    fontWeight:   700,
    fontSize:     14,
    fontFamily:   "inherit",
    flexShrink:   0,
  },
  errorBanner: {
    background:   "#fee2e2",
    color:        "#991b1b",
    padding:      "8px 14px",
    borderRadius: 8,
    fontSize:     13,
    marginTop:    8,
  },
  typing: {
    display:  "inline-flex",
    gap:      4,
  },
};
