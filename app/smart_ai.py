"""
Smart AI Engine - Advanced Response Generation
"""

import os
from dotenv import load_dotenv
from typing import List, Dict, Optional

load_dotenv()


class SmartAI:
    def __init__(self):
        print("🧠 Initializing Smart AI...")
        
        self.groq_client = None
        self.gemini_model = None
        
        # Try Groq first
        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key:
            try:
                from groq import Groq
                self.groq_client = Groq(api_key=groq_key)
                print("✅ Groq AI Ready!")
            except Exception as e:
                print(f"⚠️ Groq failed: {e}")
        
        # Fallback to Gemini
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                self.gemini_model = genai.GenerativeModel("gemini-2.0-flash")
                if not self.groq_client:
                    print("✅ Gemini Ready!")
            except Exception as e:
                print(f"⚠️ Gemini failed: {e}")

    def get_system_prompt(self, site_type: str = "") -> str:
        return f"""Tu "ShopBuddy" hai - ek intelligent AI assistant jo kisi bhi website par help karta hai.

## CURRENT CONTEXT:
Site: {site_type}

## PERSONALITY:
- Hinglish me baat kar (Hindi + English mix)
- Friendly aur helpful ho
- Emojis use kar appropriately
- Concise aur clear responses de
- Data-driven answers de

## CAPABILITIES:
1. **E-commerce** (Amazon, Flipkart): Products filter, compare, recommend
2. **Entertainment** (IMDB, YouTube): Movies, shows, videos recommend
3. **Social** (Reddit, Twitter): Posts summarize, trending batao
4. **Code** (GitHub): Repos analyze, code explain
5. **News**: Articles summarize, key points nikalo
6. **General**: Any website ka content analyze

## RULES:
1. SIRF provided data use kar - fake mat banana
2. Agar data nahi hai, clearly bol
3. User ke question ko properly address kar
4. Helpful suggestions do
5. Format response nicely with bullets/numbers jab zaroorat ho"""

    def build_context(
        self,
        items: List[Dict],
        site_type: str,
        page_type: str,
        page_title: str,
        page_content: str = ""
    ) -> str:
        """Build context for AI"""
        
        parts = []
        
        parts.append(f"📍 Site: {site_type}")
        parts.append(f"📄 Page: {page_type}")
        parts.append(f"🔗 Title: {page_title}")
        
        if items:
            parts.append(f"\n📦 ITEMS FOUND ({len(items)}):")
            
            for i, item in enumerate(items[:15], 1):
                line = f"{i}. **{item.get('name', 'Unknown')}**"
                
                if item.get('price'):
                    line += f"\n   💰 {item['price']}"
                if item.get('rating'):
                    line += f" | ⭐ {item['rating']}"
                if item.get('extra'):
                    line += f"\n   ℹ️ {item['extra'][:60]}"
                
                parts.append(line)
                
            if len(items) > 15:
                parts.append(f"... and {len(items) - 15} more items")
        else:
            parts.append("\n⚠️ No structured items found on this page")
            
            if page_content:
                parts.append(f"\n📝 PAGE CONTENT PREVIEW:\n{page_content[:800]}...")
        
        return "\n".join(parts)

    def generate_response(
        self,
        query: str,
        items: List[Dict] = None,
        site_type: str = "Unknown",
        page_type: str = "Unknown",
        page_title: str = "",
        page_content: str = ""
    ) -> str:
        """Generate intelligent response"""
        
        # Build context
        context = self.build_context(items or [], site_type, page_type, page_title, page_content)
        
        # Build prompt
        prompt = f"""USER QUERY: {query}

CONTEXT:
{context}

---
Respond helpfully in Hinglish. Be specific and use the data provided."""

        # Try Groq
        if self.groq_client:
            try:
                response = self.groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": self.get_system_prompt(site_type)},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=1500
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"⚠️ Groq error: {e}")
        
        # Try Gemini
        if self.gemini_model:
            try:
                full_prompt = f"{self.get_system_prompt(site_type)}\n\n{prompt}"
                response = self.gemini_model.generate_content(full_prompt)
                return response.text.strip()
            except Exception as e:
                print(f"⚠️ Gemini error: {e}")
        
        # Fallback
        return self.get_fallback_response(query, items, site_type)

    def get_fallback_response(self, query: str, items: List[Dict], site_type: str) -> str:
        """Fallback when AI fails"""
        
        query_lower = query.lower()
        
        # Greetings
        if any(w in query_lower for w in ['hi', 'hello', 'hey', 'namaste']):
            return f"Hey! 👋 Main ShopBuddy hoon. {site_type} par hun abhi. Kya help chahiye?"
        
        # Help
        if any(w in query_lower for w in ['help', 'kya kar', 'commands']):
            return """🤖 **Main ye kar sakta hoon:**

**Shopping Sites:**
• `best products` - Top rated items
• `under 1000` - Budget friendly
• `compare` - Products compare karo

**Entertainment:**
• `top movies` - Best rated
• `trending` - Popular content

**General:**
• `summarize` - Page summary
• `show items` - All items list

Kuch bhi pooch, main help karunga! 💪"""
        
        # Show items
        if items and any(w in query_lower for w in ['show', 'list', 'dikhao', 'items', 'products']):
            response = f"📦 **Found {len(items)} items:**\n\n"
            for i, item in enumerate(items[:8], 1):
                response += f"{i}. **{item.get('name', 'Unknown')[:50]}**"
                if item.get('price'):
                    response += f" - {item['price']}"
                if item.get('rating'):
                    response += f" ⭐{item['rating']}"
                response += "\n"
            return response
        
        # No items
        if not items:
            return f"""📍 **{site_type}** par hun, lekin structured data nahi mila.

Ye try karo:
• Search results page pe jao
• Product/content listing page pe jao
• Phir mujhse pooch!"""
        
        # Default
        return f"🤔 '{query}' ke baare me specific data nahi mila. Try: `show items` ya `summarize`"


# Singleton
smart_ai = SmartAI()