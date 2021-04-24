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
        Usefull for when your support sucks.
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
        await ctx.send(
            f"The estimated taco time is about {random.randint(2, 5) * delta}mins"
        )
    await ctx.send(file=discord.File(dir_))


def setup(bot: Bot) -> None:
    bot.add_command(cs)
    bot.add_command(taco_time)
