import os
from pathlib import Path

BASE_DIR = Path(__file__).parent
PREFIX = os.getenv("BOT_PREFIX", "!3.")

# Logging Trace Level
TRACE_LEVEL = 5
