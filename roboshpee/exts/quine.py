import os
from functools import cache
from pathlib import Path

import discord
from discord.ext import commands
from fuzzywuzzy import process
from prettytable import PrettyTable

from roboshpee.bot import Bot
from roboshpee.constants import BASE_DIR


@commands.command()
async def quine(ctx, file_name: str = "quine.py"):
    VALID_FILES = _generate_valid_files()
    file_match = process.extractOne(file_name, VALID_FILES.keys(), score_cutoff=75)
    if file_match is None:
        return await ctx.send(
            f"Could not find the provided file name. Please try again."
        )
    file_path = VALID_FILES[file_match[0]]
    with open(file_path) as file_:
        return await ctx.send(file=discord.File(file_))


@commands.command()
async def quineables(ctx) -> None:
    """
    Displays a list of files printable with
    the quine command
    """
    table = PrettyTable()
    table.align = "c"
    table.field_names = ["File Name", "File Path"]
    for f, p in _generate_valid_files().items():
        table.add_row([f, p])
    return await ctx.send(f"```\n{table.get_string()}\n```")


@cache
def _generate_valid_files() -> dict[str, Path]:
    result = dict()
    for root, _, files in os.walk(BASE_DIR):
        for f in files:
            if f.endswith(".py"):
                result.update({f: Path(root) / f})
    return result


def setup(bot: Bot) -> None:
    bot.add_command(quine)
    bot.add_command(quineables)
