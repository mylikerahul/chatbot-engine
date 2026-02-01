"""
AI Service powered by LangChain 🦜🔗
Enterprise-Grade LLM Orchestration with Real Product Intelligence
"""

from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime
from app.core.config import get_settings
from app.core.logger import Logger
from app.core.exceptions import AIServiceException

# LangChain Core Imports
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.runnables import (
    RunnablePassthrough, 
    RunnableBranch,
    RunnableParallel,
    RunnableLambda
)
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage

# Advanced LangChain Features
from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.documents import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Pydantic for Structured Output
from pydantic import BaseModel, Field
from enum import Enum
import json
import re

# Optional: Vector Store
try:
    from langchain_community.vectorstores import FAISS
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    VECTOR_STORE_AVAILABLE = True
except ImportError:
    VECTOR_STORE_AVAILABLE = False

# ============================================================================
# STRUCTURED OUTPUT SCHEMAS
# ============================================================================

class IntentType(str, Enum):
    """User query intent classification"""
    PRODUCT_SEARCH = "product_search"
    PRICE_COMPARISON = "price_comparison"
    RECOMMENDATION = "recommendation"
    QUESTION_ANSWER = "question_answer"
    GENERAL_CHAT = "general_chat"

class ProductRecommendation(BaseModel):
    """Structured product recommendation output"""
    product_name: str = Field(description="Product name")
    reason: str = Field(description="Why this product is recommended")
    price: Optional[str] = Field(default=None, description="Product price")
    rating: Optional[str] = Field(default=None, description="Product rating")
    discount: Optional[str] = Field(default=None, description="Discount percentage")
    emoji: str = Field(default="⭐", description="Relevant emoji")

# ============================================================================
# CUSTOM CALLBACKS FOR MONITORING
# ============================================================================

class TokenCounterCallback(BaseCallbackHandler):
    """Track token usage and chain performance"""
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

# ============================================================================
# IN-MEMORY CHAT HISTORY
# ============================================================================

class SimpleChatHistory:
    """Simple in-memory chat history with metadata"""
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

# ============================================================================
# PRODUCT INTELLIGENCE ENGINE
# ============================================================================

