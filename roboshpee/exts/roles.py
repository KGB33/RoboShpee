from discord.ext import commands

from roboshpee.bot import Bot


@commands.group()
async def role(ctx):
    if ctx.invoked_subcommand is None:
        await ctx.send("Invalid role command passed...")


@role.command()
async def add(ctx, *roles):
    """
    Add yourself to the supplied roles.
    """
    print(f"Added: {roles}")


@role.command
async def remove(ctx, *roles):
    """
    Remove yourself from the supplied roles.
    """
    print(f"removed: {roles}")


def setup(bot: Bot) -> None:
    bot.add_command(role)
