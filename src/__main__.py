import os

from src import bot
from src import log

TOKEN = os.getenv("DISCORD_TOKEN")
if TOKEN is None:
    log.error("DISCORD_TOKEN environment variable is not set")
    raise EnvironmentError("DISCORD_TOKEN is not set")
try:
    bot.run(TOKEN)
except Exception as e:
    log.error(f"Fatal exception {e}, exiting now...", exc_info=True)

