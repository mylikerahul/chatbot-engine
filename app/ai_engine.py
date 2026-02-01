"""
Main AI Engine - Orchestrator
"""

from typing import List, Dict, Tuple
from app.intent_classifier import intent_classifier
from app.product_engine import product_engine
from app.smart_ai import smart_ai


class AIEngine:
    def __init__(self):
        print("=" * 50)
        print("🚀 ShopBuddy AI Engine v3.0 - Universal")
        print("=" * 50)

    def get_answer(
        self,
        query: str,
        products: List[Dict] = None,
        page_url: str = None,
        page_title: str = None,
        page_content: str = None,
        site_type: str = None,
        page_type: str = None
    ) -> Tuple[str, List[str], List[Dict]]:
        """Process query and return response"""
        
        thoughts = []
        filtered_products = []
        
        # Log
        thoughts.append(f"🔍 Query: '{query}'")
        thoughts.append(f"📍 Site: {site_type or 'Unknown'}")
        thoughts.append(f"📦 Items: {len(products) if products else 0}")
        
        # Intent classification
        intent, confidence, _ = intent_classifier.classify(query)
        thoughts.append(f"🎯 Intent: {intent} ({confidence:.0%})")
        
        # Clear chat
        if intent == "clear_chat":
            return "🗑️ Chat cleared! Fresh start!", thoughts, []
        
        # Convert products to dict if needed
        items = []
        if products:
            for p in products:
                if isinstance(p, dict):
                    items.append(p)
                else:
                    items.append(p.dict() if hasattr(p, 'dict') else vars(p))
        
        # Filter products if needed
        if items and intent == "product_filter":
            filters = product_engine.parse_filters(query)
            filter_desc = product_engine.format_filter_description(filters)
            thoughts.append(f"🔧 Filters: {filter_desc}")
            
            filtered_products = product_engine.filter_products(items, filters)
            thoughts.append(f"✅ Filtered: {len(filtered_products)}")
            
            # Use filtered for response
            items = filtered_products if filtered_products else items
        
        # Generate AI response
        thoughts.append("🤖 Generating response...")
        
        response = smart_ai.generate_response(
            query=query,
            items=items,
            site_type=site_type or "Unknown",
            page_type=page_type or "Unknown",
            page_title=page_title or "",
            page_content=page_content or ""
        )
        
        thoughts.append("✅ Done!")
        
        return response, thoughts, filtered_products

    def clear_history(self) -> str:
        return "🗑️ Chat cleared!"

    def get_stats(self) -> Dict:
        return {
            "version": "3.0",
            "type": "Universal",
            "status": "active"
        }


# Global instance
engine = AIEngine()