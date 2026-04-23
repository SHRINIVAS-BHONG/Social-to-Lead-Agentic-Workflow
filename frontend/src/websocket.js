// WebSocket utility for real-time streaming
class StreamingWebSocket {
  constructor() {
    this.ws = null;
    this.isConnected = false;
    this.messageHandlers = new Map();
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 3;
    this.destroyed = false;
    this.connectPromise = null;
  }

  connect() {
    // Return existing promise if already connecting
    if (this.connectPromise) return this.connectPromise;
    if (this.isConnected) return Promise.resolve();

    this.connectPromise = new Promise((resolve, reject) => {
      if (this.destroyed) return reject(new Error('destroyed'));
      try {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.hostname}:8000/ws`;

        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
          console.log('🔗 WebSocket connected');
          this.isConnected = true;
          this.reconnectAttempts = 0;
          this.connectPromise = null;
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
          }
        };

        this.ws.onclose = () => {
          console.log('🔌 WebSocket disconnected');
          this.isConnected = false;
          this.connectPromise = null;
          if (!this.destroyed) this.attemptReconnect();
        };

        this.ws.onerror = () => {
          this.connectPromise = null;
          reject(new Error('WebSocket connection failed'));
        };

      } catch (error) {
        this.connectPromise = null;
        reject(error);
      }
    });

    return this.connectPromise;
  }

  attemptReconnect() {
    if (this.destroyed) return;
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      setTimeout(() => {
        if (!this.destroyed) this.connect().catch(() => {});
      }, 2000 * this.reconnectAttempts);
    }
  }

  handleMessage(data) {
    const handlers = this.messageHandlers.get(data.type) || [];
    handlers.forEach(handler => handler(data));
  }

  on(type, handler) {
    if (!this.messageHandlers.has(type)) {
      this.messageHandlers.set(type, []);
    }
    this.messageHandlers.get(type).push(handler);
  }

  off(type, handler) {
    const handlers = this.messageHandlers.get(type) || [];
    const index = handlers.indexOf(handler);
    if (index > -1) handlers.splice(index, 1);
  }

  sendMessage(message, sessionId = null) {
    if (this.isConnected && this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        message,
        session_id: sessionId,
        timestamp: new Date().toISOString(),
      }));
      return true;
    }
    return false;
  }

  disconnect() {
    this.destroyed = true;
    if (this.ws) {
      this.ws.close();
      this.ws = null;
      this.isConnected = false;
    }
  }
}

export const streamingWS = new StreamingWebSocket();

// Lazy connect — only when the chat page loads, not on every page
export function initWebSocket() {
  streamingWS.destroyed = false;
  streamingWS.connect().catch(() => {
    console.log('WebSocket unavailable, will use HTTP fallback');
  });
}

window.addEventListener('beforeunload', () => {
  streamingWS.destroyed = true;
});
