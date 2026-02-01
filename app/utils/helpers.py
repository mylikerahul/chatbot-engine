"""
Utility helper classes for common operations.
"""

import re
from typing import Optional


class TextHelper:
    """Helper class for text processing operations."""
    
    @staticmethod
    def clean_text(text: str, max_length: Optional[int] = None) -> str:
        """Clean and normalize text."""
        if not text:
            return ""
        
        cleaned = re.sub(r"\s+", " ", text).strip()
        
        if max_length:
            cleaned = cleaned[:max_length]
        
        return cleaned
    
    @staticmethod
    def extract_numbers(text: str) -> list:
        """Extract all numbers from text."""
        return re.findall(r"\d+\.?\d*", text)
    
    @staticmethod
    def remove_special_chars(text: str) -> str:
        """Remove special characters keeping alphanumeric and spaces."""
        return re.sub(r"[^a-zA-Z0-9\s]", "", text)


class PriceHelper:
    """Helper class for price-related operations."""
    
    CURRENCY_SYMBOLS = ["$", "Rs", "Rs.", "INR", "USD"]
    
    @classmethod
    def parse(cls, price_str: str) -> float:
        """Parse price string to float."""
        if not price_str:
            return 0.0
        
        cleaned = price_str
        for symbol in cls.CURRENCY_SYMBOLS:
            cleaned = cleaned.replace(symbol, "")
        
        cleaned = re.sub(r"[^\d.]", "", cleaned.replace(",", ""))
        
        try:
            return float(cleaned) if cleaned else 0.0
        except ValueError:
            return 0.0
    
    @classmethod
    def format(cls, price: float, currency: str = "Rs.") -> str:
        """Format price with currency symbol."""
        return f"{currency}{price:,.2f}"