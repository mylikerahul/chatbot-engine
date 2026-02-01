"""
AI Conversation Engine - Groq (Primary) + Gemini (Backup)
"""

import os
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()


class GeminiEngine:
    def __init__(self):
        print("🤖 Initializing AI Engine...")
        
        self.groq_client = None
        self.gemini_model = None
        self.chat = None
        
        # Try Groq first
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=groq_key)
                print("✅ Groq AI Ready!")
            except Exception as e:
                print(f"⚠️ Groq init failed: {e}")
        
        # Fallback to Gemini
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key and not self.groq_client:
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                self.gemini_model = genai.GenerativeModel("gemini-2.0-flash")
                self.chat = self.gemini_model.start_chat(history=[])
                print("✅ Gemini Ready (backup)!")
            except Exception as e:
                print(f"⚠️ Gemini init failed: {e}")
        
        if not self.groq_client and not self.gemini_model:
            print("⚠️ No AI configured! Using fallback only.")
        
        self.system_prompt = self._get_system_prompt()

    def _get_system_prompt(self) -> str:
        return """Tu "ShopBuddy" hai - ek smart, friendly AI Assistant.

PERSONALITY:
- Hinglish me baat kar (Hindi + English mix)
- Friendly: "bro", "yaar", "bhai" use kar
- Emojis use kar but spam mat kar
- Short aur helpful responses de

CAPABILITIES:
1. E-commerce sites par products filter karna
2. IMDB par movies/shows recommend karna
3. General questions answer karna
4. Shopping advice dena

RULES:
1. SIRF context me diye products/movies use kar
2. Fake data KABHI mat banana
3. Concise reh
4. Agar products nahi hain, toh user ko guide kar"""

    def generate_response(
        self,
        query: str,
        intent: str,
        products: List[Dict] = None,
        filtered_products: List[Dict] = None,
        analysis: Dict = None,
        filter_description: str = None,
        page_title: str = None
    ) -> str:
        """Generate response using Groq or Gemini"""
        
        # Build context
        context = self._build_context(products, filtered_products, analysis, filter_description, page_title)
        
        # Build prompt
        prompt = f"""USER: {query}
INTENT: {intent}
PAGE: {page_title or 'Unknown'}

CONTEXT:
{context}

Respond in Hinglish, be helpful and concise:"""

        # Try Groq first with UPDATED model
        if self.groq_client:
            try:
                response = self.groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",  # ✅ UPDATED MODEL
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1024
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"⚠️ Groq error: {e}")
        
        # Try Gemini
        if self.gemini_model:
            try:
                full_prompt = f"{self.system_prompt}\n\n{prompt}"
                response = self.chat.send_message(full_prompt)
                return response.text.strip()
            except Exception as e:
                print(f"⚠️ Gemini error: {e}")
        
        # Fallback
        return self._get_fallback_response(intent, query, filtered_products, page_title)

    def _build_context(self, products, filtered_products, analysis, filter_description, page_title) -> str:
        """Build context string"""
        parts = []
        
        if page_title:
            parts.append(f"Page: {page_title}")
        
        if analysis:
            parts.append(f"Total items: {analysis.get('total_products', 0)}")
        
        if filter_description and filter_description != "No filters":
            parts.append(f"Filters: {filter_description}")
        
        display_products = filtered_products if filtered_products else products
        
        if display_products:
            parts.append(f"\nITEMS ({len(display_products)}):")
            for i, p in enumerate(display_products[:8], 1):
                name = p.get('name', 'Unknown')[:60]
                price = p.get('price', 'N/A')
                rating = p.get('rating', 'N/A')
                parts.append(f"{i}. {name}\n   💰 {price} | ⭐ {rating}")
        else:
            parts.append("\n⚠️ No items found on this page")
        
        return "\n".join(parts)

    def _get_fallback_response(self, intent: str, query: str = "", products: list = None, page_title: str = None) -> str:
        """Fallback responses"""
        
        if intent == "greeting":
            return "Hey! 👋 Main ShopBuddy hoon. Kya help chahiye?"
        
        if intent == "farewell":
            return "Bye bro! 👋 Take care!"
        
        if intent == "thanks":
            return "Welcome yaar! 😊 Aur kuch chahiye?"
        
        if intent == "help":
            return """🤖 **Main ye kar sakta hoon:**

**Shopping Sites (Amazon/Flipkart):**
• `best products` - Top rated
• `under 1000` - Budget items
• `sabse sasta` - Cheapest

**Entertainment (IMDB):**
• `best movies` - Top rated
• `top shows` - Popular series

Pehle kisi site pe jao, phir mujhse pooch!"""

        if intent == "clear_chat":
            return "🗑️ Chat cleared!"
        
        # Products available
        if products and len(products) > 0:
            response = "🛒 **Found items:**\n\n"
            for i, p in enumerate(products[:5], 1):
                name = p.get('name', 'Unknown')[:50]
                price = p.get('price', '')
                rating = p.get('rating', '')
                response += f"{i}. **{name}**\n"
                if price:
                    response += f"   💰 {price}"
                if rating:
                    response += f" | ⭐ {rating}"
                response += "\n\n"
            return response
        
        # No products - check page type
        if page_title:
            pt = page_title.lower()
            if 'imdb' in pt:
                return """🎬 **IMDB pe ho!**

Ye try karo:
1. Kisi movie/show ke page pe jao
2. Ya search results page pe jao
3. Phir mujhse pooch "best movies" ya "top rated"

Example: imdb.com/chart/top"""
            
            if 'amazon' in pt or 'flipkart' in pt:
                return """🛒 **Is page par products nahi mile!**

Ye karo:
1. Search bar me kuch search kar (jaise "headphones")
2. Search results page pe jao
3. Phir mujhse pooch!"""
        
        return f"""🤔 Is page par kuch nahi mila.

**Supported sites:**
• Amazon / Flipkart - Products
• IMDB - Movies & Shows

Pehle supported site pe jao, phir mujhse pooch!"""

    def clear_history(self) -> str:
        """Clear chat history"""
        if self.gemini_model:
            try:
                self.chat = self.gemini_model.start_chat(history=[])
            except:
                pass
        return "🗑️ Chat cleared!"


# Create singleton
gemini_engine = GeminiEngine()