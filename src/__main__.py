import os

from src import bot

TOKEN = os.environ["DISCORD_TOKEN"]
bot.run(TOKEN)
