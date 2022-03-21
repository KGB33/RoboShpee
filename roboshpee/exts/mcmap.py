from typing import Literal

from discord.ext import commands

from roboshpee.bot import Bot


@commands.command()
async def mcmap(
    ctx,
    x: int,
    z: int,
    world: str = "world",
    mapname: str = "flat",
    zoom: int = 4,
    y: int = 64,
):
    """
    Creates a link to the map of the Minecraft world with the given coordinates.

    world: Literal["world", "nether", "end"] = "world",
    mapname: Literal["flat", "surface", "cave"] = "flat",
    """
    world_name = {
        "world": "world",
        "nether": "world_nether",
        "end": "world_the_end",
    }[world]
    return await ctx.send(
        f"https://mcmap.kgb33.dev/?worldname={world_name}&mapname={mapname}&zoom={zoom}&x={x}&y={y}&z={z}"
    )


def setup(bot: Bot) -> None:
    bot.add_command(mcmap)
