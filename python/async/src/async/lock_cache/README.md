# Lock Cache

Concurrent calls to an async function with a cache.
Without a lock, the calls all go through at the same time.
With a lock, the first call creates the cache and the next ones use it.
