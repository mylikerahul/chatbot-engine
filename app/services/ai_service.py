"""
AI Service powered by LangChain
Enterprise-Grade LLM Orchestration with Real Product Intelligence
Production Ready - Clean Code
"""

from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
from app.core.config import get_settings
from app.core.logger import Logger
from app.core.exceptions import AIServiceException

from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.documents import Document

from pydantic import BaseModel, Field
from enum import Enum
import json
import re

try:
    from langchain_community.vectorstores import FAISS
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    VECTOR_STORE_AVAILABLE = True
except ImportError:
    VECTOR_STORE_AVAILABLE = False


class IntentType(str, Enum):
    PRODUCT_SEARCH = "product_search"
    PRICE_COMPARISON = "price_comparison"
    RECOMMENDATION = "recommendation"
    QUESTION_ANSWER = "question_answer"
    GENERAL_CHAT = "general_chat"


class ProductRecommendation(BaseModel):
    product_name: str = Field(description="Product name")
    reason: str = Field(description="Why this product is recommended")
    price: Optional[str] = Field(default=None, description="Product price")
    rating: Optional[str] = Field(default=None, description="Product rating")
    discount: Optional[str] = Field(default=None, description="Discount percentage")


class TokenCounterCallback(BaseCallbackHandler):
    
    def __init__(self):
        self.total_tokens = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.chain_calls = 0
    
    def on_llm_start(self, serialized, prompts, **kwargs):
        self.chain_calls += 1
    
    def on_llm_end(self, response, **kwargs):
        if hasattr(response, 'llm_output') and response.llm_output:
            usage = response.llm_output.get('token_usage', {})
            self.total_tokens += usage.get('total_tokens', 0)
            self.prompt_tokens += usage.get('prompt_tokens', 0)
            self.completion_tokens += usage.get('completion_tokens', 0)


class SimpleChatHistory:
    
    def __init__(self):
        self.messages: List[BaseMessage] = []
        self.metadata: Dict[str, Any] = {
            "created_at": datetime.now(),
            "message_count": 0,
            "last_intent": None
        }
    
    def add_user_message(self, message: str, metadata: Dict = None) -> None:
        msg = HumanMessage(content=message)
        if metadata:
            msg.additional_kwargs = metadata
        self.messages.append(msg)
        self.metadata["message_count"] += 1
    
    def add_ai_message(self, message: str, metadata: Dict = None) -> None:
        msg = AIMessage(content=message)
        if metadata:
            msg.additional_kwargs = metadata
        self.messages.append(msg)
    
    def clear(self) -> None:
        self.messages.clear()
        self.metadata["message_count"] = 0


