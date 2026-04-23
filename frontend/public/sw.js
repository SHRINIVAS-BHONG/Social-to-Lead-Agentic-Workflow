// AutoStream Service Worker - Minimal PWA support
const CACHE_NAME = 'autostream-v2';

self.addEventListener('install', (event) => {
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

// Network-first for everything — no aggressive caching that breaks dev
self.addEventListener('fetch', (event) => {
  const { request } = event;

  // Skip non-GET and WebSocket
  if (request.method !== 'GET') return;
  if (request.url.startsWith('ws:') || request.url.startsWith('wss:')) return;
  // Skip hot-reload requests
  if (request.url.includes('hot-update')) return;

  event.respondWith(
    fetch(request).catch(() => caches.match(request))
  );
});
