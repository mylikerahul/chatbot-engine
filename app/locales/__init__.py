"""
Localization module for multi-language support.
Provides translations for all supported languages.
"""

from app.locales.en import ENGLISH
from app.locales.hi import HINDI
from app.locales.es import SPANISH
from app.locales.fr import FRENCH
from app.locales.de import GERMAN
from app.locales.ar import ARABIC
from app.locales.zh import CHINESE
from app.locales.ja import JAPANESE
from app.locales.pt import PORTUGUESE
from app.locales.ru import RUSSIAN

TRANSLATIONS = {
    "en": ENGLISH,
    "hi": HINDI,
    "es": SPANISH,
    "fr": FRENCH,
    "de": GERMAN,
    "ar": ARABIC,
    "zh": CHINESE,
    "ja": JAPANESE,
    "pt": PORTUGUESE,
    "ru": RUSSIAN
}

SUPPORTED_LANGUAGES = {
    "en": {"name": "English", "native": "English", "direction": "ltr"},
    "hi": {"name": "Hindi", "native": "हिन्दी", "direction": "ltr"},
    "es": {"name": "Spanish", "native": "Español", "direction": "ltr"},
    "fr": {"name": "French", "native": "Français", "direction": "ltr"},
    "de": {"name": "German", "native": "Deutsch", "direction": "ltr"},
    "ar": {"name": "Arabic", "native": "العربية", "direction": "rtl"},
    "zh": {"name": "Chinese", "native": "中文", "direction": "ltr"},
    "ja": {"name": "Japanese", "native": "日本語", "direction": "ltr"},
    "pt": {"name": "Portuguese", "native": "Português", "direction": "ltr"},
    "ru": {"name": "Russian", "native": "Русский", "direction": "ltr"}
}

__all__ = ["TRANSLATIONS", "SUPPORTED_LANGUAGES"]