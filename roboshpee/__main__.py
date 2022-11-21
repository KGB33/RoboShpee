import asyncio
import logging
import os

from roboshpee.bot import Bot
from roboshpee.log import setup as logging_setup

logging_setup()
log = logging.getLogger(name="bot")


async def main():
    if TOKEN := os.getenv("DISCORD_TOKEN"):
        log.info("Starting Bot.")
        instance = Bot.create()
        try:
            log.info("Logging in...")
            await instance.login(TOKEN)
            log.info("Loading Cogs...")
            await instance.load_extentions()
            log.info("Connecting...")
            await instance.connect()
            log.info("Done!")
        except Exception as e:
            log.error(f"Fatal Exception {e}, exiting now...", exc_info=True)
        finally:
            log.info("Clearing Command Tree...")
            await instance.clear_commands()
            await instance.close()

    elif TOKEN is None:
        log.error("DISCORD_TOKEN environment variable is not set, exiting now...")
        raise EnvironmentError("DISCORD_TOKEN is not set.")


if __name__ == "__main__":
    asyncio.run(main())
