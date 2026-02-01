"""
Intent Classifier using Sentence Transformers
"""

import re

# Try importing, handle if fails
try:
    import numpy as np
    from sentence_transformers import SentenceTransformer
    HAS_TRANSFORMER = True
except ImportError:
    HAS_TRANSFORMER = False
    print("⚠️ sentence-transformers not installed, using rule-based classification")


class IntentClassifier:
    def __init__(self):
        print("🔮 Loading Intent Classifier...")
        
        self.model = None
        self.intent_embeddings = {}
        
        # Define intents with examples
        self.intents = {
            "greeting": ["hi", "hello", "hey", "namaste", "good morning", "kaise ho", "how are you"],
            "farewell": ["bye", "goodbye", "see you", "tata", "alvida"],
            "thanks": ["thank you", "thanks", "thanku", "shukriya", "dhanyawad"],
            "help": ["help", "commands", "what can you do", "kya kar sakta hai"],
            "product_filter": ["show products", "best products", "cheap", "under 1000", "above 500", "sasta", "mehnga", "dikhao", "batao"],
            "product_compare": ["compare", "vs", "versus", "which is better", "konsa better"],
            "product_info": ["tell me about", "details", "information", "specs"],
            "price_query": ["price", "cost", "kitne ka", "how much"],
            "clear_chat": ["clear", "reset", "new chat", "start over"],
            "general_question": ["what", "why", "how", "kya", "kaise"]
        }
        
        if HAS_TRANSFORMER:
            try:
                self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
                
                # Pre-compute embeddings
                for intent, examples in self.intents.items():
                    self.intent_embeddings[intent] = self.model.encode(examples)
                
                print("✅ Intent Classifier Ready (ML mode)!")
            except Exception as e:
                print(f"⚠️ ML model failed: {e}, using rules")
                self.model = None
        else:
            print("✅ Intent Classifier Ready (Rule-based)!")

    def classify(self, query: str):
        """Classify query intent"""
        query = query.lower().strip()
        
        # Quick rules first
        quick = self._quick_rules(query)
        if quick:
            return quick, 0.95, {}
        
        # ML-based classification
        if self.model and self.intent_embeddings:
            try:
                query_embedding = self.model.encode([query])[0]
                
                scores = {}
                for intent, embeddings in self.intent_embeddings.items():
                    similarities = np.dot(embeddings, query_embedding) / (
                        np.linalg.norm(embeddings, axis=1) * np.linalg.norm(query_embedding) + 1e-8
                    )
                    scores[intent] = float(np.max(similarities))
                
                best_intent = max(scores, key=scores.get)
                confidence = scores[best_intent]
                
                if confidence < 0.4:
                    if re.search(r'\d+', query):
                        return "product_filter", 0.6, scores
                    return "general_question", confidence, scores
                
                return best_intent, confidence, scores
            except Exception as e:
                print(f"⚠️ ML classification failed: {e}")
        
        # Fallback to rules
        return self._rule_based_classify(query), 0.7, {}

    def _quick_rules(self, query: str):
        """Quick exact match rules"""
        
        if query in ['hi', 'hii', 'hello', 'hey', 'namaste', 'yo']:
            return "greeting"
        
        if query in ['bye', 'goodbye', 'tata']:
            return "farewell"
        
        if query in ['clear', 'reset', 'new chat']:
            return "clear_chat"
        
        if re.search(r'(?:under|below|above|over|₹|rs)\s*\d+', query):
            return "product_filter"
        
        if any(w in query for w in ['thank', 'thanks', 'shukriya']):
            return "thanks"
        
        return None

    def _rule_based_classify(self, query: str):
        """Rule-based classification fallback"""
        
        if any(w in query for w in ['best', 'top', 'cheap', 'sasta', 'under', 'above', 'price', 'product', 'show', 'dikhao']):
            return "product_filter"
        
        if any(w in query for w in ['compare', 'vs', 'better']):
            return "product_compare"
        
        if any(w in query for w in ['help', 'command', 'kya kar']):
            return "help"
        
        return "general_question"

    def get_similar_products(self, query: str, products: list, top_k: int = 5):
        """Find similar products (simple version)"""
        return products[:top_k] if products else []


# Create singleton
intent_classifier = IntentClassifier()