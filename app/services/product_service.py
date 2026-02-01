"""
Product filtering and analysis service.
Provides smart filtering, sorting, and product comparison.
"""

import re
from typing import List, Dict, Optional, Tuple
from app.core.logger import Logger
from app.models.enums import SortOrder


class ProductFilter:
    """Data class for filter parameters."""
    
    def __init__(self):
        self.min_price: Optional[float] = None
        self.max_price: Optional[float] = None
        self.sort_by: Optional[str] = None
        self.sort_order: Optional[SortOrder] = None
        self.limit: int = 10


class ProductService:
    """
    Service for product filtering, sorting, and analysis.
    Implements singleton pattern.
    """
    
    _instance: Optional["ProductService"] = None
    
    def __new__(cls) -> "ProductService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self) -> None:
        self._logger = Logger("product_service")
        self._logger.info("Product service initialized")
    
    def extract_price(self, price_str: str) -> float:
        """Extract numeric price from string."""
        if not price_str or price_str in ["N/A", "", None]:
            return 0.0
        
        cleaned = re.sub(r"[^\d.]", "", str(price_str).replace(",", ""))
        
        try:
            return float(cleaned) if cleaned else 0.0
        except ValueError:
            return 0.0
    
    def extract_rating(self, rating_str: str) -> float:
        """Extract numeric rating from string."""
        if not rating_str or rating_str in ["N/A", "", None]:
            return 0.0
        
        match = re.search(r"(\d+\.?\d*)", str(rating_str))
        
        try:
            return float(match.group(1)) if match else 0.0
        except (ValueError, AttributeError):
            return 0.0
    
    def parse_filters(self, query: str) -> ProductFilter:
        """Parse filter parameters from user query."""
        query_lower = query.lower()
        filters = ProductFilter()
        
        under_match = re.search(
            r"(?:under|below|niche|less than|max|upto)\s*(?:rs\.?|inr)?\s*(\d+)",
            query_lower
        )
        if under_match:
            filters.max_price = float(under_match.group(1))
        
        above_match = re.search(
            r"(?:above|over|upar|more than|min|atleast)\s*(?:rs\.?|inr)?\s*(\d+)",
            query_lower
        )
        if above_match:
            filters.min_price = float(above_match.group(1))
        
        between_match = re.search(
            r"(\d+)\s*(?:to|se|-|and)\s*(\d+)",
            query_lower
        )
        if between_match and not under_match and not above_match:
            p1, p2 = float(between_match.group(1)), float(between_match.group(2))
            filters.min_price = min(p1, p2)
            filters.max_price = max(p1, p2)
        
        cheap_keywords = ["cheap", "sasta", "lowest price", "budget", "kam price"]
        if any(kw in query_lower for kw in cheap_keywords):
            filters.sort_by = "price"
            filters.sort_order = SortOrder.ASCENDING
        
        expensive_keywords = ["expensive", "mehnga", "costly", "premium", "highest price"]
        if any(kw in query_lower for kw in expensive_keywords):
            filters.sort_by = "price"
            filters.sort_order = SortOrder.DESCENDING
        
        best_keywords = ["best", "top", "highest rated", "accha", "popular"]
        if any(kw in query_lower for kw in best_keywords):
            filters.sort_by = "rating"
            filters.sort_order = SortOrder.DESCENDING
        
        limit_match = re.search(r"(?:top|first|show)\s*(\d+)", query_lower)
        if limit_match:
            filters.limit = min(int(limit_match.group(1)), 20)
        
        return filters
    
    def apply_filters(self, products: List[Dict], filters: ProductFilter) -> List[Dict]:
        """Apply filters to product list."""
        if not products:
            return []
        
        filtered = products.copy()
        
        if filters.min_price is not None:
            filtered = [
                p for p in filtered
                if self.extract_price(p.get("price", "0")) >= filters.min_price
            ]
        
        if filters.max_price is not None:
            filtered = [
                p for p in filtered
                if 0 < self.extract_price(p.get("price", "0")) <= filters.max_price
            ]
        
        if filters.sort_by == "price":
            reverse = filters.sort_order == SortOrder.DESCENDING
            default_val = 0 if reverse else 999999
            filtered = sorted(
                filtered,
                key=lambda x: self.extract_price(x.get("price", "0")) or default_val,
                reverse=reverse
            )
        elif filters.sort_by == "rating":
            filtered = sorted(
                filtered,
                key=lambda x: self.extract_rating(x.get("rating", "0")),
                reverse=True
            )
        
        return filtered[:filters.limit]
    
    def analyze_products(self, products: List[Dict]) -> Dict:
        """Analyze product list for statistics."""
        if not products:
            return {"total": 0}
        
        prices = [self.extract_price(p.get("price", "0")) for p in products]
        prices = [p for p in prices if p > 0]
        
        ratings = [self.extract_rating(p.get("rating", "0")) for p in products]
        ratings = [r for r in ratings if r > 0]
        
        return {
            "total": len(products),
            "price_min": min(prices) if prices else 0,
            "price_max": max(prices) if prices else 0,
            "price_avg": sum(prices) / len(prices) if prices else 0,
            "rating_avg": sum(ratings) / len(ratings) if ratings else 0
        }
    
    def format_filter_description(self, filters: ProductFilter) -> str:
        """Generate human-readable filter description."""
        parts = []
        
        if filters.min_price and filters.max_price:
            parts.append(f"Rs.{int(filters.min_price)} - Rs.{int(filters.max_price)}")
        elif filters.min_price:
            parts.append(f"Above Rs.{int(filters.min_price)}")
        elif filters.max_price:
            parts.append(f"Under Rs.{int(filters.max_price)}")
        
        if filters.sort_by == "price":
            order = "Lowest first" if filters.sort_order == SortOrder.ASCENDING else "Highest first"
            parts.append(order)
        elif filters.sort_by == "rating":
            parts.append("Best rated first")
        
        return " | ".join(parts) if parts else "No filters"