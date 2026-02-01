"""
Professional logging system with structured output.
Provides consistent logging across all services.
"""

import logging
import sys
from datetime import datetime
from typing import Optional
from app.core.config import get_settings


class LogFormatter(logging.Formatter):
    """Custom formatter with color support for console output."""
    
    COLORS = {
        "DEBUG": "\033[36m",
        "INFO": "\033[32m",
        "WARNING": "\033[33m",
        "ERROR": "\033[31m",
        "CRITICAL": "\033[35m",
        "RESET": "\033[0m"
    }
    
    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        level = record.levelname
        color = self.COLORS.get(level, self.COLORS["RESET"])
        reset = self.COLORS["RESET"]
        
        message = f"[{timestamp}] {color}{level:8}{reset} | {record.name} | {record.getMessage()}"
        
        if record.exc_info:
            message += f"\n{self.formatException(record.exc_info)}"
        
        return message


class Logger:
    """
    Singleton logger class providing consistent logging interface.
    """
    
    _instances: dict = {}
    
    def __new__(cls, name: str = "shopbuddy") -> "Logger":
        if name not in cls._instances:
            instance = super().__new__(cls)
            instance._initialize(name)
            cls._instances[name] = instance
        return cls._instances[name]
    
    def _initialize(self, name: str) -> None:
        self._name = name
        self._logger = logging.getLogger(name)
        
        settings = get_settings()
        self._logger.setLevel(getattr(logging, settings.log_level.upper()))
        
        if not self._logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(LogFormatter())
            self._logger.addHandler(handler)
    
    def debug(self, message: str, **kwargs) -> None:
        self._logger.debug(message, **kwargs)
    
    def info(self, message: str, **kwargs) -> None:
        self._logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs) -> None:
        self._logger.warning(message, **kwargs)
    
    def error(self, message: str, **kwargs) -> None:
        self._logger.error(message, **kwargs)
    
    def critical(self, message: str, **kwargs) -> None:
        self._logger.critical(message, **kwargs)
    
    def exception(self, message: str, **kwargs) -> None:
        self._logger.exception(message, **kwargs)