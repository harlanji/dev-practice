# Cache: Evict Least Recently Used (LRU) Files

The cache is files that have previously been read, saved so future reads will be more efficient.

There is a quota that defines the amount of data that can be cached.

When a new entry is going to be added to the cache and it will exceed the quota,
the LRU items are deleted until there will be space to store the new item.

Individual items can have a max age as well, determined by the cache server and a local option.

## Use Cases

* Sync videos (and sets) for offline use without having to worry about cleaning up.

A video may be watched once and forgotten about a new videos are added the next time online,
while sets may be played every day. The former would be automatically deleted soon,
while the latter would remain on disk day after day.


## Implementation

The cached file is stored with a hashed name that won't be overwritten except by
a file from the same location. It contains the response body is it would be 
downloaded by a browser

Adjacent, there is a file that contains a JSON dict of HTTP response headers, as
well as some X- headers added by the caching proxy.

When a new file is to be written we purge the cache. The purge method takes
a parameter with the amount of space we need freed--this could be the 
Content-Length of a new item to be cached or additional bytes received if 
C.-L. was not accurate.


## Related Work

There is a Requests-Cache plugin that seems to cover many of our bases, but hashed
no concept of quota or least recently used purging. We could add that onto the
existing code base for our purposes.

https://requests-cache.readthedocs.io/en/stable/user_guide/expiration.html#precedence

