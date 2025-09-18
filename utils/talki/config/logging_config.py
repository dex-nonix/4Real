"""
Logging configuration with colored output formatter.
"""

import logging
import colorama
from talki.utils.constants import LOG_FORMAT, LOG_DATE_FORMAT, LOG_LEVEL

# Initialize colorama for colored console output
colorama.init()


class ColoredFormatter(logging.Formatter):
    """
    Custom logging formatter that adds emojis and colors to log levels.
    """
    def format(self, record):
        if record.levelno == logging.INFO:
            record.levelname = f"ℹ️  {record.levelname}"
        elif record.levelno == logging.WARNING:
            record.levelname = f"⚠️  {record.levelname}"
        elif record.levelno == logging.ERROR:
            record.levelname = f"❌ {record.levelname}"
        elif record.levelno == logging.DEBUG:
            record.levelname = f"🔍 {record.levelname}"
        return super().format(record)


def setup_logger(name: str = 'TalkiLogger') -> logging.Logger:
    """
    Set up and configure the application logger.

    Args:
        name: Name for the logger instance

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL))

    # Remove existing handlers to avoid duplicates
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, LOG_LEVEL))

    # Create and set formatter
    formatter = ColoredFormatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    console_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(console_handler)

    return logger


# Global logger instance
logger = setup_logger()
