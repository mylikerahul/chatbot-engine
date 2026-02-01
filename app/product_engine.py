"""
Product Filtering Engine
"""

import re
from typing import List, Dict


class ProductEngine:
    def __init__(self):
        print("🛒 Product Engine Initialized!")

    def extract_price(self, price_str: str) -> float:
        """Extract numeric price"""
        if not price_str or price_str == 'N/A':
            return 0.0
        cleaned = re.sub(r'[^\d.]', '', str(price_str).replace(',', ''))
        try:
            return float(cleaned) if cleaned else 0.0
        except:
            return 0.0

    def extract_rating(self, rating_str: str) -> float:
        """Extract numeric rating"""
        if not rating_str or rating_str == 'N/A':
            return 0.0
        match = re.search(r'(\d+\.?\d*)', str(rating_str))
        try:
            return float(match.group(1)) if match else 0.0
        except:
            return 0.0

    def parse_filters(self, query: str) -> Dict:
        """Parse filters from query"""
        query_lower = query.lower()
        filters = {
            'min_price': None,
            'max_price': None,
            'sort_by': None,
            'sort_order': None
        }
        
        # Under/Below X
        under_match = re.search(r'(?:under|below|niche|less than|max|upto)\s*(?:₹|rs\.?|inr)?\s*(\d+)', query_lower)
        if under_match:
            filters['max_price'] = float(under_match.group(1))
        
        # Above/Over X
        above_match = re.search(r'(?:above|over|upar|more than|min)\s*(?:₹|rs\.?|inr)?\s*(\d+)', query_lower)
        if above_match:
            filters['min_price'] = float(above_match.group(1))
        
        # Between X and Y
        between_match = re.search(r'(\d+)\s*(?:to|se|-|and)\s*(\d+)', query_lower)
        if between_match and not under_match and not above_match:
            p1, p2 = float(between_match.group(1)), float(between_match.group(2))
            filters['min_price'] = min(p1, p2)
            filters['max_price'] = max(p1, p2)
        
        # Sort by cheap
        if any(w in query_lower for w in ['cheap', 'sasta', 'lowest', 'budget']):
            filters['sort_by'] = 'price'
            filters['sort_order'] = 'asc'
        
        # Sort by expensive
        if any(w in query_lower for w in ['expensive', 'mehnga', 'costly', 'premium']):
            filters['sort_by'] = 'price'
            filters['sort_order'] = 'desc'
        
        # Sort by rating
        if any(w in query_lower for w in ['best', 'top', 'highest rated', 'accha', 'popular']):
            filters['sort_by'] = 'rating'
            filters['sort_order'] = 'desc'
        
        return filters

    def filter_products(self, products: List[Dict], filters: Dict) -> List[Dict]:
        """Apply filters"""
        if not products:
            return []
        
        filtered = products.copy()
        
        if filters['min_price'] is not None:
            filtered = [p for p in filtered if self.extract_price(p.get('price', '0')) >= filters['min_price']]
        
        if filters['max_price'] is not None:
            filtered = [p for p in filtered if 0 < self.extract_price(p.get('price', '0')) <= filters['max_price']]
        
        if filters['sort_by'] == 'price':
            reverse = filters['sort_order'] == 'desc'
            default = 0 if reverse else 999999
            filtered = sorted(filtered, key=lambda x: self.extract_price(x.get('price', '0')) or default, reverse=reverse)
        
        elif filters['sort_by'] == 'rating':
            filtered = sorted(filtered, key=lambda x: self.extract_rating(x.get('rating', '0')), reverse=True)
        
        return filtered

    def analyze_products(self, products: List[Dict]) -> Dict:
        """Analyze products"""
        if not products:
            return {'total_products': 0}
        
        prices = [self.extract_price(p.get('price', '0')) for p in products]
        prices = [p for p in prices if p > 0]
        
        return {
            'total_products': len(products),
            'price_range': {
                'min': min(prices) if prices else 0,
                'max': max(prices) if prices else 0
            }
        }

    def format_filter_description(self, filters: Dict) -> str:
        """Readable filter description"""
        parts = []
        
        if filters['min_price'] and filters['max_price']:
            parts.append(f"₹{int(filters['min_price'])} - ₹{int(filters['max_price'])}")
        elif filters['min_price']:
            parts.append(f"Above ₹{int(filters['min_price'])}")
        elif filters['max_price']:
            parts.append(f"Under ₹{int(filters['max_price'])}")
        
        if filters['sort_by'] == 'price':
            parts.append("Cheapest first" if filters['sort_order'] == 'asc' else "Expensive first")
        elif filters['sort_by'] == 'rating':
            parts.append("Best rated first")
        
        return " | ".join(parts) if parts else "No filters"


# Create singleton
product_engine = ProductEngine()