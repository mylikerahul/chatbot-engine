"""
Application configuration using Pydantic Settings.
"""

from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "ShopBuddy AI"
    app_version: str = "4.0.0"
    app_env: str = "development"
    debug: bool = True
    
    # Server
    host: str = "127.0.0.1"
    port: int = 8080
    
    # AI Providers
    groq_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    huggingfacehub_api_token: Optional[str] = None  # Added this field
    
    # Model Configuration
    groq_model: str = "llama-3.3-70b-versatile"
    gemini_model: str = "gemini-2.0-flash"
    
    # AI Parameters
    temperature: float = 0.7
    max_tokens: int = 1500
    
    # Logging
    log_level: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # This allows extra fields in .env
    )
    
    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"
    
    @property
    def has_groq(self) -> bool:
        return bool(self.groq_api_key)
    
    @property
    def has_gemini(self) -> bool:
        return bool(self.gemini_api_key)


@lru_cache()
def get_settings() -> Settings:
    """Returns cached settings instance."""
    return Settings()