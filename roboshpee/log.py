import logging
import sys
from logging import handlers

from roboshpee.constants import BASE_DIR, TRACE_LEVEL


def setup() -> None:
    """Set up loggers."""
    logging.TRACE = TRACE_LEVEL
    logging.addLevelName(TRACE_LEVEL, "TRACE")

    # log_level = TRACE_LEVEL if constants.DEBUG_MODE else logging.INFO
    log_level = logging.INFO
    format_string = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    log_format = logging.Formatter(format_string)

    log_file = BASE_DIR / "logs" / "roboshpee.log"
    log_file.parent.mkdir(exist_ok=True)
    file_handler = handlers.RotatingFileHandler(
        log_file, maxBytes=5242880, backupCount=7, encoding="utf8"
    )
    file_handler.setFormatter(log_format)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(log_format)

    root_log = logging.getLogger()
    root_log.setLevel(log_level)
    root_log.addHandler(file_handler)
    root_log.addHandler(stdout_handler)

    logging.getLogger("discord").setLevel(logging.WARNING)
    logging.getLogger("bot").setLevel(logging.INFO)

    # Uncomment / add more as needed
    # logging.getLogger("websockets").setLevel(logging.WARNING)
    # logging.getLogger("chardet").setLevel(logging.WARNING)
    # logging.getLogger("async_rediscache").setLevel(logging.WARNING)

    # Set back to the default of INFO even if asyncio's debug mode is enabled.
    # logging.getLogger("asyncio").setLevel(logging.INFO)
