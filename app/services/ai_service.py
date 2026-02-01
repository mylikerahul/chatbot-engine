"""
AI response generation service with multi-language support.
"""

from typing import List, Dict, Optional
from abc import ABC, abstractmethod
from app.core.config import get_settings
from app.core.logger import Logger
from app.core.exceptions import AIServiceException
from app.models.enums import AIProvider
from app.services.language_service import language_service


class AIProviderBase(ABC):
    """Abstract base class for AI providers."""
    
    @abstractmethod
    def generate(self, prompt: str, system_prompt: str) -> str:
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        pass


class GroqProvider(AIProviderBase):
    """Groq LLaMA provider implementation."""
    
    def __init__(self):
        self._settings = get_settings()
        self._client = None
        self._initialize()
    
    def _initialize(self) -> None:
        if not self._settings.has_groq:
            return
        
        try:
            from groq import Groq
            self._client = Groq(api_key=self._settings.groq_api_key)
        except Exception:
            self._client = None
    
    def is_available(self) -> bool:
        return self._client is not None
    
    def generate(self, prompt: str, system_prompt: str) -> str:
        if not self.is_available():
            raise AIServiceException("Groq client not initialized", "groq")
        
        response = self._client.chat.completions.create(
            model=self._settings.groq_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=self._settings.temperature,
            max_tokens=self._settings.max_tokens
        )
        
        return response.choices[0].message.content.strip()


class GeminiProvider(AIProviderBase):
    """Google Gemini provider implementation."""
    
    def __init__(self):
        self._settings = get_settings()
        self._model = None
        self._initialize()
    
    def _initialize(self) -> None:
        if not self._settings.has_gemini:
            return
        
        try:
            import google.generativeai as genai
            genai.configure(api_key=self._settings.gemini_api_key)
            self._model = genai.GenerativeModel(self._settings.gemini_model)
        except Exception:
            self._model = None
    
    def is_available(self) -> bool:
        return self._model is not None
    
    def generate(self, prompt: str, system_prompt: str) -> str:
        if not self.is_available():
            raise AIServiceException("Gemini model not initialized", "gemini")
        
        full_prompt = f"{system_prompt}\n\n{prompt}"
        response = self._model.generate_content(full_prompt)
        
        return response.text.strip()


class AIService:
    """
    Main AI service with multi-language support.
    """
    
    _instance: Optional["AIService"] = None
    
    LANGUAGE_INSTRUCTIONS = {
        "en": "Respond in English. Be helpful, friendly, and concise.",
        "hi": "Respond in Hindi (Devanagari script). Be helpful and friendly. Use simple Hindi that everyone can understand.",
        "es": "Responde en español. Sé útil, amigable y conciso.",
        "fr": "Répondez en français. Soyez utile, amical et concis.",
        "de": "Antworten Sie auf Deutsch. Seien Sie hilfsbereit, freundlich und prägnant.",
        "ar": "الرد باللغة العربية. كن مفيداً وودوداً وموجزاً.",
        "zh": "用中文回复。要有帮助、友好、简洁。",
        "ja": "日本語で回答してください。親切で、フレンドリーで、簡潔に。",
        "pt": "Responda em português. Seja útil, amigável e conciso.",
        "ru": "Отвечайте на русском языке. Будьте полезны, дружелюбны и кратки."
    }
    
    def __new__(cls) -> "AIService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self) -> None:
        self._logger = Logger("ai_service")
        self._settings = get_settings()
        
        self._providers: Dict[str, AIProviderBase] = {}
        self._active_provider: Optional[str] = None
        
        self._setup_providers()
    
    def _setup_providers(self) -> None:
        groq = GroqProvider()
        if groq.is_available():
            self._providers[AIProvider.GROQ.value] = groq
            self._active_provider = AIProvider.GROQ.value
            self._logger.info("Groq provider initialized")
        
        gemini = GeminiProvider()
        if gemini.is_available():
            self._providers[AIProvider.GEMINI.value] = gemini
            if not self._active_provider:
                self._active_provider = AIProvider.GEMINI.value
            self._logger.info("Gemini provider initialized")
        
        if not self._active_provider:
            self._logger.warning("No AI provider available")
    
    def _build_system_prompt(self, language: str = "en") -> str:
        lang_instruction = self.LANGUAGE_INSTRUCTIONS.get(
            language,
            self.LANGUAGE_INSTRUCTIONS["en"]
        )
        
        return f"""You are ShopBuddy, an intelligent shopping and entertainment assistant.

LANGUAGE INSTRUCTION:
{lang_instruction}

CAPABILITIES:
- Filter and recommend products from e-commerce sites
- Suggest movies, shows, and entertainment content
- Provide book recommendations
- Answer questions about items on the page

RULES:
- Only use data provided in the context
- Never fabricate product information
- Mention prices and ratings accurately
- If no data available, guide user appropriately
- Always respond in the specified language"""
    
    def _build_context(
        self,
        items: List[Dict],
        site_type: str,
        page_type: str,
        page_title: str,
        page_content: str = ""
    ) -> str:
        parts = [
            f"Site: {site_type}",
            f"Page Type: {page_type}",
            f"Title: {page_title}"
        ]
        
        if items:
            parts.append(f"\nItems Found ({len(items)}):")
            for i, item in enumerate(items[:12], 1):
                line = f"{i}. {item.get('name', 'Unknown')}"
                if item.get("price"):
                    line += f" | Price: {item['price']}"
                if item.get("rating"):
                    line += f" | Rating: {item['rating']}"
                parts.append(line)
        else:
            parts.append("\nNo structured items found on this page.")
            if page_content:
                parts.append(f"\nPage Content Preview:\n{page_content[:600]}...")
        
        return "\n".join(parts)
    
    def generate_response(
        self,
        query: str,
        items: List[Dict] = None,
        site_type: str = "Unknown",
        page_type: str = "Unknown",
        page_title: str = "",
        page_content: str = "",
        language: str = "en"
    ) -> str:
        """Generate AI response in specified language."""
        
        system_prompt = self._build_system_prompt(language)
        
        context = self._build_context(
            items or [],
            site_type,
            page_type,
            page_title,
            page_content
        )
        
        prompt = f"""User Query: {query}

Context:
{context}

Provide a helpful response:"""

        if self._active_provider and self._active_provider in self._providers:
            try:
                provider = self._providers[self._active_provider]
                return provider.generate(prompt, system_prompt)
            except Exception as e:
                self._logger.error(f"Provider {self._active_provider} failed: {e}")
                
                