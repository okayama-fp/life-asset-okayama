var CACHE = 'pap-v1';
var STATIC = ['/'];

self.addEventListener('install', function (e) {
  e.waitUntil(
    caches.open(CACHE).then(function (c) { return c.addAll(STATIC); })
  );
  self.skipWaiting();
});

self.addEventListener('activate', function (e) {
  e.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(
        keys.filter(function (k) { return k !== CACHE; }).map(function (k) { return caches.delete(k); })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', function (e) {
  var url = e.request.url;

  // Let external API calls (market data, news) go through the network always
  if (url.includes('yahoo.com') || url.includes('rss2json.com') || url.includes('nhk.or.jp')) {
    return;
  }

  // Network-first for HTML, cache fallback for offline
  if (e.request.mode === 'navigate') {
    e.respondWith(
      fetch(e.request)
        .then(function (r) {
          var clone = r.clone();
          caches.open(CACHE).then(function (c) { c.put(e.request, clone); });
          return r;
        })
        .catch(function () { return caches.match('/'); })
    );
    return;
  }

  // Cache-first for other static assets
  e.respondWith(
    caches.match(e.request).then(function (cached) {
      return cached || fetch(e.request);
    })
  );
});
