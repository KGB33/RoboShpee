import datetime
import functools


def ttl_cache(ttl=datetime.timedelta(minutes=3)):
    def wrap(func):
        cache = {}

        @functools.wraps(func)
        def wrapped(*args, **kw):
            now = datetime.datetime.now()
            key = tuple(args), frozenset(kw.items())
            if key not in cache or now - cache[key][0] > ttl:
                value = func(*args, **kw)
                cache[key] = (now, value)
            return cache[key][1]

        return wrapped

    return wrap
