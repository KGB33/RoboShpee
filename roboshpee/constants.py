import os
from pathlib import Path
from typing import Final

import discord

BASE_DIR: Final = Path(__file__).parent
PREFIX: Final = os.getenv("BOT_PREFIX", "!3.")
BOT_ID: Final = int(os.getenv("BOT_ID", "536718941964468245"))

# Logging Trace Level
TRACE_LEVEL: Final = 5

# Role IDs
OWNER: Final = 536732291918200842
MASTER_SHPEE: Final = 279665426718392320
ELDER_SHPEE: Final = 757592645185962074
SENOR_SHPEE: Final = 791704460308119563

# @game Role color
TOGGLEABLE_GAME_ROLE_COLOR: Final = discord.Color.dark_blue()
