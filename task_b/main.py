"""
Task B — Recommendation API
Endpoints:
  POST /recommend         — single-turn personalised recommendations
  POST /recommend/chat    — multi-turn conversational recommendations
  GET  /catalog           — browse available items
"""

import uuid
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from agents.recommender_agent import get_recommendations

app = FastAPI(
    title="DSN×BCT Task B — Recommendation API",
    description="Agentic personalised recommendation system using iterative search and reasoning to match items to individual Nigerian user profiles.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory conversation store (use Redis in production)
_conversations: dict[str, list[dict]] = {}


class ReviewHistory(BaseModel):
    item: str
    rating: float = Field(ge=1.0, le=5.0)
    review: str = ""
    category: str = ""


class UserPersona(BaseModel):
    user_id: str = "user_001"
    name: str = "User"
    location: str = "Lagos, Nigeria"
    review_history: list[ReviewHistory] = Field(default_factory=list)
    preferences: list[str] = Field(default_factory=list)


class RecommendRequest(BaseModel):
    user_persona: UserPersona
    context: dict[str, Any] = Field(
        default_factory=dict,
        description="Optional context: mood, occasion, budget, category preference, etc.",
    )
    num_recommendations: int = Field(default=5, ge=1, le=20)


class ChatRecommendRequest(BaseModel):
    user_persona: UserPersona
    message: str = Field(description="User's natural language message/follow-up")
    conversation_id: str | None = None
    num_recommendations: int = Field(default=5, ge=1, le=10)


class RecommendationItem(BaseModel):
    item_id: str
    name: str
    category: str = ""
    score: float
    reason: str


class RecommendResponse(BaseModel):
    recommendations: list[RecommendationItem]
    overall_reasoning: str
    cold_start_strategy: str = ""
    is_cold_start: bool
    user_profile_summary: dict[str, Any]
    conversation_id: str | None = None


@app.get("/")
def root():
    return {
        "service": "Task B — Recommendation",
        "status": "online",
        "endpoints": {
            "POST /recommend": "Single-turn personalised recommendations",
            "POST /recommend/chat": "Multi-turn conversational recommendations",
            "GET /catalog": "Browse available items",
            "GET /example": "Example request payload",
        },
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/catalog")
def get_catalog():
    from shared.sample_catalog import get_all_items
    items = get_all_items()
    categories: dict[str, list] = {}
    for item in items:
        cat = item.get("category", "other")
        categories.setdefault(cat, []).append({"id": item["id"], "name": item["name"]})
    return {"total": len(items), "categories": categories}


@app.get("/example")
def example():
    return {
        "user_persona": {
            "user_id": "u_ngozi",
            "name": "Ngozi",
            "location": "Abuja, Nigeria",
            "preferences": ["afrobeats music", "fine dining", "self-improvement books"],
            "review_history": [
                {"item": "Nkoyo Restaurant", "rating": 5.0, "review": "Best restaurant in Abuja, period.", "category": "restaurant"},
                {"item": "Atomic Habits", "rating": 4.5, "review": "Changed my life. Practical and easy to apply.", "category": "book"},
                {"item": "Burna Boy - African Giant", "rating": 5.0, "review": "A masterpiece. Every track is a vibe.", "category": "music"},
            ],
        },
        "context": {
            "occasion": "Date night",
            "mood": "celebratory",
            "budget": "premium",
        },
        "num_recommendations": 5,
    }


@app.post("/recommend", response_model=RecommendResponse)
def recommend(request: RecommendRequest):
    try:
        result = get_recommendations(
            user_persona=request.user_persona.model_dump(),
            context=request.context,
            num_recommendations=request.num_recommendations,
        )
        recs = [RecommendationItem(**r) for r in result.get("recommendations", [])]
        return RecommendResponse(
            recommendations=recs,
            overall_reasoning=result.get("overall_reasoning", ""),
            cold_start_strategy=result.get("cold_start_strategy", ""),
            is_cold_start=result.get("is_cold_start", False),
            user_profile_summary=result.get("user_profile_summary", {}),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/recommend/chat", response_model=RecommendResponse)
def recommend_chat(request: ChatRecommendRequest):
    """
    Multi-turn conversational recommendation.
    Pass conversation_id from a previous response to continue the session.
    """
    try:
        conv_id = request.conversation_id or str(uuid.uuid4())
        history = _conversations.get(conv_id, [])

        # Prepend the user's chat message as context
        context = {"user_message": request.message}

        result = get_recommendations(
            user_persona=request.user_persona.model_dump(),
            context=context,
            num_recommendations=request.num_recommendations,
            conversation_history=history if history else None,
        )

        # Store updated conversation (trim to last 20 messages to avoid bloat)
        _conversations[conv_id] = result.get("updated_conversation", [])[-20:]

        recs = [RecommendationItem(**r) for r in result.get("recommendations", [])]
        return RecommendResponse(
            recommendations=recs,
            overall_reasoning=result.get("overall_reasoning", ""),
            cold_start_strategy=result.get("cold_start_strategy", ""),
            is_cold_start=result.get("is_cold_start", False),
            user_profile_summary=result.get("user_profile_summary", {}),
            conversation_id=conv_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=False)
