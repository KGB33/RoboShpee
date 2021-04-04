from pathlib import Path
import os
import sys
import logging
from datetime import datetime

from discord.ext import commands

BASE_DIR = Path(__file__).parent
PREFIX = os.getenv("BOT_PREFIX", "!3.")

# ================ Logger Setup ================
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
formatter = logging.Formatter("\n\n%(asctime)s - %(levelname)s - \n\t%(message)s")
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(logging.INFO)
stdout_handler.setFormatter(formatter)
log.addHandler(stdout_handler)
"""
file_handler = logging.FileHandler(
    BASE_DIR / "logs" / f"{datetime.now()}_roboshpee.log"
)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
log.addHandler(file_handler)
"""


def bot_factory(prefix=PREFIX):
    bot = commands.Bot(command_prefix=prefix)

    @bot.event
    async def on_ready():
        log.info(
            f"Started Successfully at {datetime.now()} UTC"
            f"\n\tWith name: {bot.user.name}"
            f"\n\tWith ID: {bot.user.id}"
            f"\n\t and Prefix '{PREFIX}'"
        )

    return bot
