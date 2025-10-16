import functools
import logging
import os
import time
from datetime import datetime, timezone, timedelta
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

LOG_DIR = "./logs"
LOG_FILE = os.path.join(LOG_DIR, "audio_downloader.log")

os.makedirs(LOG_DIR, exist_ok=True)


class ISTFormatter(logging.Formatter):
    """Custom formatter to use Indian Standard Time (IST) for logs."""

    def formatTime(self, record, datefmt=None):
        ist_time = datetime.now(timezone.utc) + timedelta(hours=5, minutes=30)
        return ist_time.strftime(datefmt if datefmt else "%Y-%m-%d %H:%M:%S")


def get_logger(name="default"):
    logger = logging.getLogger(name)

    if not logger.hasHandlers():  # Avoid duplicate handlers
        logger.setLevel(logging.INFO)

        # Console handler (logs to terminal)
        console_handler = logging.StreamHandler()
        console_formatter = ISTFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        # File handler (logs to file with rotation)
        file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=3)  # 5MB max per file
        file_formatter = ISTFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    return logger


def timing_decorator(label=None):
    """Decorator to measure execution time using perf_counter with an optional label."""

    def decorator(func):
        LOGGER = get_logger('AudioDownloader')

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            end_time = time.perf_counter()
            elapsed_time = end_time - start_time
            log_label = label if label else func.__name__
            LOGGER.info(f"{log_label} completed in {elapsed_time:.6f} seconds")
            return result

        return wrapper

    return decorator

