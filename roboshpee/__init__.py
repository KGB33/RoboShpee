from pathlib import Path
import os
from typing import TYPE_CHECKING

from roboshpee import log

if TYPE_CHECKING:
    from roboshpee.bot import Bot

BASE_DIR = Path(__file__).parent
PREFIX = os.getenv("BOT_PREFIX", "!3.")

log.setup()

instance: Bot = None  # Global Bot instance
