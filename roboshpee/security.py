import functools


def minimum_role_permission(role_id: int):
    """
    Used as a decorator to determine if a user has a high
    enough role to use the command.
    """

    def wrapper(func):
        @functools.wraps(func)
        async def wrapped(ctx, *args, **kwargs):
            role = ctx.guild.get_role(role_id)
            if ctx.author.roles[-1] >= role:
                return await func(ctx, *args, **kwargs)
            else:
                return await ctx.send("You do not have permission to use this command.")

        return wrapped

    return wrapper


def requires_exact_role(role_id: int):
    def wrapper(func):
        @functools.wraps(func)
        async def wrapped(ctx, *args, **kwargs):
            role = ctx.guild.get_role(role_id)
            if role in ctx.author.roles:
                return await func(ctx, *args, **kwargs)
            else:
                return await ctx.send("You do not have permission to use this command.")

        return wrapped

    return wrapper
