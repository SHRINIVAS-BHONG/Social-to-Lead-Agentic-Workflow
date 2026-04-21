const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

/**
 * Send a chat message to the AutoStream AI Agent backend.
 *
 * @param {string} message   - The user's message text
 * @param {string|null} sessionId - Existing session ID (null for new session)
 * @returns {Promise<{response, session_id, intent, lead_info, lead_captured}>}
 */
export async function sendMessage(message, sessionId) {
  const res = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message, session_id: sessionId }),
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(error.detail || `HTTP ${res.status}`);
  }

  return res.json();
}

/**
 * Fetch the health status of the backend.
 */
export async function checkHealth() {
  const res = await fetch(`${API_BASE_URL}/health`);
  return res.json();
}