class ProductIntelligence:
    """Smart product filtering and analysis engine"""
    
    @staticmethod
    def extract_price_range(query: str) -> Tuple[Optional[int], Optional[int]]:
        """Extract price range from user query"""
        # Patterns: "2000 se kam", "500-1000", "under 1500"
        patterns = [
            r'(\d+)\s*se\s*kam',      # "2000 se kam"
            r'under\s*(\d+)',          # "under 2000"
            r'below\s*(\d+)',          # "below 1500"
            r'(\d+)\s*se\s*(\d+)',     # "500 se 1500"
            r'(\d+)\s*-\s*(\d+)',      # "500-1500"
            r'between\s*(\d+)\s*and\s*(\d+)',  # "between 500 and 1000"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query.lower())
            if match:
                groups = match.groups()
                if len(groups) == 1:
                    return (0, int(groups[0]))
                else:
                    return (int(groups[0]), int(groups[1]))
        
        return (None, None)
    
    @staticmethod
    def filter_by_price(items: List[Dict], min_price: int = None, max_price: int = None) -> List[Dict]:
        """Filter products by price range"""
        if not items:
            return []
        
        filtered = []
        for item in items:
            price_str = item.get('price', '₹0')
            # Extract numeric value from price (₹1,299 -> 1299)
            price_match = re.search(r'[\d,]+', price_str)
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
        """Detect product category from query"""
        query_lower = query.lower()
        
        category_keywords = {
            "mobile_accessories": [
                "mobile", "phone", "earphone", "headphone", "earbuds",
                "charger", "cable", "power bank", "screen guard",
                "case", "cover", "adapter", "wireless"
            ],
            "electronics": [
                "tv", "television", "speaker", "alexa", "echo",
                "fire stick", "tablet", "laptop", "camera",
                "smart watch", "fitness band"
            ],
            "home_kitchen": [
                "mixer", "grinder", "kettle", "kitchen", "cooker",
                "toaster", "oven", "refrigerator", "washing machine",
                "iron", "vacuum", "cleaner"
            ],
            "fashion": [
                "shirt", "tshirt", "jeans", "shoes", "watch",
                "sunglasses", "bag", "wallet", "belt", "clothing"
            ],
            "books": [
                "book", "novel", "kindle", "magazine", "comic"
            ]
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                return category
        
        return None
    
    @staticmethod
    def sort_by_value(items: List[Dict]) -> List[Dict]:
        """Sort products by best value (price, discount, rating)"""
        if not items:
            return []
        
        def value_score(item):
            score = 0.0
            
            # Extract discount percentage (higher is better)
            discount = 0
            if 'discount' in item and item['discount']:
                match = re.search(r'(\d+)%', str(item['discount']))
                if match:
                    discount = int(match.group(1))
            
            # Extract rating (higher is better)
            rating = 0.0
            if 'rating' in item and item['rating']:
                match = re.search(r'([\d.]+)', str(item['rating']))
                if match:
                    try:
                        rating = float(match.group(1))
                    except ValueError:
                        rating = 0.0
            
            # Extract price (lower is better for value)
            price = 999999
            if 'price' in item and item['price']:
                match = re.search(r'[\d,]+', str(item['price']))
                if match:
                    try:
                        price = int(match.group().replace(',', ''))
                    except ValueError:
                        price = 999999
            
            # Calculate composite score
            # Weighted formula: 40% discount + 30% rating + 30% price value
            discount_score = discount * 0.4
            rating_score = rating * 6  # Scale to 0-30
            price_score = max(0, (5000 - price) / 5000) * 30  # Normalize to 0-30
            
            score = discount_score + rating_score + price_score
            
            return score
        
        return sorted(items, key=value_score, reverse=True)
    
    @staticmethod
    def sort_by_price(items: List[Dict], ascending: bool = True) -> List[Dict]:
        """Sort products by price"""
        if not items:
            return []
        
        def get_price(item):
            price_str = item.get('price', '₹999999')
            match = re.search(r'[\d,]+', price_str)
            if match:
                try:
                    return int(match.group().replace(',', ''))
                except ValueError:
                    return 999999
            return 999999
        
        return sorted(items, key=get_price, reverse=not ascending)
    
    @staticmethod
    def sort_by_rating(items: List[Dict]) -> List[Dict]:
        """Sort products by rating (highest first)"""
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

# ============================================================================
# MAIN SERVICE CLASS
# ============================================================================

class LangChainService:
    """
    🚀 Advanced AI Service using LangChain LCEL
    
    Features:
    ✅ Multi-Model Fallback Strategy (Groq -> Gemini)
    ✅ Smart Product Filtering & Sorting
    ✅ Price Range Detection
    ✅ Category Classification
    ✅ Conversational Memory
    ✅ Intent Classification
    ✅ Token Usage Tracking
    ✅ RAG Support (Optional)
    """
    
    _instance: Optional["LangChainService"] = None
    
    def __new__(cls) -> "LangChainService":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self) -> None:
        """Initialize all LangChain components"""
        self._logger = Logger("langchain_service")
        self._settings = get_settings()
        
        # Product Intelligence Engine
        self._product_intel = ProductIntelligence()
        
        # Chat History Management
        self._chat_histories: Dict[str, SimpleChatHistory] = {}
        
        # Callback for monitoring
        self._token_callback = TokenCounterCallback()
        
        # Vector Store for RAG
        self._vectorstore: Optional[Any] = None
        self._embeddings = None
        
        # Setup all chains
        self._setup_llms()
        self._setup_embeddings()
        self._setup_chains()
    
    # ========================================================================
    # LLM SETUP WITH FALLBACK
    # ========================================================================
    
    def _setup_llms(self) -> None:
        """Initialize LLMs with advanced fallback configuration"""
        try:
            llms = []
            
            # Primary: Groq (Ultra-fast LLaMA 3.3 70B)
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
                self._logger.info("✅ Primary LLM (Groq LLaMA 3.3) initialized")

            # Backup: Gemini Pro (Advanced reasoning)
            if self._settings.has_gemini:
                gemini_llm = ChatGoogleGenerativeAI(
                    model=self._settings.gemini_model,
                    google_api_key=self._settings.gemini_api_key,
                    temperature=self._settings.temperature,
                    convert_system_message_to_human=True,
                    callbacks=[self._token_callback]
                )
                llms.append(gemini_llm)
                self._logger.info("✅ Backup LLM (Gemini Pro) initialized")

            # Create fallback chain
            if len(llms) > 1:
                self._llm = llms[0].with_fallbacks(llms[1:])
                self._logger.info("🔄 Fallback mechanism activated")
            elif len(llms) == 1:
                self._llm = llms[0]
            else:
                self._logger.warning("⚠️ No LLMs available!")
                self._llm = None
                
        except Exception as e:
            self._logger.error(f"❌ LLM initialization failed: {e}")
            self._llm = None
    
    # ========================================================================
    # EMBEDDINGS & VECTOR STORE (RAG)
    # ========================================================================
    
    def _setup_embeddings(self) -> None:
        """Setup embeddings for semantic search"""
        if not VECTOR_STORE_AVAILABLE:
            self._logger.info("ℹ️ Vector store optional - using standard search")
            return
            
        try:
            if self._settings.has_gemini:
                self._embeddings = GoogleGenerativeAIEmbeddings(
                    model="models/embedding-001",
                    google_api_key=self._settings.gemini_api_key
                )
                self._logger.info("✅ Embeddings initialized (Gemini)")
        except Exception as e:
            self._logger.error(f"⚠️ Embeddings setup failed: {e}")
            self._embeddings = None
    
    def _create_vectorstore(self, items: List[Dict]) -> None:
        """Create FAISS vector store from products (RAG)"""
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
                Description: {item.get('description', '')}
                Reviews: {item.get('reviews', 'N/A')}
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
            self._logger.info(f"📚 Vector store created with {len(documents)} products")
            
        except Exception as e:
            self._logger.error(f"Vector store creation failed: {e}")
            self._vectorstore = None
    
    # ========================================================================
    # CHAIN SETUP
    # ========================================================================
    
    def _setup_chains(self) -> None:
        """Build advanced LangChain pipelines"""
        if not self._llm:
            self._logger.warning("Cannot setup chains without LLM")
            return
        
        # 1. Intent Classification Chain
        self._intent_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an intent classifier for e-commerce queries. Classify into ONE category:

Categories:
- product_search: User searching for specific products
- price_comparison: Comparing prices or asking about deals
- recommendation: Wants product suggestions/recommendations
- question_answer: Questions about features/specifications
- general_chat: Greetings or general conversation

Respond with ONLY the category name in lowercase."""),
            ("human", "{query}")
        ])
        
        self._intent_chain = (
            self._intent_prompt 
            | self._llm 
            | StrOutputParser()
        )
        
        # 2. Main Response Chain with Rich Context
        self._response_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are ShopBuddy 🛍️ - An Expert AI Shopping Assistant with deep product knowledge.

🎯 CURRENT CONTEXT:
{context}

🌍 LANGUAGE: {language_instruction}

📋 CORE GUIDELINES:
1. ONLY recommend products from the context provided - NEVER hallucinate or invent products
2. For each recommendation, explain WHY it's good (discount, rating, features, value)
3. Use emojis strategically: 💰 (great deals), ⭐ (high ratings), 🔥 (trending), 💎 (premium)
4. Compare products when multiple options exist
5. Highlight discounts and savings prominently
6. Mention ratings and review counts for credibility
7. If asked for specific count (e.g., "50 products"), provide exactly that many from available products
8. Sort recommendations by best value unless user specifies otherwise
9. If NO products are available, politely inform the user and suggest they browse the site
10. Be helpful, enthusiastic, and professional

💬 CONVERSATION HISTORY:
{chat_history}

🎨 RESPONSE STYLE:
- Be enthusiastic but professional
- Use bullet points or numbered lists for product recommendations
- Include price, discount, and rating for each product
- Explain the value proposition clearly
- End with a helpful question or suggestion
"""),
            ("human", "{query}")
        ])
        
        self._response_chain = (
            self._response_prompt 
            | self._llm 
            | StrOutputParser()
        )
        
        # 3. Structured JSON Output Chain
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
            "discount": "Discount",
            "emoji": "Emoji"
        }}
    ],
    "total_products": 5
}}

