import os
from pathlib import Path
from typing import Final

BASE_DIR: Final = Path(__file__).parent
PREFIX: Final = os.getenv("BOT_PREFIX", "!3.")

# Logging Trace Level
TRACE_LEVEL: Final = 5

# Role IDs
MASTER_SHPEE: Final = 279665426718392320
ELDER_SHPEE: Final = 757592645185962074
SENOR_SHPEE: Final = 791704460308119563
