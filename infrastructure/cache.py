from django.core.cache import cache


class CacheHandler:
    def __init__(self):
        self.cache_backend = cache

    def get(self, key):
        return self.cache_backend.get(key)

    def set(self, key, value, timeout=None):
        self.cache_backend.set(key, value, timeout)

    def delete(self, key):
        self.cache_backend.delete(key)

    def clear(self):
        self.cache_backend.clear()


def cache_key_generator(prefix, identifier):
    return f"{prefix}:{identifier}"


def cache_decorator(timeout=300):
    def decorator(func):
        def wrapper(*args, **kwargs):
            cache_key = cache_key_generator(func.__name__, str(args) + str(kwargs))
            cached_result = cache.get(cache_key)
            if cached_result:
                return cached_result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result

        return wrapper

    return decorator
