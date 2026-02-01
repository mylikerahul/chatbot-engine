"""
API layer containing routes and dependencies.
"""

from app.api.routes import router
from app.api.dependencies import get_ai_service, get_intent_service, get_product_service

__all__ = [
    "router",
    "get_ai_service",
    "get_intent_service",
    "get_product_service"
]