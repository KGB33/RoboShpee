import logging
import os

from discord.ext import commands


def create_bot():
    # get Env Vars
    if (PREFIX := os.environ["BOT_PREFIX"]) is None:
        PREFIX = "!3."

    # Set up logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler("33bot.log")
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Set up discord bot
    bot = commands.Bot(command_prefix=PREFIX)

    @bot.event
    async def on_ready():
        print("Logged Successfully")
        print(f"Bot Name: {bot.user.name}")
        print(f"Bot ID: {bot.user.id}")
        print(f"With {PREFIX=}")
        print("--------------\n\n")

    # set up opus to use voice
    # discord.opus.load_opus('libopus-0.x86.dll')

    # Register Commands
    from src.commands import (
        golden_gun,
        quote,
        random_num,
        roles,
        toggle_role,
        hello,
        heros,
        shaxx,
        thanks,
        echo,
    )

    bot.add_command(golden_gun)
    bot.add_command(quote)
    bot.add_command(random_num)
    bot.add_command(roles)
    bot.add_command(toggle_role)
    bot.add_command(hello)
    bot.add_command(heros)
    bot.add_command(shaxx)
    bot.add_command(thanks)
    bot.add_command(echo)

    return bot


bot = create_bot()
