"""
FastAPI dependency injection functions.
"""

from app.services.ai_service import AIService
from app.services.intent_service import IntentService
from app.services.product_service import ProductService
from app.services.language_service import LanguageService, language_service


def get_ai_service() -> AIService:
    """Dependency for AI service."""
    return AIService()


def get_intent_service() -> IntentService:
    """Dependency for intent classification service."""
    return IntentService()


def get_product_service() -> ProductService:
    """Dependency for product filtering service."""
    return ProductService()


def get_language_service() -> LanguageService:
    """Dependency for language service."""
    return language_service