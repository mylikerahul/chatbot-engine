"""
Custom exception hierarchy for ShopBuddy AI.
Provides structured error handling across the application.
"""

from typing import Optional, Dict, Any


class ShopBuddyException(Exception):
    """Base exception for all ShopBuddy errors."""
    
    def __init__(
        self,
        message: str,
        code: str = "SHOPBUDDY_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "error": self.code,
            "message": self.message,
            "details": self.details
        }


class AIServiceException(ShopBuddyException):
    """Exception raised when AI service fails."""
    
    def __init__(self, message: str, provider: str = "unknown"):
        super().__init__(
            message=message,
            code="AI_SERVICE_ERROR",
            details={"provider": provider}
        )


class ScraperException(ShopBuddyException):
    """Exception raised when scraping fails."""
    
    def __init__(self, message: str, site: str = "unknown"):
        super().__init__(
            message=message,
            code="SCRAPER_ERROR",
            details={"site": site}
        )


class ValidationException(ShopBuddyException):
    """Exception raised for validation errors."""
    
    def __init__(self, message: str, field: str = "unknown"):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            details={"field": field}
        )


class ConfigurationException(ShopBuddyException):
    """Exception raised for configuration errors."""
    
    def __init__(self, message: str):
        super().__init__(
            message=message,
            code="CONFIGURATION_ERROR"
        )