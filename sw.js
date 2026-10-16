// Change the version number each time you update index.html, so phones get the new version.
const CACHE = 'scorer-v1';
const CORE = ['./', 'index.html', 'manifest.json', 'icon-192.png', 'icon-512.png'];
const BIG = ['vosk.js', 'model.tar.gz'];

self.addEventListener('install', (e) => {
  e.waitUntil((async () => {
    const c = await caches.open(CACHE);
    await c.addAll(CORE);
    for (const f of BIG) {
      try { await c.add(f); } catch (x) { /* file missing: skip */ }
    }
    await self.skipWaiting();
  })());
});

self.addEventListener('activate', (e) => {
  e.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)));
    await self.clients.claim();
  })());
});

self.addEventListener('fetch', (e) => {
  if (e.request.method !== 'GET') return;
  e.respondWith(
    caches.match(e.request, { ignoreSearch: true }).then((hit) => hit || fetch(e.request))
  );
});
