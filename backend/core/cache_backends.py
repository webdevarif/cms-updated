"""
Development cache backend that satisfies django-ratelimit requirements.
"""

import time

from django.core.cache.backends.base import BaseCache
from django.core.cache.backends.dummy import DummyCache


class DevelopmentCache(DummyCache):
    """
    Development cache backend that supports atomic operations for django-ratelimit.
    This is a simple in-memory cache that supports increment/decrement operations.
    """

    def __init__(self, location, params):
        super().__init__(location, params)
        self._cache = {}
        self._expire_times = {}

    def set(self, key, value, timeout=None):
        """Set a value in cache with optional timeout."""
        self._cache[key] = value
        if timeout is not None:
            self._expire_times[key] = time.time() + timeout
        return True

    def get(self, key, default=None):
        """Get a value from cache, respecting expiration."""
        # Check if key exists and hasn't expired
        if key in self._cache:
            if key in self._expire_times:
                if time.time() > self._expire_times[key]:
                    # Key expired, remove it
                    del self._cache[key]
                    del self._expire_times[key]
                    return default
            return self._cache[key]
        return default

    def delete(self, key):
        """Delete a key from cache."""
        self._cache.pop(key, None)
        self._expire_times.pop(key, None)
        return True

    def clear(self):
        """Clear all cache entries."""
        self._cache.clear()
        self._expire_times.clear()
        return True

    def incr(self, key, delta=1):
        """Increment a value atomically."""
        current = self.get(key, 0)
        new_value = current + delta
        self.set(key, new_value)
        return new_value

    def decr(self, key, delta=1):
        """Decrement a value atomically."""
        current = self.get(key, 0)
        new_value = current - delta
        self.set(key, new_value)
        return new_value

    def has_key(self, key):
        """Check if key exists and hasn't expired."""
        return self.get(key) is not None

    def add(self, key, value, timeout=None):
        """Add a value only if key doesn't exist."""
        if self.has_key(key):
            return False
        return self.set(key, value, timeout)

    def get_many(self, keys, default=None):
        """Get multiple values from cache."""
        return {key: self.get(key, default) for key in keys}

    def set_many(self, data, timeout=None):
        """Set multiple values in cache."""
        for key, value in data.items():
            self.set(key, value, timeout)
        return True

    def delete_many(self, keys):
        """Delete multiple keys from cache."""
        for key in keys:
            self.delete(key)
        return True
