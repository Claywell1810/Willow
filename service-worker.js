const CACHE_NAME = "willow-app-2026-10-03d";

const FILES_TO_CACHE = [
  "./",
  "./index.html",
  "./manifest.json",
  "./willow-icon-192.png",
  "./willow-icon-512.png"
];

self.addEventListener("install", event => {
  event.waitUntil(
    // cache: "reload" = immer frisch vom Server, nie aus dem Browser-Cache (sonst landet ggf. die alte index.html im neuen Cache)
    caches.open(CACHE_NAME).then(cache => cache.addAll(FILES_TO_CACHE.map(u => new Request(u, { cache: "reload" }))))
  );
  self.skipWaiting();
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", event => {
  event.respondWith(
    caches.match(event.request).then(cached => cached || fetch(event.request))
  );
});
