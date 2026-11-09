// Offline support for the home-screen app.
// Page and data: network first (always fresh when online), saved copy when offline.
// Icons and manifest: saved copy first.
const CACHE = "scanner-v2";
const SHELL = ["./", "index.html", "manifest.json", "icon-192.png", "icon-512.png", "icon-180.png"];

self.addEventListener("install", (e) => {
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", (e) => {
  e.waitUntil(caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
    .then(() => self.clients.claim()));
});

async function networkFirst(req) {
  const cache = await caches.open(CACHE);
  try {
    // A page navigation can't be re-issued with options (it throws), which made
    // v1 serve its saved copy of the page forever; fetch the URL instead.
    const res = await fetch(req.mode === "navigate" ? req.url : req, { cache: "no-store" });
    if (res.ok) cache.put(req, res.clone());
    return res;
  } catch (err) {
    const hit = await cache.match(req, { ignoreSearch: true });
    if (!hit) throw err;
    const headers = new Headers(hit.headers);
    headers.set("X-From-Cache", "1");
    return new Response(await hit.blob(), { status: 200, headers });
  }
}

self.addEventListener("fetch", (e) => {
  const url = new URL(e.request.url);
  if (e.request.method !== "GET" || url.origin !== self.location.origin) return;  // GitHub API, CDN: untouched
  if (/\.(png|json)$/.test(url.pathname) && !url.pathname.endsWith("data.json")) {
    e.respondWith(caches.match(e.request).then((hit) => hit || fetch(e.request)));
  } else {
    e.respondWith(networkFirst(e.request));
  }
});
