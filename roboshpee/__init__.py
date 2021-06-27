from typing import TYPE_CHECKING

from roboshpee import log

if TYPE_CHECKING:
    from roboshpee.bot import Bot

log.setup()

instance: "Bot" = None  # Global Bot instance