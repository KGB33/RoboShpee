import asyncio
import logging
import os

from roboshpee.bot import Bot
from roboshpee.log import setup as logging_setup

logging_setup()
log = logging.getLogger(name="bot")


def main():
    if TOKEN := os.getenv("DISCORD_TOKEN"):
        log.info("Starting Bot.")
        try:
            instance = Bot.create()
            asyncio.run(instance.load_extentions())
            instance.run(TOKEN)
        except Exception as e:
            log.error(f"Fatal Exception {e}, exiting now...", exc_info=True)
    elif TOKEN is None:
        log.error("DISCORD_TOKEN environment variable is not set, exiting now...")
        raise EnvironmentError("DISCORD_TOKEN is not set.")


if __name__ == "__main__":
    main()
