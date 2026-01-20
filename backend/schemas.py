"""Pydantic schemas for API requests/responses"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class ItemInfo(BaseModel):
    """Item information"""
    asin: str
    title: str
    category: Optional[str] = None
    brand: Optional[str] = None
    price: Optional[float] = None
    rating_avg: float = 0
    rating_count: int = 0
    similarity: Optional[float] = None
    
    class Config:
        from_attributes = True


class RecommendationRequest(BaseModel):
    """Request for recommendations"""
    query: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None


class RecommendationResponse(BaseModel):
    """Response with recommendations"""
    query: str
    intent: str
    detected_category: Optional[str] = None
    recommendations: List[ItemInfo]
    session_id: str


class ItemDetailRequest(BaseModel):
    """Request for item details"""
    asin: str


class ItemDetailResponse(BaseModel):
    """Response with item details"""
    asin: str
    title: str
    category: Optional[str] = None
    brand: Optional[str] = None
    price: Optional[float] = None
    rating_avg: float
    rating_count: int
    category_path: Optional[str] = None
    attributes: Dict[str, Any] = {}
    
    class Config:
        from_attributes = True


class ConversationMessage(BaseModel):
    """Message in conversation"""
    role: str  # "user" or "assistant"
    content: str


class ConversationRequest(BaseModel):
    """Request for conversation"""
    session_id: str
    message: str


class ConversationResponse(BaseModel):
    """Response with conversation"""
    session_id: str
    assistant_response: str
    recommendations: List[ItemInfo] = []
