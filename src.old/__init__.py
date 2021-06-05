from pathlib import Path
import logging
import os

from discord.ext import commands
import redis

BASE_DIR = Path(__file__).parent
PREFIX = os.getenv("BOT_PREFIX", "!3.")

# Set up logger
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)
handler = logging.FileHandler("33bot.log")
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
log.addHandler(handler)


# Set up Redis
db = redis.Redis()


bot = commands.Bot(command_prefix=PREFIX)


@bot.event
async def on_ready():
    log.info("Logged Successfully")
    log.info(f"Bot Name: {bot.user.name}")
    log.info(f"Bot ID: {bot.user.id}")
    log.info(f"With {PREFIX=}")


# set up opus to use voice
# discord.opus.load_opus('libopus-0.x86.dll')
