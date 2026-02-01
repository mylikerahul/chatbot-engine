"""
Intent classification service using sentence transformers.
Provides semantic similarity based intent detection.
"""

import re
from typing import Tuple, Dict, List, Optional
from app.core.logger import Logger
from app.core.config import get_settings
from app.models.enums import IntentType


class IntentService:
    """
    Service for classifying user intent using ML models.
    Implements singleton pattern for resource efficiency.
    """
    
    _instance: Optional["IntentService"] = None
    
    def __new__(cls) -> "IntentService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self) -> None:
        self._logger = Logger("intent_service")
        self._model = None
        self._intent_embeddings: Dict[str, any] = {}
        
        self._intent_examples: Dict[str, List[str]] = {
            IntentType.GREETING.value: [
                "hi", "hello", "hey", "namaste", "good morning",
                "good evening", "howdy", "hola", "kaise ho", "how are you"
            ],
            IntentType.FAREWELL.value: [
                "bye", "goodbye", "see you", "tata", "alvida", "take care"
            ],
            IntentType.THANKS.value: [
                "thank you", "thanks", "thanku", "shukriya", "dhanyawad"
            ],
            IntentType.HELP.value: [
                "help", "commands", "what can you do", "how to use", "guide"
            ],
            IntentType.PRODUCT_FILTER.value: [
                "show products", "best products", "top rated", "cheap",
                "expensive", "under 1000", "above 500", "filter", "sort",
                "sasta", "mehnga", "accha", "dikhao", "batao"
            ],
            IntentType.PRODUCT_COMPARE.value: [
                "compare", "vs", "versus", "difference", "which is better"
            ],
            IntentType.PRODUCT_INFO.value: [
                "tell me about", "details", "information", "specs", "features"
            ],
            IntentType.PRICE_QUERY.value: [
                "price", "cost", "kitne ka", "how much", "rate"
            ],
            IntentType.SUMMARIZE.value: [
                "summarize", "summary", "overview", "brief", "explain page"
            ],
            IntentType.CLEAR_CHAT.value: [
                "clear", "reset", "new chat", "start over", "forget"
            ],
            IntentType.GENERAL_QUESTION.value: [
                "what", "why", "how", "when", "where", "who", "explain"
            ]
        }
        
        self._load_model()
    
    def _load_model(self) -> None:
        try:
            from sentence_transformers import SentenceTransformer
            import numpy as np
            
            self._model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            self._np = np
            
            for intent, examples in self._intent_examples.items():
                self._intent_embeddings[intent] = self._model.encode(examples)
            
            self._logger.info("Intent classification model loaded successfully")
            
        except Exception as e:
            self._logger.warning(f"ML model not available, using rule-based classification: {e}")
            self._model = None
    
    def classify(self, query: str) -> Tuple[str, float, Dict[str, float]]:
        """
        Classify user intent from query text.
        
        Args:
            query: User input text
            
        Returns:
            Tuple of (intent_type, confidence, all_scores)
        """
        query = query.lower().strip()
        
        quick_result = self._quick_classify(query)
        if quick_result:
            return quick_result, 0.95, {}
        
        if self._model and self._intent_embeddings:
            return self._ml_classify(query)
        
        return self._rule_based_classify(query), 0.6, {}
    
    def _quick_classify(self, query: str) -> Optional[str]:
        """Fast rule-based classification for common patterns."""
        
        greetings = ["hi", "hii", "hello", "hey", "namaste", "yo"]
        if query in greetings:
            return IntentType.GREETING.value
        
        if query in ["clear", "reset", "new chat"]:
            return IntentType.CLEAR_CHAT.value
        
        if re.search(r"(?:under|below|above|over)\s*\d+", query):
            return IntentType.PRODUCT_FILTER.value
        
        thanks_patterns = ["thank", "thanks", "thanku", "shukriya"]
        if any(p in query for p in thanks_patterns):
            return IntentType.THANKS.value
        
        return None
    
    def _ml_classify(self, query: str) -> Tuple[str, float, Dict[str, float]]:
        """ML-based classification using sentence transformers."""
        
        try:
            query_embedding = self._model.encode([query])[0]
            
            scores: Dict[str, float] = {}
            for intent, embeddings in self._intent_embeddings.items():
                similarities = self._np.dot(embeddings, query_embedding) / (
                    self._np.linalg.norm(embeddings, axis=1) * 
                    self._np.linalg.norm(query_embedding) + 1e-8
                )
                scores[intent] = float(self._np.max(similarities))
            
            best_intent = max(scores, key=scores.get)
            confidence = scores[best_intent]
            
            if confidence < 0.4:
                if re.search(r"\d+", query):
                    return IntentType.PRODUCT_FILTER.value, 0.6, scores
                return IntentType.GENERAL_QUESTION.value, confidence, scores
            
            return best_intent, confidence, scores
            
        except Exception as e:
            self._logger.error(f"ML classification failed: {e}")
            return self._rule_based_classify(query), 0.5, {}
    
    def _rule_based_classify(self, query: str) -> str:
        """Fallback rule-based classification."""
        
        product_keywords = ["best", "top", "cheap", "sasta", "under", "above", "price", "product", "show"]
        if any(kw in query for kw in product_keywords):
            return IntentType.PRODUCT_FILTER.value
        
        compare_keywords = ["compare", "vs", "better", "difference"]
        if any(kw in query for kw in compare_keywords):
            return IntentType.PRODUCT_COMPARE.value
        
        if "summarize" in query or "summary" in query:
            return IntentType.SUMMARIZE.value
        
        help_keywords = ["help", "command", "how to"]
        if any(kw in query for kw in help_keywords):
            return IntentType.HELP.value
        
        return IntentType.GENERAL_QUESTION.value