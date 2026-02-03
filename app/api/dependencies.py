from functools import cached_property
from app.services.ai_service import AIService
from app.services.intent_service import IntentService
from app.services.product_service import ProductService
from app.services.language_service import LanguageService

class ServiceContainer:
    @cached_property
    def language_service(self) -> LanguageService:
        return LanguageService()

    @cached_property
    def ai_service(self) -> AIService:
        return AIService()

    @cached_property
    def intent_service(self) -> IntentService:
        return IntentService()

    @cached_property
    def product_service(self) -> ProductService:
        return ProductService()

container = ServiceContainer()

def get_ai_service() -> AIService:
    return container.ai_service

def get_intent_service() -> IntentService:
    return container.intent_service

def get_product_service() -> ProductService:
    return container.product_service

def get_language_service() -> LanguageService:
    return container.language_service