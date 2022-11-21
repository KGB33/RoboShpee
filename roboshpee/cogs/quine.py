import os
from pathlib import Path

import discord
from cashews import cache
from discord.ext import commands
from fuzzywuzzy import process
from prettytable import MARKDOWN, PrettyTable

from roboshpee.bot import Bot
from roboshpee.constants import BASE_DIR


@commands.command()
async def quine(ctx, file_name: str = "quine.py"):
    valid_files = await _generate_valid_files()
    file_match = process.extractOne(file_name, valid_files.keys(), score_cutoff=75)
    if file_match is None:
        return await ctx.send(
            "Could not find the provided file name. Please try again."
        )
    file_path = valid_files[file_match[0]]
    with open(file_path) as file_:
        return await ctx.send(file=discord.File(file_))


@commands.command()
async def quineables(ctx) -> None:
    """
    Displays a list of files printable with
    the quine command
    """
    table = await _quineables()
    return await ctx.send(f"```\n{table.get_string()}\n```")


async def _quineables(path: Path = BASE_DIR) -> PrettyTable:
    table = PrettyTable()
    table.align = "c"
    table.field_names = ["File Name", "File Path"]
    table.set_style(MARKDOWN)
    files = await _generate_valid_files(path)
    for f, p in files.items():
        table.add_row([f, p])
    return table


@cache(ttl="1h")
async def _generate_valid_files(path: Path = BASE_DIR) -> dict[str, Path]:
    result = dict()
    for root, _, files in os.walk(path):
        for f in files:
            if f.endswith(".py"):
                result.update({f: Path(root) / f})
    return result


async def setup(bot: Bot) -> None:
    bot.add_command(quine)
    bot.add_command(quineables)
