"""
English language translations.
"""

ENGLISH = {
    "meta": {
        "code": "en",
        "name": "English",
        "native_name": "English",
        "direction": "ltr"
    },
    
    "greetings": {
        "hello": "Hello! I'm ShopBuddy, your smart shopping assistant. How can I help you today?",
        "welcome": "Welcome! I can help you find products, compare prices, and get recommendations.",
        "good_morning": "Good morning! Ready to help you with your shopping needs.",
        "good_afternoon": "Good afternoon! What are you looking for today?",
        "good_evening": "Good evening! Let me help you find what you need."
    },
    
    "farewells": {
        "bye": "Goodbye! Happy shopping!",
        "see_you": "See you later! Feel free to come back anytime.",
        "take_care": "Take care! Hope I was helpful."
    },
    
    "thanks": {
        "welcome": "You're welcome! Need anything else?",
        "glad_to_help": "Glad I could help! Anything else you'd like to know?",
        "my_pleasure": "My pleasure! Let me know if you need more assistance."
    },
    
    "help": {
        "intro": "Here's what I can do for you:",
        "commands": [
            "**Product Search**: 'show best products', 'top rated items'",
            "**Price Filter**: 'under 1000', 'above 5000', 'between 500 and 2000'",
            "**Sorting**: 'cheapest first', 'highest rated', 'most expensive'",
            "**Compare**: 'compare top 3', 'which is better'",
            "**Summarize**: 'summarize this page', 'what's on this page'"
        ],
        "tip": "Just type naturally - I understand conversational queries!"
    },
    
    "products": {
        "found": "Found {count} items:",
        "no_items": "No items found on this page.",
        "filtered": "Filtered {count} items based on your criteria:",
        "top_rated": "Top rated products:",
        "cheapest": "Most affordable options:",
        "expensive": "Premium choices:",
        "recommendation": "Based on ratings and price, I recommend:",
        "compare_header": "Comparison of selected items:",
        "price": "Price",
        "rating": "Rating",
        "no_match": "No products match your filters. Try different criteria."
    },
    
    "filters": {
        "applied": "Filters applied: {filters}",
        "under": "Under {amount}",
        "above": "Above {amount}",
        "between": "Between {min} and {max}",
        "sorted_by_price_asc": "Sorted by price (low to high)",
        "sorted_by_price_desc": "Sorted by price (high to low)",
        "sorted_by_rating": "Sorted by rating (best first)"
    },
    
    "errors": {
        "no_products_page": "I don't see any products on this page. Please navigate to a product listing page.",
        "connection_failed": "Connection failed. Please make sure the server is running.",
        "ai_unavailable": "AI service is temporarily unavailable. Using basic responses.",
        "unknown_query": "I'm not sure I understand. Could you rephrase that?",
        "try_again": "Something went wrong. Please try again."
    },
    
    "site_messages": {
        "detected": "Detected: {site}",
        "items_found": "{count} items found on this page",
        "no_items_found": "No items detected on this page",
        "page_type": "Page type: {type}",
        "navigate_suggestion": "Navigate to a product listing page for best results."
    },
    
    "actions": {
        "show_all": "Show All",
        "best_rated": "Best Rated",
        "cheapest": "Cheapest",
        "summarize": "Summarize",
        "compare": "Compare",
        "clear": "Clear Chat"
    },
    
    "ui": {
        "placeholder": "Ask me anything...",
        "send": "Send",
        "typing": "Thinking...",
        "powered_by": "Powered by ShopBuddy AI"
    }
}