"""
Task A — User Modeling API
Endpoint: POST /generate-review
Input:  user_persona (dict) + product_details (dict)
Output: rating (float) + review_text (str) + reasoning (str)
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Any
import uvicorn

from agents.review_generator import generate_review

app = FastAPI(
    title="DSN×BCT Task A — User Modeling API",
    description="Generates behaviorally faithful user reviews and ratings based on individual user history and Nigerian cultural context.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


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


class ProductDetails(BaseModel):
    item_id: str = "item_001"
    name: str
    category: str = ""
    description: str = ""
    cuisine: str = ""
    price_range: str = ""
    location: str = ""
    avg_rating: float | None = None
    tags: list[str] = Field(default_factory=list)


class ReviewRequest(BaseModel):
    user_persona: UserPersona
    product_details: ProductDetails


class ReviewResponse(BaseModel):
    rating: float
    review: str
    reasoning: str
    user_profile_summary: dict[str, Any]


@app.get("/")
def root():
    return {
        "service": "Task A — User Modeling",
        "status": "online",
        "endpoints": {
            "POST /generate-review": "Generate a simulated review for a user-item pair",
            "GET /health": "Health check",
            "GET /example": "Get an example request payload",
        },
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/example")
def example():
    return {
        "user_persona": {
            "user_id": "u_chidi",
            "name": "Chidi",
            "location": "Lagos, Nigeria",
            "preferences": ["spicy food", "good service", "value for money"],
            "review_history": [
                {
                    "item": "Chicken Republic",
                    "rating": 3.5,
                    "review": "The chicken was okay but e take time small. Price reasonable sha.",
                    "category": "restaurant",
                },
                {
                    "item": "Yellow Chilli",
                    "rating": 4.5,
                    "review": "E sweet me die! The oxtail pepper soup na the best in Lagos. Service top notch.",
                    "category": "restaurant",
                },
                {
                    "item": "Mama Cass",
                    "rating": 4.0,
                    "review": "Consistent quality. Their jollof rice always dey there for you. No dulling.",
                    "category": "restaurant",
                },
            ],
        },
        "product_details": {
            "item_id": "ng_r003",
            "name": "Kilimanjaro Restaurant",
            "category": "restaurant",
            "cuisine": "Nigerian",
            "description": "Known for grills, suya and Nigerian continental dishes. Located in Lekki.",
            "price_range": "$$",
            "location": "Lekki, Lagos",
            "tags": ["nigerian", "grills", "suya", "lekki"],
        },
    }


@app.post("/generate-review", response_model=ReviewResponse)
def generate_review_endpoint(request: ReviewRequest):
    try:
        persona_dict = request.user_persona.model_dump()
        product_dict = request.product_details.model_dump()
        result = generate_review(persona_dict, product_dict)
        return ReviewResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=False)
