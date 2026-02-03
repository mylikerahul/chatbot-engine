import logging
import sys
from datetime import datetime
from typing import Optional
from app.core.config import get_settings

class ANSIColor:
    DEBUG = "\033[36m"
    INFO = "\033[32m"
    WARNING = "\033[33m"
    ERROR = "\033[31m"
    CRITICAL = "\033[35m"
    RESET = "\033[0m"

    @classmethod
    def get(cls, level_name: str) -> str:
        return getattr(cls, level_name, cls.RESET)

class ConsoleFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        color = ANSIColor.get(record.levelname)
        reset = ANSIColor.RESET
        
        message = f"[{timestamp}] {color}{record.levelname:8}{reset} | {record.name} | {record.getMessage()}"
        
        if record.exc_info:
            message += f"\n{self.formatException(record.exc_info)}"
        
        return message

class LogConfig:
    """
    Configuration manager for logging. 
    Allows setting up global handlers once.
    """
    _setup_done = False

    @classmethod
    def setup(cls):
        if cls._setup_done:
            return

        settings = get_settings()
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, settings.log_level.upper()))
        
        if not root_logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(ConsoleFormatter())
            root_logger.addHandler(handler)
        
        cls._setup_done = True

class AppLogger:
    """
    Wrapper around Python's native logger to provide a consistent interface.
    """
    def __init__(self, name: str = "shopbuddy"):
        # Ensure configuration is applied globally at least once
        LogConfig.setup()
        self._logger = logging.getLogger(name)

    def debug(self, message: str, **kwargs):
        self._logger.debug(message, **kwargs)

    def info(self, message: str, **kwargs):
        self._logger.info(message, **kwargs)

    def warning(self, message: str, **kwargs):
        self._logger.warning(message, **kwargs)

    def error(self, message: str, **kwargs):
        self._logger.error(message, **kwargs)

    def critical(self, message: str, **kwargs):
        self._logger.critical(message, **kwargs)

    def exception(self, message: str, **kwargs):
        self._logger.exception(message, **kwargs)