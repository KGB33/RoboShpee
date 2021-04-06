import logging

from discord.ext import commands

from roboshpee import PREFIX

log = logging.getLogger("bot")


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def create(cls) -> "Bot":
        return cls(command_prefix=commands.when_mentioned_or(PREFIX))


"""
@bot.event
async def on_ready():
    log.info(
        f"Started Successfully at {datetime.now()} UTC"
        f"\n\tWith name: {bot.user.name}"
        f"\n\tWith ID: {bot.user.id}"
        f"\n\t and Prefix '{PREFIX}'"
    )
    return bot
"""
