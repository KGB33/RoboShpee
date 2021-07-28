import datetime
import functools


async def msg_owner(ctx, message: str):
    if ctx.guild.owner is None:
        owner = await ctx.guild.fetch_member(ctx.guild.owner_id)
    else:
        owner = ctx.guild.owner
    await owner.send(message)


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
