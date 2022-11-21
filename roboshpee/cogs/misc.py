import asyncio
import random
from typing import Optional

import discord
from discord.ext import commands

from roboshpee.bot import Bot
from roboshpee.constants import BASE_DIR


@commands.command()
async def cs(ctx):
    """
    Displays a Creep Score flow chart.
        Useful for when your support sucks.
    """
    dir_ = (
        BASE_DIR
        / "static"
        / random.choice(("bella_cs_chart.png", "magnizar_cs_chart.png"))
    )
    return await ctx.send(file=discord.File(dir_))


@commands.command()
async def taco_time(ctx, delta: Optional[int]):
    """
    Takes a duration (in mins) and translates it to taco_time
    """
    dir_ = BASE_DIR / "static" / "taco_time.png"
    if delta is not None:
        scaled_delta = random.gammavariate(2, 2) * delta
        await ctx.send(f"The estimated taco time is about {scaled_delta:.2g}mins")
    await ctx.send(file=discord.File(dir_))


@commands.command()
async def rtd(ctx, sides: int = 2):
    """
    Roll a 'dice' with some number of sides.
    """
    await ctx.send(f"{random.randint(1, sides)}")


@commands.command()
async def quote(ctx):
    """
    Fetches a random quote from the #quotes channel
    """
    quotes_channel = discord.utils.get(ctx.guild.channels, name="quotes")
    quote = random.choice(
        [q async for q in discord.iterators.HistoryIterator(quotes_channel, 200)]
    )
    await ctx.send(quote.content)


@commands.command()
async def timer(
    ctx, delta: int, timer_name: Optional[str], *users: Optional[discord.User]
):
    """
    Pings the caller and the optional users after a give time.
    Timers are lost if the bot crashes or restarts.

    Param 'delta' is the time in mins.
    """
    await ctx.send(f"Timer {timer_name} set for {delta} mins.")
    if not users:
        users = ()
    mentions = " ".join(u.mention for u in users)
    mentions = f"{ctx.author.mention} {mentions}"
    await asyncio.sleep(delta * 60)
    await ctx.send(f"Timer {timer_name} Done! {mentions}")


async def setup(bot: Bot) -> None:
    bot.add_command(cs)
    bot.add_command(taco_time)
    bot.add_command(quote)
    bot.add_command(timer)
    bot.add_command(rtd)