ONLY return valid JSON, no markdown or extra text."""),
            ("human", "{query}")
        ])
        
        self._structured_chain = (
            self._structured_prompt 
            | self._llm 
            | JsonOutputParser()
        )
        
        self._logger.info("✅ All LangChain pipelines initialized")
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _format_products_context(self, items: List[Dict]) -> str:
        """Format products into rich, detailed context"""
        if not items:
            return "⚠️ No products currently available in this view. The user should browse the website to see products."
        
        context_parts = [f"📦 **{len(items)} Products Available:**\n"]
        
        for i, item in enumerate(items, 1):
            parts = [f"\n**{i}. {item.get('name', 'Unknown Product')}**"]
            
            if item.get("price"):
                parts.append(f"   💰 Price: **{item['price']}**")
            
            if item.get("original_price"):
                parts.append(f"   ~~Original: {item['original_price']}~~")
            
            if item.get("discount"):
                parts.append(f"   🔥 Discount: **{item['discount']}**")
            
            if item.get("rating"):
                parts.append(f"   ⭐ Rating: **{item['rating']}**")
            
            if item.get("reviews"):
                parts.append(f"   📊 Reviews: {item['reviews']}")
            
            if item.get("description"):
                desc = str(item['description'])[:150]
                parts.append(f"   📝 {desc}")
            
            context_parts.append("\n".join(parts))
        
        return "\n".join(context_parts)
    
    def _get_chat_history(self, session_id: str) -> SimpleChatHistory:
        """Get or create chat history for session"""
        if session_id not in self._chat_histories:
            self._chat_histories[session_id] = SimpleChatHistory()
        return self._chat_histories[session_id]
    
    def _prepare_items(self, items: List[Dict], query: str) -> List[Dict]:
        """Smart product preparation with filtering and sorting"""
        
        if not items or len(items) == 0:
            self._logger.warning("⚠️ No products provided from scraper")
            return []
        
        # Step 1: Extract price range from query
        min_price, max_price = self._product_intel.extract_price_range(query)
        
        if max_price:
            self._logger.info(f"💰 Filtering by price: ₹{min_price or 0} - ₹{max_price}")
            items = self._product_intel.filter_by_price(items, min_price, max_price)
        
        # Step 2: Check for sorting keywords
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["cheapest", "lowest price", "sasta", "cheap"]):
            items = self._product_intel.sort_by_price(items, ascending=True)
            self._logger.info("📊 Sorted by: Price (Low to High)")
        
        elif any(word in query_lower for word in ["expensive", "costly", "premium", "mahanga"]):
            items = self._product_intel.sort_by_price(items, ascending=False)
            self._logger.info("📊 Sorted by: Price (High to Low)")
        
        elif any(word in query_lower for word in ["best rated", "top rated", "highest rating"]):
            items = self._product_intel.sort_by_rating(items)
            self._logger.info("📊 Sorted by: Rating")
        
        else:
            # Default: Sort by best value
            items = self._product_intel.sort_by_value(items)
            self._logger.info("📊 Sorted by: Best Value")
        
        self._logger.info(f"✅ Prepared {len(items)} products for context")
        return items
    
    # ========================================================================
    # PUBLIC API
    # ========================================================================
    
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
        """
        🚀 Generate AI response using advanced LangChain pipeline
        
        Args:
            query: User question
            items: Scraped products from page
            site_type: E-commerce platform
            page_type: Product/Search/Category page
            page_title: Current page title
            page_content: Page text summary
            language: Response language (en/hi/es)
            session_id: Conversation session ID
            use_rag: Enable semantic search with RAG
        
        Returns:
            AI-generated response
        """
        if not self._response_chain:
            return "⚠️ AI Service is currently unavailable. Please check API keys."
        
        try:
            # Step 1: Prepare products (filter, sort)
            prepared_items = self._prepare_items(items or [], query)
            
            # Step 2: Create Vector Store for RAG (if enabled)
            if use_rag and prepared_items and VECTOR_STORE_AVAILABLE:
                self._create_vectorstore(prepared_items)
            
            # Step 3: Build Context
            product_context = self._format_products_context(prepared_items)
            
            full_context = f"""
