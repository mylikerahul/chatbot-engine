"""
API route definitions with multi-language support.
"""

import time
from typing import List, Dict
from fastapi import APIRouter, Depends, HTTPException, Query

from app.core.config import get_settings
from app.core.logger import Logger
from app.core.exceptions import ShopBuddyException
from app.models.schemas import (
    QueryRequest,
    QueryResponse,
    HealthResponse,
    LanguagesResponse,
    LanguageInfo
)
from app.models.enums import IntentType
from app.api.dependencies import (
    get_ai_service,
    get_intent_service,
    get_product_service,
    get_language_service
)
from app.services.ai_service import AIService
from app.services.intent_service import IntentService
from app.services.product_service import ProductService
from app.services.language_service import LanguageService

router = APIRouter()
logger = Logger("api")


@router.get("/", response_model=Dict)
async def root():
    """Root endpoint returning service info."""
    settings = get_settings()
    return {
        "service": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "multi_language": True
    }


@router.get("/health", response_model=HealthResponse)
async def health_check(
    ai_service: AIService = Depends(get_ai_service)
):
    """Health check endpoint."""
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


@router.get("/languages", response_model=LanguagesResponse)
async def get_languages(
    language_service: LanguageService = Depends(get_language_service)
):
    """Get supported languages."""
    supported = language_service.get_supported_languages()
    
    languages_info = {}
    for code, info in supported.items():
        languages_info[code] = LanguageInfo(
            code=code,
            name=info["name"],
            native_name=info["native"],
            direction=info["direction"]
        )
    
    return LanguagesResponse(
        current=language_service.get_current_language(),
        supported=languages_info
    )


@router.post("/language/{language_code}")
async def set_language(
    language_code: str,
    language_service: LanguageService = Depends(get_language_service)
):
    """Set preferred language."""
    success = language_service.set_language(language_code)
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language: {language_code}"
        )
    
    return {
        "message": f"Language set to {language_code}",
        "language": language_code
    }


@router.post("/chat", response_model=QueryResponse)
async def chat(
    request: QueryRequest,
    ai_service: AIService = Depends(get_ai_service),
    intent_service: IntentService = Depends(get_intent_service),
    product_service: ProductService = Depends(get_product_service),
    language_service: LanguageService = Depends(get_language_service)
):
    """Main chat endpoint with multi-language support."""
    
    start_time = time.time()
    thoughts: List[str] = []
    filtered_products: List[Dict] = []
    
    try:
        if request.language == "auto":
            detected_lang = language_service.detect_language(request.query)
            language_service.set_language(detected_lang)
        elif request.language:
            language_service.set_language(request.language)
        
        current_lang = language_service.get_current_language()
        thoughts.append(f"Language: {current_lang}")
        thoughts.append(f"Query: {request.query}")
        thoughts.append(f"Site: {request.site_type or 'Unknown'}")
        thoughts.append(f"Items: {len(request.products) if request.products else 0}")
        
        intent, confidence, _ = intent_service.classify(request.query)
        thoughts.append(f"Intent: {intent} ({confidence:.0%})")
        
        if intent == IntentType.CLEAR_CHAT.value:
            return QueryResponse(
                answer=language_service.translate("actions.clear", current_lang) + "!",
                thoughts=thoughts,
                intent=intent,
                confidence=confidence,
                processing_time=time.time() - start_time,
                language=current_lang
            )
        
        if intent == IntentType.HELP.value:
            return QueryResponse(
                answer=language_service.get_help_text(current_lang),
                thoughts=thoughts,
                intent=intent,
                confidence=confidence,
                processing_time=time.time() - start_time,
                language=current_lang
            )
        
        items = []
        if request.products:
            items = [p.model_dump() for p in request.products]
        
        if items and intent == IntentType.PRODUCT_FILTER.value:
            filters = product_service.parse_filters(request.query)
            filter_desc = product_service.format_filter_description(filters)
            thoughts.append(f"Filters: {filter_desc}")
            
            filtered_products = product_service.apply_filters(items, filters)
            thoughts.append(f"Filtered: {len(filtered_products)} items")
            
            items = filtered_products if filtered_products else items
        
        thoughts.append("Generating response")
        
        answer = ai_service.generate_response(
            query=request.query,
            items=items,
            site_type=request.site_type or "Unknown",
            page_type=request.page_type or "Unknown",
            page_title=request.page_title or "",
            page_content=request.page_content or "",
            language=current_lang
        )
        
        processing_time = time.time() - start_time
        thoughts.append(f"Completed in {processing_time:.2f}s")
        
        logger.info(f"Query: {request.query[:50]}... | Lang: {current_lang} | Time: {processing_time:.2f}s")
        
        return QueryResponse(
            answer=answer,
            thoughts=thoughts,
            filtered_products=filtered_products,
            intent=intent,
            confidence=confidence,
            processing_time=processing_time,
            language=current_lang
        )
        
    except ShopBuddyException as e:
        logger.error(f"Error: {e.message}")
        raise HTTPException(status_code=400, detail=e.to_dict())
        
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail={
            "error": "INTERNAL_ERROR",
            "message": "An unexpected error occurred"
        })


@router.post("/clear")
async def clear_chat(
    language_service: LanguageService = Depends(get_language_service)
):
    """Clear chat history."""
    current_lang = language_service.get_current_language()
    message = language_service.translate("actions.clear", current_lang)
    
    return {"message": message, "status": "success"}