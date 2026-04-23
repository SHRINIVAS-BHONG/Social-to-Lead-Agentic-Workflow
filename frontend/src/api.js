const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await res.json().catch(() => ({ detail: "Unknown error" }));
  if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);
  return data;
}

// ── Chat ──────────────────────────────────────────────────────────────────────
export async function sendMessage(message, sessionId) {
  return request("/chat", {
    method: "POST",
    body: JSON.stringify({ message, session_id: sessionId }),
  });
}

// ── Auth ──────────────────────────────────────────────────────────────────────
export async function checkRegistrationToken(token) {
  return request(`/auth/check-token/${token}`);
}

export async function registerUser(token, password, socialAccounts) {
  return request("/auth/register", {
    method: "POST",
    body: JSON.stringify({ token, password, social_accounts: socialAccounts }),
  });
}

export async function loginUser(email, password) {
  return request("/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export async function getProfile(sessionToken) {
  return request(`/auth/profile?session_token=${sessionToken}`);
}

export async function connectSocial(sessionToken, platform, username, password) {
  return request("/auth/connect-social", {
    method: "POST",
    body: JSON.stringify({
      session_token: sessionToken,
      platform,
      username,
      password,
    }),
  });
}

export async function checkUserExists(email) {
  return request(`/auth/check-user/${encodeURIComponent(email)}`);
}

export async function checkHealth() {
  return request("/health");
}
