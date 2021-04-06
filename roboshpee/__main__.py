import os

from roboshpee import bot, log


if TOKEN := os.getenv("DISCORD_TOKEN"):
    log.info("Starting Bot.")
    try:
        bot.run(TOKEN)
    except Exception as e:
        log.error(f"Fatal Exception {e}, exiting now...", exc_info=True)
elif TOKEN is None:
    log.error("DISCORD_TOKEN environment variable is not set, exiting now...")
    raise EnvironmentError("DISCORD_TOKEN is not set.")
