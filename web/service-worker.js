const CACHE_NAME = "aimoneycoach-shell-v1";
const APP_SHELL = [
  "/",
  "/offline",
  "/manifest.webmanifest",
  "/favicon.svg",
  "/web/styles.css",
  "/web/app.js",
  "/web/icons/apple-touch-icon.png",
  "/web/icons/icon-192.png",
  "/web/icons/icon-512.png",
];

const API_PREFIXES = [
  "/api",
  "/auth",
  "/profile",
  "/coach",
  "/chat",
  "/recommendations",
  "/simulations",
];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(APP_SHELL)).then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys
          .filter((key) => key !== CACHE_NAME)
          .map((key) => caches.delete(key))
      )
    ).then(() => self.clients.claim())
  );
});

function isApiRequest(pathname) {
  return API_PREFIXES.some((prefix) => pathname.startsWith(prefix));
}

function shouldHandleStatic(url) {
  if (url.origin !== self.location.origin) {
    return false;
  }
  return (
    url.pathname === "/" ||
    url.pathname === "/offline" ||
    url.pathname === "/manifest.webmanifest" ||
    url.pathname === "/favicon.svg" ||
    url.pathname.startsWith("/web/")
  );
}

self.addEventListener("fetch", (event) => {
  const { request } = event;
  if (request.method !== "GET") {
    return;
  }

  const url = new URL(request.url);
  if (url.origin !== self.location.origin || isApiRequest(url.pathname)) {
    return;
  }

  if (request.mode === "navigate") {
    event.respondWith(
      fetch(request)
        .then((response) => {
          const cached = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put("/", cached));
          return response;
        })
        .catch(async () => {
          return (
            (await caches.match(request)) ||
            (await caches.match("/")) ||
            (await caches.match("/offline"))
          );
        })
    );
    return;
  }

  if (!shouldHandleStatic(url)) {
    return;
  }

  event.respondWith(
    caches.match(request).then((cachedResponse) => {
      const networkFetch = fetch(request)
        .then((response) => {
          const cloned = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(request, cloned));
          return response;
        })
        .catch(() => cachedResponse);

      return cachedResponse || networkFetch;
    })
  );
});
