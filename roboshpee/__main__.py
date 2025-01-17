import asyncio
import logging
import os

from roboshpee.bot import Bot

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
            log.info("Syncing Commands...")
            await instance.tree.sync()
            log.info("Connecting...")
            await instance.connect()
            log.info("Done!")
        except Exception as e:
            log.error(f"Fatal Exception {e}, exiting now...", exc_info=True)
        finally:
            log.info("Clearing Command Tree...")
            # Pod termination delay causes new pod's commands to be removed.
            if os.getenv("KUBERNETES_SERVICE_HOST") is None:
                await instance.clear_commands()
            await instance.close()

    elif TOKEN is None:
        log.error("DISCORD_TOKEN environment variable is not set, exiting now...")
        raise EnvironmentError("DISCORD_TOKEN is not set.")


if __name__ == "__main__":
    asyncio.run(main())
