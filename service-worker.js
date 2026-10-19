const CACHE_NAME = "willow-app-2026-10-19e";
// Paket T1 (18.10.2026): Willow und Willow 2014 (Ordner 2014/) liegen auf derselben Domain und teilen sich Cache Storage.
// Jede App räumt nur ihre eigenen Caches auf (Präfix bis „-app-“: "willow-app-" bzw. "willow14-app-") und liest nur aus dem eigenen.
const CACHE_PFX = CACHE_NAME.replace(/-app-.*$/, "-app-");

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
      Promise.all(keys.filter(k => k !== CACHE_NAME && k.startsWith(CACHE_PFX)).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

// Selbstheilung (Paket T1): fehlt eine App-Datei im eigenen Cache (z. B. weil ein alter Worker der anderen App ihn gelöscht hat),
// wird sie beim nächsten Online-Abruf wieder abgelegt.
const OWN_URLS = new Set(FILES_TO_CACHE.map(u => new URL(u, self.registration.scope).href));
self.addEventListener("fetch", event => {
  event.respondWith(
    caches.open(CACHE_NAME).then(cache => cache.match(event.request).then(cached => cached || fetch(event.request).then(resp => {
      if (event.request.method === "GET" && resp && resp.ok && OWN_URLS.has(event.request.url)) cache.put(event.request, resp.clone());
      return resp;
    })))
  );
});
