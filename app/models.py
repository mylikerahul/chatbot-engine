from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class Product(BaseModel):
    id: int
    name: str
    price: Optional[str] = ""
    rating: Optional[str] = ""
    extra: Optional[str] = ""
    type: Optional[str] = "item"
    image: Optional[str] = None


class QueryRequest(BaseModel):
    query: str
    products: Optional[List[Product]] = []
    page_url: Optional[str] = None
    page_title: Optional[str] = None
    page_content: Optional[str] = None
    site_type: Optional[str] = None
    page_type: Optional[str] = None


class AIResponse(BaseModel):
    answer: str
    thoughts: List[str]
    filtered_products: Optional[List[Dict[str, Any]]] = []