import time
from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException

from app.core.config import get_settings
from app.core.logger import Logger
from app.core.exceptions import ShopBuddyException
from app.models.schemas import (
    QueryRequest, QueryResponse, HealthResponse, 
    LanguagesResponse, LanguageInfo
)
from app.models.enums import IntentType
from app.api.dependencies import (
    get_ai_service, get_intent_service, 
    get_product_service, get_language_service
)
from app.services.ai_service import AIService
from app.services.intent_service import IntentService
from app.services.product_service import ProductService
from app.services.language_service import LanguageService

class ShopBuddyAPI:
    def __init__(self):
        # 1. Class Properties (State)
        self.router = APIRouter()
        self.logger = Logger("api")
        
        # 2. Register Routes (Constructor mein hi routes bind kar diye)
        self._register_routes()

    def _register_routes(self):
        """Saare endpoints ko router ke saath jodna."""
        self.router.add_api_route("/", self.root, methods=["GET"], response_model=Dict)
        self.router.add_api_route("/health", self.health_check, methods=["GET"], response_model=HealthResponse)
        self.router.add_api_route("/languages", self.get_languages, methods=["GET"], response_model=LanguagesResponse)
        self.router.add_api_route("/language/{language_code}", self.set_language, methods=["POST"])
        self.router.add_api_route("/chat", self.chat, methods=["POST"], response_model=QueryResponse)
        self.router.add_api_route("/clear", self.clear_chat, methods=["POST"])

    # --- Endpoints (Ab ye Class Methods hain) ---

    async def root(self):
        """Root endpoint returning service info."""
        settings = get_settings()
        return {
            "service": settings.app_name,
            "version": settings.app_version,
            "status": "running",
            "multi_language": True
        }

    async def health_check(self, ai_service: AIService = Depends(get_ai_service)):
        settings = get_settings()
        services = {
            "api": "healthy",
            "ai_provider": ai_service.active_provider or "fallback",
            "language": "active"
        }
        return HealthResponse(
            status="healthy",
            version=settings.app_version,
            services=services
        )

    async def get_languages(self, language_service: LanguageService = Depends(get_language_service)):
        supported = language_service.get_supported_languages()
        # List comprehension for cleaner code
        languages_info = {
            code: LanguageInfo(
                code=code, name=info["name"], 
                native_name=info["native"], direction=info["direction"]
            ) for code, info in supported.items()
        }
        return LanguagesResponse(
            current=language_service.get_current_language(),
            supported=languages_info
        )

    async def set_language(self, language_code: str, language_service: LanguageService = Depends(get_language_service)):
        if not language_service.set_language(language_code):
            raise HTTPException(status_code=400, detail=f"Unsupported language: {language_code}")
        
        return {"message": f"Language set to {language_code}", "language": language_code}

    async def chat(
        self,
        request: QueryRequest,
        ai_service: AIService = Depends(get_ai_service),
        intent_service: IntentService = Depends(get_intent_service),
        product_service: ProductService = Depends(get_product_service),
        language_service: LanguageService = Depends(get_language_service)
    ):
        """Main chat logic encapsulated in a method."""
        start_time = time.time()
        thoughts: List[str] = []
        
        try:
            # Language Handling
            if request.language == "auto":
                detected_lang = language_service.detect_language(request.query)
                language_service.set_language(detected_lang)
            elif request.language:
                language_service.set_language(request.language)
            
            current_lang = language_service.get_current_language()
            
            # Logging thoughts (Instance variable use nahi kiya taaki request stateless rahe, 
            # par hum self.logger use kar sakte hain)
            thoughts.extend([
                f"Language: {current_lang}",
                f"Query: {request.query}",
                f"Items: {len(request.products) if request.products else 0}"
            ])

            # Intent Logic
            intent, confidence, _ = intent_service.classify(request.query)
            thoughts.append(f"Intent: {intent} ({confidence:.0%})")

            # --- Specific Intent Handlers (Clean Code) ---
            if intent == IntentType.CLEAR_CHAT.value:
                return self._build_response(
                    answer=language_service.translate("actions.clear", current_lang) + "!",
                    thoughts=thoughts, intent=intent, conf=confidence, start=start_time, lang=current_lang
                )

            if intent == IntentType.HELP.value:
                return self._build_response(
                    answer=language_service.get_help_text(current_lang),
                    thoughts=thoughts, intent=intent, conf=confidence, start=start_time, lang=current_lang
                )

            # Product Logic
            items = [p.model_dump() for p in request.products] if request.products else []
            filtered_products = []

            if items and intent == IntentType.PRODUCT_FILTER.value:
                filters = product_service.parse_filters(request.query)
                thoughts.append(f"Filters: {product_service.format_filter_description(filters)}")
                filtered_products = product_service.apply_filters(items, filters)
                thoughts.append(f"Filtered: {len(filtered_products)} items")
                items = filtered_products if filtered_products else items

            # AI Generation
            thoughts.append("Generating response")
            answer = ai_service.generate_response(
                query=request.query, items=items, 
                site_type=request.site_type or "Unknown",
                page_type=request.page_type or "Unknown",
                page_title=request.page_title or "",
                page_content=request.page_content or "",
                language=current_lang
            )

            processing_time = time.time() - start_time
            self.logger.info(f"Query Processed | Time: {processing_time:.2f}s")

            return QueryResponse(
                answer=answer, thoughts=thoughts, filtered_products=filtered_products,
                intent=intent, confidence=confidence, processing_time=processing_time, language=current_lang
            )

        except ShopBuddyException as e:
            self.logger.error(f"Error: {e.message}")
            raise HTTPException(status_code=400, detail=e.to_dict())
        except Exception as e:
            self.logger.exception(f"Unexpected error: {e}")
            raise HTTPException(status_code=500, detail={"error": "INTERNAL_ERROR"})

    async def clear_chat(self, language_service: LanguageService = Depends(get_language_service)):
        current_lang = language_service.get_current_language()
        return {
            "message": language_service.translate("actions.clear", current_lang), 
            "status": "success"
        }

    # --- Helper Method (Private) ---
    def _build_response(self, answer, thoughts, intent, conf, start, lang):
        """Duplicate code reduce karne ke liye helper method"""
        return QueryResponse(
            answer=answer, thoughts=thoughts, intent=intent,
            confidence=conf, processing_time=time.time() - start, language=lang
        )

# Instance create karo aur router export karo
shop_buddy_api = ShopBuddyAPI()
router = shop_buddy_api.router