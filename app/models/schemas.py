"""
Pydantic schemas with multi-language support.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class Product(BaseModel):
    """Schema for scraped product/item data."""
    
    id: int = Field(..., description="Unique identifier")
    name: str = Field(..., description="Product name", max_length=200)
    price: Optional[str] = Field(default="", description="Price or metadata")
    rating: Optional[str] = Field(default="", description="Rating score")
    extra: Optional[str] = Field(default="", description="Additional info")
    item_type: Optional[str] = Field(default="item", alias="type")
    image: Optional[str] = Field(default=None, description="Image URL")
    
    class Config:
        populate_by_name = True


class QueryRequest(BaseModel):
    """Schema for chat query request with language support."""
    
    query: str = Field(..., description="User query text", min_length=1)
    products: Optional[List[Product]] = Field(default=[], description="Scraped items")
    page_url: Optional[str] = Field(default=None, description="Current page URL")
    page_title: Optional[str] = Field(default=None, description="Page title")
    page_content: Optional[str] = Field(default=None, description="Page text content")
    site_type: Optional[str] = Field(default=None, description="Detected site type")
    page_type: Optional[str] = Field(default=None, description="Page category")
    language: Optional[str] = Field(default="auto", description="Language code (auto/en/hi/es/...)")


class QueryResponse(BaseModel):
    """Schema for chat query response."""
    
    answer: str = Field(..., description="AI generated response")
    thoughts: List[str] = Field(default=[], description="Processing steps")
    filtered_products: Optional[List[Dict[str, Any]]] = Field(default=[])
    intent: Optional[str] = Field(default=None, description="Detected intent")
    confidence: Optional[float] = Field(default=None, description="Intent confidence")
    processing_time: Optional[float] = Field(default=None, description="Time in seconds")
    language: Optional[str] = Field(default=None, description="Response language")


class LanguageInfo(BaseModel):
    """Schema for language information."""
    
    code: str = Field(..., description="ISO 639-1 code")
    name: str = Field(..., description="English name")
    native_name: str = Field(..., description="Native name")
    direction: str = Field(default="ltr", description="Text direction")


class LanguagesResponse(BaseModel):
    """Schema for supported languages response."""
    
    current: str = Field(..., description="Current language code")
    supported: Dict[str, LanguageInfo] = Field(..., description="Supported languages")


class HealthResponse(BaseModel):
    """Schema for health check response."""
    
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="Application version")
    services: Dict[str, str] = Field(default={}, description="Service statuses")


class ErrorResponse(BaseModel):
    """Schema for error response."""
    
    error: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(default={})