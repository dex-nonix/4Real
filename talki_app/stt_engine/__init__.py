import logging

from .colored_formatter import ColoredFormatter
log_level = logging.INFO
logger = logging.getLogger('AsyncSTTLogger')
logger.setLevel(log_level)
console_handler = logging.StreamHandler()
console_handler.setLevel(log_level)
formatter = ColoredFormatter('%(asctime)s | %(levelname)s | %(message)s', datefmt='%H:%M:%S')
console_handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(console_handler)

