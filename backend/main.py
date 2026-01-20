"""FastAPI main application"""
import logging
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uuid
from datetime import datetime

from backend.database import get_db, init_db
from backend.models import Session as DBSession, Event
from backend.recommendation_engine import RecommendationEngine
from backend.schemas import (
    RecommendationRequest, RecommendationResponse, ItemInfo,
    ItemDetailRequest, ItemDetailResponse,
    ConversationRequest, ConversationResponse
)
from backend.ollama_client import ollama_client

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Amazon Recommendation System",
    description="A recommendation system using LLM and vector embeddings",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/api/recommend", response_model=RecommendationResponse)
async def get_recommendations(
    request: RecommendationRequest,
    db: Session = Depends(get_db)
):
    """Get recommendations based on user query"""
    try:
        # Create or get session
        session_id = request.session_id or str(uuid.uuid4())
        
        db_session = db.query(DBSession).filter(DBSession.session_id == session_id).first()
        if not db_session:
            db_session = DBSession(session_id=session_id, user_id=request.user_id)
            db.add(db_session)
            db.commit()
        
        # Initialize recommendation engine
        rec_engine = RecommendationEngine(db)
        
        # Understand query and get intent
        intent, keywords = rec_engine.understand_query(request.query)
        
        # Detect product category
        detected_category = rec_engine.detect_category(request.query, keywords)
        
        # Generate recommendations
        recommendations = rec_engine.generate_recommendations(request.query)
        
        # Log event
        event = Event(
            session_id=session_id,
            user_id=request.user_id,
            event_type="query",
            payload={
                "query": request.query,
                "intent": intent,
                "keywords": keywords,
                "detected_category": detected_category
            }
        )
        db.add(event)
        db.commit()
        
        # Convert to response
        items = [ItemInfo(**item) for item in recommendations]
        
        return RecommendationResponse(
            query=request.query,
            intent=intent,
            detected_category=detected_category,
            recommendations=items,
            session_id=session_id
        )
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/item-details", response_model=ItemDetailResponse)
async def get_item_details(
    request: ItemDetailRequest,
    db: Session = Depends(get_db)
):
    """Get detailed information about an item"""
    try:
        rec_engine = RecommendationEngine(db)
        details = rec_engine.get_item_details(request.asin)
        
        if not details:
            raise HTTPException(status_code=404, detail="Item not found")
        
        return ItemDetailResponse(**details)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting item details: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat", response_model=ConversationResponse)
async def chat(
    request: ConversationRequest,
    db: Session = Depends(get_db)
):
    """Chat endpoint for multi-turn conversation"""
    try:
        # Get or create session
        db_session = db.query(DBSession).filter(DBSession.session_id == request.session_id).first()
        if not db_session:
            db_session = DBSession(session_id=request.session_id)
            db.add(db_session)
            db.commit()
        
        # Initialize recommendation engine
        rec_engine = RecommendationEngine(db)
        
        # Generate response and recommendations
        intent, keywords = rec_engine.understand_query(request.message)
        recommendations = rec_engine.generate_recommendations(request.message)
        
        # Create assistant response
        system_prompt = """你是一个专业的电商推荐助手。根据用户的需求，提供友好、有帮助的回复。
        你会获得推荐的商品列表，可以在回复中描述这些商品。"""
        
        assistant_message = ollama_client.generate_text(request.message, system_prompt)
        
        # Log event
        event = Event(
            session_id=request.session_id,
            event_type="chat",
            payload={
                "user_message": request.message,
                "intent": intent
            }
        )
        db.add(event)
        db.commit()
        
        # Convert recommendations
        items = [ItemInfo(**item) for item in recommendations]
        
        return ConversationResponse(
            session_id=request.session_id,
            assistant_response=assistant_message,
            recommendations=items
        )
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
