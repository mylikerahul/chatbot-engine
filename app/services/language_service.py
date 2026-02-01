"""
Language detection and translation service.
Provides multi-language support across the application.
"""

import re
from typing import Optional, Dict, Any, List
from app.core.logger import Logger
from app.locales import TRANSLATIONS, SUPPORTED_LANGUAGES


class LanguageService:
    """
    Service for language detection and translation.
    Implements singleton pattern for resource efficiency.
    """
    
    _instance: Optional["LanguageService"] = None
    
    def __new__(cls) -> "LanguageService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self) -> None:
        self._logger = Logger("language_service")
        self._default_language = "en"
        self._current_language = "en"
        
        self._language_patterns = {
            "hi": [
                r"[\u0900-\u097F]",
                r"\b(kya|kaise|hai|hain|mujhe|batao|dikhao|chahiye|acha|theek)\b"
            ],
            "ar": [r"[\u0600-\u06FF]"],
            "zh": [r"[\u4e00-\u9fff]"],
            "ja": [r"[\u3040-\u309F\u30A0-\u30FF]"],
            "ru": [r"[\u0400-\u04FF]"],
            "es": [r"\b(hola|gracias|como|estas|quiero|mostrar|productos)\b"],
            "fr": [r"\b(bonjour|merci|comment|montrer|produits|prix)\b"],
            "de": [r"\b(hallo|danke|wie|zeigen|produkte|preis)\b"],
            "pt": [r"\b(ola|obrigado|como|mostrar|produtos|preco)\b"]
        }
        
        self._logger.info("Language service initialized")
    
    def detect_language(self, text: str) -> str:
        """
        Detect language from text using pattern matching.
        
        Args:
            text: Input text to analyze
            
        Returns:
            ISO 639-1 language code
        """
        if not text:
            return self._default_language
        
        text_lower = text.lower()
        
        for lang_code, patterns in self._language_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE | re.UNICODE):
                    self._logger.debug(f"Detected language: {lang_code}")
                    return lang_code
        
        return self._default_language
    
    def set_language(self, language_code: str) -> bool:
        """
        Set current language for translations.
        
        Args:
            language_code: ISO 639-1 language code
            
        Returns:
            True if language was set successfully
        """
        if language_code in SUPPORTED_LANGUAGES:
            self._current_language = language_code
            self._logger.info(f"Language set to: {language_code}")
            return True
        
        self._logger.warning(f"Unsupported language: {language_code}")
        return False
    
    def get_current_language(self) -> str:
        """Get current language code."""
        return self._current_language
    
    def get_supported_languages(self) -> Dict[str, Dict[str, str]]:
        """Get all supported languages with metadata."""
        return SUPPORTED_LANGUAGES
    
    def translate(
        self,
        key: str,
        language: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Get translated text for a key.
        
        Args:
            key: Translation key in dot notation (e.g., "greetings.hello")
            language: Target language code (uses current if not specified)
            **kwargs: Format arguments for string interpolation
            
        Returns:
            Translated text or key if not found
        """
        lang = language or self._current_language
        
        if lang not in TRANSLATIONS:
            lang = self._default_language
        
        translations = TRANSLATIONS[lang]
        
        try:
            keys = key.split(".")
            value = translations
            
            for k in keys:
                value = value[k]
            
            if kwargs:
                value = value.format(**kwargs)
            
            return value
            
        except (KeyError, TypeError):
            self._logger.warning(f"Translation not found: {key} ({lang})")
            return key
    
    def get_greeting(self, language: Optional[str] = None) -> str:
        """Get localized greeting message."""
        return self.translate("greetings.hello", language)
    
    def get_farewell(self, language: Optional[str] = None) -> str:
        """Get localized farewell message."""
        return self.translate("farewells.bye", language)
    
    def get_thanks_response(self, language: Optional[str] = None) -> str:
        """Get localized thanks response."""
        return self.translate("thanks.welcome", language)
    
    def get_help_text(self, language: Optional[str] = None) -> str:
        """Get localized help text."""
        lang = language or self._current_language
        
        intro = self.translate("help.intro", lang)
        commands = self.translate("help.commands", lang)
        tip = self.translate("help.tip", lang)
        
        if isinstance(commands, list):
            commands_text = "\n".join(commands)
        else:
            commands_text = str(commands)
        
        return f"{intro}\n\n{commands_text}\n\n{tip}"
    
    def get_error_message(
        self,
        error_type: str,
        language: Optional[str] = None
    ) -> str:
        """Get localized error message."""
        return self.translate(f"errors.{error_type}", language)
    
    def get_product_text(
        self,
        text_type: str,
        language: Optional[str] = None,
        **kwargs
    ) -> str:
        """Get localized product-related text."""
        return self.translate(f"products.{text_type}", language, **kwargs)
    
    def get_action_label(
        self,
        action: str,
        language: Optional[str] = None
    ) -> str:
        """Get localized action button label."""
        return self.translate(f"actions.{action}", language)
    
    def get_ui_text(
        self,
        element: str,
        language: Optional[str] = None
    ) -> str:
        """Get localized UI element text."""
        return self.translate(f"ui.{element}", language)
    
    def get_all_translations(self, language: Optional[str] = None) -> Dict[str, Any]:
        """Get all translations for a language."""
        lang = language or self._current_language
        return TRANSLATIONS.get(lang, TRANSLATIONS[self._default_language])
    
    def get_direction(self, language: Optional[str] = None) -> str:
        """Get text direction (ltr/rtl) for language."""
        lang = language or self._current_language
        lang_info = SUPPORTED_LANGUAGES.get(lang, {})
        return lang_info.get("direction", "ltr")


language_service = LanguageService()