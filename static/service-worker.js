
const CACHE_NAME = "mindwell-v1";

const FILES_TO_CACHE = [
    "/",
    "/static/manifest.json",
    "/static/css/style.css"
];

// Install service worker
self.addEventListener("install", function(event) {

    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function(cache) {
                return cache.addAll(FILES_TO_CACHE);
            })
    );

    self.skipWaiting();
});

// Activate service worker
self.addEventListener("activate", function(event) {

    event.waitUntil(
        self.clients.claim()
    );
});

// Handle requests
self.addEventListener("fetch", function(event) {

    // Only cache GET requests from this origin
    if (event.request.method !== "GET") {
        return;
    }

    event.respondWith(
        fetch(event.request).catch(function() {
            return caches.match(event.request);
        })
    );

});
