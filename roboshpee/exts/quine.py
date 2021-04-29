from typing import Optional
import os
from pathlib import Path

import discord
from discord.ext import commands
from fuzzywuzzy import process
from prettytable import PrettyTable

from roboshpee.constants import BASE_DIR
from roboshpee.bot import Bot


@commands.command()
async def quine(ctx, file_name: Optional[str] = "quine.py"):
    VALID_FILES = _generate_valid_files()
    file_name, ratio = process.extractOne(file_name, VALID_FILES.keys())
    if ratio < 75:
        return await ctx.send(
            f"Closest file name is `{file_name}` ({ratio}% match)please try again"
        )
    file_path = VALID_FILES[file_name]
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


def _generate_valid_files():
    result = dict()
    for root, dirs, files in os.walk(BASE_DIR):
        for f in files:
            if f.endswith(".py"):
                result.update({f: Path(root) / f})
    return result


def setup(bot: Bot) -> None:
    bot.add_command(quine)
    bot.add_command(quineables)
