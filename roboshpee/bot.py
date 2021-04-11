import logging

from discord.ext import commands

from roboshpee import constants

log = logging.getLogger("bot")


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def create(cls) -> "Bot":
        return cls(command_prefix=commands.when_mentioned_or(constants.PREFIX))

    def load_extentions(self) -> None:
        """
        Used to load commands, Cogs, Groups, etc...
        from the modules found by roboshpee.extentions
        """
        from roboshpee.extentions import EXTENSIONS

        extentions = set(EXTENSIONS)
        for extention in extentions:
            self.load_extension(extention)


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