class ProductIntelligence:
    
    @staticmethod
    def extract_price_range(query: str) -> Tuple[Optional[int], Optional[int]]:
        patterns = [
            r'(\d+)\s*(?:se|से)\s*kam',
            r'under\s*[₹$]?\s*(\d+)',
            r'below\s*[₹$]?\s*(\d+)',
            r'less\s*than\s*[₹$]?\s*(\d+)',
            r'[₹$]?\s*(\d+)\s*(?:se|से|-|to)\s*[₹$]?\s*(\d+)',
            r'between\s*[₹$]?\s*(\d+)\s*(?:and|&)\s*[₹$]?\s*(\d+)',
            r'budget\s*[₹$]?\s*(\d+)',
            r'max\s*[₹$]?\s*(\d+)',
        ]
        
        query_lower = query.lower().replace(',', '')
        
        for pattern in patterns:
            match = re.search(pattern, query_lower)
            if match:
                groups = match.groups()
                if len(groups) == 1:
                    return (0, int(groups[0]))
                else:
                    return (int(groups[0]), int(groups[1]))
        
        return (None, None)
    
    @staticmethod
    def filter_by_price(items: List[Dict], min_price: int = None, max_price: int = None) -> List[Dict]:
        if not items:
            return []
        
        filtered = []
        
        for item in items:
            price_str = item.get('price', '0')
            price_match = re.search(r'[\d,]+', str(price_str))
            
            if price_match:
                try:
                    price = int(price_match.group().replace(',', ''))
                    
                    if min_price and price < min_price:
                        continue
                    if max_price and price > max_price:
                        continue
                    
                    filtered.append(item)
                except ValueError:
                    continue
        
        return filtered
    
    @staticmethod
    def extract_category(query: str) -> Optional[str]:
        query_lower = query.lower()
        
        category_keywords = {
            "mobile_accessories": [
                "mobile", "phone", "earphone", "headphone", "earbuds",
                "charger", "cable", "power bank", "case", "cover"
            ],
            "electronics": [
                "tv", "television", "speaker", "tablet", "laptop",
                "camera", "smart watch", "monitor"
            ],
            "home_kitchen": [
                "mixer", "grinder", "kettle", "cooker", "toaster",
                "oven", "refrigerator", "washing machine", "iron", "fan"
            ],
            "fashion": [
                "shirt", "tshirt", "jeans", "shoes", "watch",
                "sunglasses", "bag", "wallet", "belt"
            ],
            "books": ["book", "novel", "kindle", "magazine"],
            "beauty": ["beauty", "cosmetic", "makeup", "skincare", "perfume"]
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                return category
        
        return None
    
    @staticmethod
    def sort_by_value(items: List[Dict]) -> List[Dict]:
        if not items:
            return []
        
        def value_score(item):
            score = 0.0
            
            discount = 0
            if item.get('discount'):
                match = re.search(r'(\d+)%', str(item['discount']))
                if match:
                    discount = int(match.group(1))
            
            rating = 0.0
            if item.get('rating'):
                match = re.search(r'([\d.]+)', str(item['rating']))
                if match:
                    try:
                        rating = float(match.group(1))
                    except ValueError:
                        pass
            
            price = 999999
            if item.get('price'):
                match = re.search(r'[\d,]+', str(item['price']))
                if match:
                    try:
                        price = int(match.group().replace(',', ''))
                    except ValueError:
                        pass
            
            score = (discount * 0.4) + (rating * 6) + (max(0, (10000 - price) / 10000) * 30)
            return score
        
        return sorted(items, key=value_score, reverse=True)
    
    @staticmethod
    def sort_by_price(items: List[Dict], ascending: bool = True) -> List[Dict]:
        if not items:
            return []
        
        def get_price(item):
            price_str = item.get('price', '999999')
            match = re.search(r'[\d,]+', str(price_str))
            if match:
                try:
                    return int(match.group().replace(',', ''))
                except ValueError:
                    return 999999
            return 999999
        
        return sorted(items, key=get_price, reverse=not ascending)
    
    @staticmethod
    def sort_by_rating(items: List[Dict]) -> List[Dict]:
        if not items:
            return []
        
        def get_rating(item):
            rating_str = item.get('rating', '0')
            match = re.search(r'([\d.]+)', str(rating_str))
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    return 0.0
            return 0.0
        
        return sorted(items, key=get_rating, reverse=True)


class LangChainService:
    
    _instance: Optional["LangChainService"] = None
    
    def __new__(cls) -> "LangChainService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self) -> None:
        self._logger = Logger("langchain_service")
        self._settings = get_settings()
        self._product_intel = ProductIntelligence()
        self._chat_histories: Dict[str, SimpleChatHistory] = {}
        self._token_callback = TokenCounterCallback()
        self._vectorstore: Optional[Any] = None
        self._embeddings = None
        
        self._setup_llms()
        self._setup_embeddings()
        self._setup_chains()
    
    def _setup_llms(self) -> None:
        try:
            llms = []
            
            if self._settings.has_groq:
                groq_llm = ChatGroq(
                    temperature=self._settings.temperature,
                    model_name=self._settings.groq_model,
                    groq_api_key=self._settings.groq_api_key,
                    max_tokens=self._settings.max_tokens,
                    max_retries=2,
                    callbacks=[self._token_callback]
                )
                llms.append(groq_llm)
            
            if self._settings.has_gemini:
                gemini_llm = ChatGoogleGenerativeAI(
                    model=self._settings.gemini_model,
                    google_api_key=self._settings.gemini_api_key,
                    temperature=self._settings.temperature,
                    convert_system_message_to_human=True,
                    callbacks=[self._token_callback]
                )
                llms.append(gemini_llm)
            
            if len(llms) > 1:
                self._llm = llms[0].with_fallbacks(llms[1:])
            elif len(llms) == 1:
                self._llm = llms[0]
            else:
                self._llm = None
                
        except Exception as e:
            self._logger.error(f"LLM initialization failed: {e}")
            self._llm = None
    
    def _setup_embeddings(self) -> None:
        if not VECTOR_STORE_AVAILABLE:
            return
        
        try:
            if self._settings.has_gemini:
                self._embeddings = GoogleGenerativeAIEmbeddings(
                    model="models/embedding-001",
                    google_api_key=self._settings.gemini_api_key
                )
        except Exception as e:
            self._logger.error(f"Embeddings setup failed: {e}")
            self._embeddings = None
    
    def _create_vectorstore(self, items: List[Dict]) -> None:
        if not VECTOR_STORE_AVAILABLE or not self._embeddings or not items:
            return
        
        try:
            documents = []
            for item in items:
                content = f"""
                Product: {item.get('name', 'Unknown')}
                Price: {item.get('price', 'N/A')}
                Rating: {item.get('rating', 'N/A')}
                Discount: {item.get('discount', 'N/A')}
                """
                metadata = {
                    'name': item.get('name'),
                    'price': item.get('price'),
                    'rating': item.get('rating'),
                    'discount': item.get('discount')
                }
                documents.append(Document(page_content=content, metadata=metadata))
            
            self._vectorstore = FAISS.from_documents(
                documents=documents,
                embedding=self._embeddings
            )
        except Exception:
            self._vectorstore = None
    
    def _setup_chains(self) -> None:
        if not self._llm:
            return
        
        self._intent_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an intent classifier for e-commerce queries. Classify into ONE category:

Categories:
- product_search: User searching for specific products
- price_comparison: Comparing prices or asking about deals
- recommendation: Wants product suggestions
- question_answer: Questions about features
- general_chat: Greetings or general conversation

Respond with ONLY the category name in lowercase."""),
            ("human", "{query}")
        ])
        
        self._intent_chain = self._intent_prompt | self._llm | StrOutputParser()
        
        self._response_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are ShopBuddy - An Expert AI Shopping Assistant.

CURRENT CONTEXT:
{context}

LANGUAGE: {language_instruction}

GUIDELINES:
1. ONLY recommend products from the context provided
2. For each recommendation, explain WHY it's good
3. Compare products when multiple options exist
4. Highlight discounts and savings
5. Mention ratings for credibility
6. If NO products are available, inform the user politely
7. Be helpful and professional

CONVERSATION HISTORY:
{chat_history}

FORMAT:
- Use bullet points or numbered lists
- Include price and rating for each product
- End with a helpful follow-up question
"""),
            ("human", "{query}")
        ])
        
        self._response_chain = self._response_prompt | self._llm | StrOutputParser()
        
        self._structured_prompt = ChatPromptTemplate.from_messages([
            ("system", """Generate structured JSON with product recommendations.

Context: {context}

Return valid JSON:
{{
    "intent": "product_search|price_comparison|recommendation|question_answer|general_chat",
    "response_text": "Natural language response",
    "recommendations": [
        {{
            "product_name": "Product name",
            "reason": "Why recommended",
            "price": "Price",
            "rating": "Rating",
            "discount": "Discount"
        }}
    ],
    "total_products": 5
}}"""),
            ("human", "{query}")
        ])
        
        self._structured_chain = self._structured_prompt | self._llm | JsonOutputParser()
    
    def _format_products_context(self, items: List[Dict]) -> str:
        if not items:
            return "No products currently available. The user should browse the website to see products."
        
        context_parts = [f"{len(items)} Products Available:\n"]
        
        for i, item in enumerate(items[:25], 1):
            parts = [f"\n{i}. {item.get('name', 'Unknown Product')}"]
            
            if item.get("price"):
                parts.append(f"   Price: {item['price']}")
            
            if item.get("discount"):
                parts.append(f"   Discount: {item['discount']}")
            
            if item.get("rating"):
                parts.append(f"   Rating: {item['rating']}")
            
            if item.get("reviews"):
                parts.append(f"   Reviews: {item['reviews']}")
            
            context_parts.append("\n".join(parts))
        
        return "\n".join(context_parts)
    
    def _get_chat_history(self, session_id: str) -> SimpleChatHistory:
        if session_id not in self._chat_histories:
            self._chat_histories[session_id] = SimpleChatHistory()
        return self._chat_histories[session_id]
    
    def _prepare_items(self, items: List[Dict], query: str) -> List[Dict]:
        if not items:
            return []
        
        min_price, max_price = self._product_intel.extract_price_range(query)
        
        if max_price:
            items = self._product_intel.filter_by_price(items, min_price, max_price)
        
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["cheapest", "lowest price", "sasta", "cheap", "budget"]):
            items = self._product_intel.sort_by_price(items, ascending=True)
        elif any(word in query_lower for word in ["expensive", "costly", "premium", "best"]):
            items = self._product_intel.sort_by_price(items, ascending=False)
        elif any(word in query_lower for word in ["best rated", "top rated", "highest rating", "popular"]):
            items = self._product_intel.sort_by_rating(items)
        else:
            items = self._product_intel.sort_by_value(items)
        
        return items
    
    def generate_response(
        self,
        query: str,
        items: List[Dict] = None,
        site_type: str = "Unknown",
        page_type: str = "Unknown",
        page_title: str = "",
        page_content: str = "",
        language: str = "en",
        session_id: str = "default",
        use_rag: bool = False
    ) -> str:
        
        if not self._response_chain:
            return "AI Service is currently unavailable. Please check API keys configuration."
        
        try:
            prepared_items = self._prepare_items(items or [], query)
            
            if use_rag and prepared_items and VECTOR_STORE_AVAILABLE:
                self._create_vectorstore(prepared_items)
            
            product_context = self._format_products_context(prepared_items)
            
            full_context = f"""
Site: {site_type}
Page Type: {page_type}
Page Title: {page_title}

{product_context}

Page Summary:
{page_content[:400] if page_content else 'No additional page content available.'}
            """
            
            language_map = {
                "en": "Respond in clear, professional English.",
                "hi": "Respond in Hinglish (Hindi + English mix). Use Roman script for Hindi words.",
                "es": "Respond in Spanish.",
                "auto": "Detect language from query and respond accordingly."
            }
            lang_instruction = language_map.get(language, language_map["en"])
            
            chat_history = self._get_chat_history(session_id)
            history_text = "\n".join([
                f"{'User' if isinstance(msg, HumanMessage) else 'ShopBuddy'}: {msg.content[:100]}"
                for msg in chat_history.messages[-4:]
            ]) or "No previous conversation."
            
            response = self._response_chain.invoke({
                "context": full_context,
                "language_instruction": lang_instruction,
                "query": query,
                "chat_history": history_text
            })
            
            chat_history.add_user_message(query, {"timestamp": datetime.now().isoformat()})
            chat_history.add_ai_message(response, {
                "timestamp": datetime.now().isoformat(),
                "products_shown": len(prepared_items)
            })
            
            return response
            
        except Exception as e:
            self._logger.error(f"Chain execution failed: {e}")
            return "Sorry, I encountered an error processing your request. Please try again."
    
    def classify_intent(self, query: str) -> str:
        if not self._intent_chain:
            return "general_chat"
        
        try:
            intent = self._intent_chain.invoke({"query": query})
            cleaned = intent.strip().lower()
            
            valid_intents = [
                "product_search", "price_comparison", "recommendation",
                "question_answer", "general_chat"
            ]
            
            return cleaned if cleaned in valid_intents else "general_chat"
            
        except Exception:
            return "general_chat"
    
    def clear_history(self, session_id: str = "default") -> None:
        if session_id in self._chat_histories:
            self._chat_histories[session_id].clear()
    
    @property
    def active_provider(self) -> str:
        if not self._llm:
            return "none"
        return "LangChain (Groq/Gemini Fallback)"
    
    @property
    def token_usage(self) -> Dict[str, int]:
        return {
            "total_tokens": self._token_callback.total_tokens,
            "prompt_tokens": self._token_callback.prompt_tokens,
            "completion_tokens": self._token_callback.completion_tokens,
            "chain_calls": self._token_callback.chain_calls
        }
    
    @property
    def has_rag_support(self) -> bool:
        return VECTOR_STORE_AVAILABLE and self._embeddings is not None
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "service": "LangChainService",
            "version": "2.0.0",
            "llm_available": self._llm is not None,
            "active_provider": self.active_provider,
            "has_rag": self.has_rag_support,
            "token_usage": self.token_usage,
            "active_sessions": len(self._chat_histories)
        }


AIService = LangChainService