"""
Enumeration types for ShopBuddy AI.
Provides type-safe constants for various categories.
"""

from enum import Enum


class IntentType(str, Enum):
    """User intent classification types."""
    
    GREETING = "greeting"
    FAREWELL = "farewell"
    THANKS = "thanks"
    HELP = "help"
    PRODUCT_FILTER = "product_filter"
    PRODUCT_COMPARE = "product_compare"
    PRODUCT_INFO = "product_info"
    PRICE_QUERY = "price_query"
    SUMMARIZE = "summarize"
    GENERAL_QUESTION = "general_question"
    CLEAR_CHAT = "clear_chat"
    UNKNOWN = "unknown"


class SiteCategory(str, Enum):
    """Website category types."""
    
    ECOMMERCE = "ecommerce"
    MOVIES = "movies"
    STREAMING = "streaming"
    BOOKS = "books"
    KIDS = "kids"
    FASHION = "fashion"
    BEAUTY = "beauty"
    TECH = "tech"
    SOCIAL = "social"
    NEWS = "news"
    GENERAL = "general"


class SortOrder(str, Enum):
    """Sorting order options."""
    
    ASCENDING = "asc"
    DESCENDING = "desc"


class AIProvider(str, Enum):
    """AI service provider options."""
    
    GROQ = "groq"
    GEMINI = "gemini"
    FALLBACK = "fallback"