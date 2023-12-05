import asyncio
import logging
import re

from discord import Intents, Message
from discord.ext import commands

from roboshpee import constants
from roboshpee import events

log = logging.getLogger("bot")


class Bot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @classmethod
    def create(cls, *args, **kwargs) -> "Bot":
        intents = Intents.default()
        intents.message_content = True
        intents.members = True
        return cls(
            intents=intents,
            command_prefix=commands.when_mentioned_or(constants.PREFIX),
            *args,
            **kwargs,
        )

    async def load_extentions(self) -> None:
        """
        Used to load commands, Cogs, Groups, etc...
        from the modules found by roboshpee.extensions
        """
        from roboshpee.extensions import EXTENSIONS

        extensions = set(EXTENSIONS)
        async with asyncio.TaskGroup() as tg:
            for extension in extensions:
                tg.create_task(self.load_extension(extension))

    async def on_connect(self):
        await self.tree.sync()

    async def on_message(self, msg: Message, /) -> None:
        if (msg.author == self.application_id) or (msg.author.bot):
            return
        if match := re.findall(r"https?://(?:twitter|x)\.com/[^.\s]+", msg.content):
            await events.on_twitter_msg(msg, match)
        return await super().on_message(msg)

    async def clear_commands(self):
        self.tree.clear_commands(guild=None)
        await self.tree.sync()