🌐 **Site:** {site_type}
📄 **Page Type:** {page_type}
📌 **Page Title:** {page_title}

{product_context}

📝 **Page Summary:**
{page_content[:400] if page_content else 'No additional page content available.'}
            """
            
            # Step 4: Language Configuration
            language_map = {
                "en": "Respond in clear, professional English with appropriate emojis.",
                "hi": "Respond in Hinglish (Hindi + English mix). Use Roman script primarily, with Devanagari only for emphasis.",
                "es": "Respond in Spanish with appropriate emojis.",
                "auto": "Detect language from query and respond accordingly."
            }
            lang_instruction = language_map.get(language, "Respond in Hinglish with emojis.")
            
            # Step 5: Get Chat History
            chat_history = self._get_chat_history(session_id)
            history_text = "\n".join([
                f"{'👤 User' if isinstance(msg, HumanMessage) else '🤖 ShopBuddy'}: {msg.content[:100]}"
                for msg in chat_history.messages[-4:]  # Last 2 exchanges
            ]) or "No previous conversation."
            
            # Step 6: Invoke LangChain Pipeline
            self._logger.info(f"🔄 Processing query: {query[:50]}...")
            
            response = self._response_chain.invoke({
                "context": full_context,
                "language_instruction": lang_instruction,
                "query": query,
                "chat_history": history_text
            })
            
            # Step 7: Update Chat History
            chat_history.add_user_message(query, {"timestamp": datetime.now().isoformat()})
            chat_history.add_ai_message(response, {
                "timestamp": datetime.now().isoformat(),
                "products_shown": len(prepared_items)
            })
            
            # Step 8: Log Analytics
            self._logger.info(f"✅ Response generated | Products: {len(prepared_items)} | Tokens: {self._token_callback.total_tokens}")
            
            return response
            
        except Exception as e:
            self._logger.error(f"❌ Chain execution failed: {e}", exc_info=True)
            return "Sorry, I encountered an error processing your request. Please try again! 🙏"
    
    def classify_intent(self, query: str) -> str:
        """Classify user query intent using LangChain"""
        if not self._intent_chain:
            return "general_chat"
        
        try:
            intent = self._intent_chain.invoke({"query": query})
            cleaned = intent.strip().lower()
            
            valid_intents = ["product_search", "price_comparison", "recommendation", 
                           "question_answer", "general_chat"]
            return cleaned if cleaned in valid_intents else "general_chat"
        except Exception as e:
            self._logger.error(f"Intent classification failed: {e}")
            return "general_chat"
    
    def clear_history(self, session_id: str = "default") -> None:
        """Clear chat history for session"""
        if session_id in self._chat_histories:
            self._chat_histories[session_id].clear()
            self._logger.info(f"🗑️ Cleared history for: {session_id}")
    
    @property
    def active_provider(self) -> str:
        """Get active LLM provider info"""
        if not self._llm:
            return "none"
        return "LangChain (Groq/Gemini Fallback)"
    
    @property
    def token_usage(self) -> Dict[str, int]:
        """Get token usage statistics"""
        return {
            "total_tokens": self._token_callback.total_tokens,
            "prompt_tokens": self._token_callback.prompt_tokens,
            "completion_tokens": self._token_callback.completion_tokens,
            "chain_calls": self._token_callback.chain_calls
        }
    
    @property
    def has_rag_support(self) -> bool:
        """Check if RAG is available"""
        return VECTOR_STORE_AVAILABLE and self._embeddings is not None

# ============================================================================
# BACKWARD COMPATIBILITY
# ============================================================================

AIService = LangChainService