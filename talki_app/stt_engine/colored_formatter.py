import logging
import colorama
colorama.init()

class ColoredFormatter(logging.Formatter):
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
