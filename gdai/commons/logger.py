from __future__ import annotations

import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from dotenv import load_dotenv

load_dotenv(override=True)

logging.getLogger("sqlalchemy").setLevel(logging.ERROR)
logging.getLogger("sqlalchemy.engine").setLevel(logging.ERROR)
logging.getLogger("chonkie").setLevel(logging.ERROR)
logging.getLogger("tqdm").setLevel(logging.ERROR)
logging.getLogger("rich.progress").setLevel(logging.ERROR)


class ColorFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[41m",  # Red background
    }
    RESET = "\033[0m"
    GDAI_COLOR = "\033[33m"  # Yellow for 'gdai'

    def format(self, record):
        # Color by level
        level_color = self.COLORS.get(record.levelname, "")
        msg = super().format(record)
        return f"{level_color}{msg}{self.RESET}"


# Disable existing handlers from the root logger
logging.getLogger().handlers = []


class ModulePathFilter(logging.Filter):
    """Filter that adds module path information to log records"""

    def filter(self, record: logging.LogRecord) -> bool:
        # Ensure module_path exists to satisfy formatter fields
        try:
            module_name = getattr(record, "module", None) or "unknown_module"
            pathname = getattr(record, "pathname", None) or ""
            record.module_path = f"{module_name}:{record.lineno}" if record.lineno else module_name
            # Fallback: include file path when available
            if pathname and module_name not in pathname:
                record.module_path = f"{pathname}:{record.lineno}"
        except Exception:
            # Never break logging due to filter issues
            record.module_path = "unknown:0"
        return True


# Create the GDAI logger
GDAI_LOG_LEVEL = os.getenv("GDAI_LOG_LEVEL", "INFO").upper()
if GDAI_LOG_LEVEL not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
    raise ValueError(f"Invalid GDAI_LOG_LEVEL: {GDAI_LOG_LEVEL}. Must be one of DEBUG, INFO, WARNING, ERROR, CRITICAL.")

# Get log format from environment or use default
GDAI_LOG_FORMAT = os.getenv(
    "GDAI_LOG_FORMAT",
    "[%(asctime)s] [GDAI] [%(module_path)s] [%(levelname)s]: %(message)s",
)
GDAI_LOG_FILE_ENABLED = os.getenv("GDAI_LOG_FILE_ENABLED", "false").lower() == "true"

gdai_logger = logging.getLogger("GDAI")
gdai_logger.setLevel(GDAI_LOG_LEVEL)


# Remove any existing handlers
for handler in gdai_logger.handlers[:]:
    gdai_logger.removeHandler(handler)

# Add a custom filter
gdai_logger.addFilter(ModulePathFilter())


# Custom formatter for time formatting (avoid assigning to method directly)
class CustomFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        result = super().formatTime(record, datefmt)
        return result[:-3]  # Remove last 3 digits of microseconds


# Create formatter with configurable format
formatter = ColorFormatter(GDAI_LOG_FORMAT, "%Y-%m-%d %H:%M:%S")

# Add console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
gdai_logger.addHandler(console_handler)

# Add file handler if enabled
if GDAI_LOG_FILE_ENABLED:
    try:
        log_file_path = os.getenv("GDAI_LOG_FILE_PATH", "/tmp/gdai.log")
        max_bytes = int(float(os.getenv("GDAI_LOG_FILE_MAX_SIZE_MB", "10")) * 1024 * 1024)
        backup_count = int(os.getenv("GDAI_LOG_FILE_BACKUP_COUNT", "5"))

        # Ensure log directory exists
        log_dir = os.path.dirname(log_file_path)
        os.makedirs(log_dir, exist_ok=True)

        file_handler = RotatingFileHandler(log_file_path, maxBytes=max_bytes, backupCount=backup_count)
        file_handler.setFormatter(formatter)
        gdai_logger.addHandler(file_handler)
    except Exception as e:
        # Use console handler to report file handler initialization error
        console_handler.setFormatter(formatter)
        gdai_logger.addHandler(console_handler)
        gdai_logger.error(f"Failed to initialize file logging: {e}")

gdai_logger.propagate = False


class Logger:
    """Singleton logger class that delegates to the configured GDAI logger"""

    _instance = None

    def __new__(cls):
        """Ensure only one instance of Logger exists"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the logger instance (only once)"""
        if self._initialized:
            return
        self._initialized = True

    def info(self, message):
        """Log info message"""
        gdai_logger.info(message)

    def warning(self, message):
        """Log warning message"""
        gdai_logger.warning(message)

    def error(self, message):
        """Log error message"""
        gdai_logger.error(message)

    def debug(self, message):
        """Log debug message"""
        gdai_logger.debug(message)

    def critical(self, message):
        """Log critical message"""
        gdai_logger.critical(message)

    def exception(self, message, *args, exc_info=True, **kwargs):
        """Log exception information with traceback.

        Should be called from an exception handler.

        Args:
            message: The message to log
            *args: Variable arguments for message formatting
            exc_info: Boolean indicating if exception info should be added, defaults to True
            **kwargs: Additional logger parameters
        """
        gdai_logger.error(message, *args, exc_info=exc_info, **kwargs)


# Create a singleton logger instance
logger = Logger()
