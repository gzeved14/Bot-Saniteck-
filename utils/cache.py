from time import time

_cache = {}

def get_cache(key):
    if key in _cache:
        value, exp = _cache[key]
        if time() < exp:
            return value
    return None

def set_cache(key, value, ttl=60):
    _cache[key] = (value, time() + ttl)