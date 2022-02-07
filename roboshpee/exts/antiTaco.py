from discord.ext import commands

from roboshpee.utils import msg_owner


class AntiTacoCog(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.name != "FrostyTacos":
            return
        if message.content != "You cant just delete our messages":
            return
        await message.delete()
        await msg_owner(f"Removed a message from {message.author}.\n{message.content=}")


def setup(bot):
    bot.add_cog(AntiTacoCog(bot))
