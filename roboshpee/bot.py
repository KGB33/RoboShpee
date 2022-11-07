import asyncio
import logging

from discord import Intents
from discord.ext import commands

from roboshpee import constants

log = logging.getLogger("bot")


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def create(cls) -> "Bot":
        intents = Intents.default()
        intents.message_content = True
        return cls(
            intents=intents, command_prefix=commands.when_mentioned_or(constants.PREFIX)
        )

    async def load_extentions(self) -> None:
        """
        Used to load commands, Cogs, Groups, etc...
        from the modules found by roboshpee.extentions
        """
        from roboshpee.extentions import EXTENSIONS

        extentions = set(EXTENSIONS)
        async with asyncio.TaskGroup() as tg:
            for extention in extentions:
                tg.create_task(self.load_extension(extention))
