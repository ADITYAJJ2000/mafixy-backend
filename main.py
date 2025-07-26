import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Dict, List
import uuid

# Environment configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# FastAPI app configuration
app = FastAPI(
    title="Mafixy API",
    description="AI-powered facial analysis platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class UserCreate(BaseModel):
    email: str
    username: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class AnalysisRequest(BaseModel):
    image: str
    user_id: str = "user_123"

# Health check endpoints
@app.get("/")
async def root():
    return {
        "message": "Mafixy API is running!", 
        "status": "healthy",
        "version": "1.0.0",
        "environment": ENVIRONMENT
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "environment": ENVIRONMENT,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/ping")
async def ping():
    return {"message": "pong"}

# API endpoints
@app.post("/api/auth/register")
async def register(user: UserCreate):
    """Simple registration endpoint"""
    return {
        "message": "User registered successfully",
        "data": {
            "user": {
                "id": str(uuid.uuid4()),
                "email": user.email,
                "username": user.username
            },
            "token": "sample-jwt-token"
        }
    }

@app.post("/api/auth/login")
async def login(user: UserLogin):
    """Simple login endpoint"""
    return {
        "message": "Login successful",
        "data": {
            "user": {
                "id": str(uuid.uuid4()),
                "email": user.email
            },
            "token": "sample-jwt-token"
        }
    }

@app.post("/api/analyze-face")
async def analyze_face(request: AnalysisRequest):
    """Simple facial analysis endpoint (mock response)"""
    return {
        "message": "Analysis completed successfully",
        "data": {
            "id": str(uuid.uuid4()),
            "user_id": request.user_id,
            "scores": {
                "symmetry": 0.85,
                "jawline": 0.80,
                "facial_ratio": 0.88,
                "overall": 0.84
            },
            "improvement_tips": [
                "Great facial structure detected!",
                "Consider good lighting for better analysis",
                "Maintain a neutral expression for accurate results"
            ],
            "landmarks_detected": True,
            "analysis_timestamp": datetime.now().isoformat()
        }
    }

@app.get("/api/analysis-history/{user_id}")
async def get_analysis_history(user_id: str):
    """Get analysis history for a user"""
    return {
        "message": "Analysis history retrieved",
        "data": [
            {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "scores": {"overall": 0.85, "symmetry": 0.80},
                "timestamp": datetime.now().isoformat()
            }
        ]
    }

@app.post("/api/analysis-history")
async def save_analysis(analysis_data: dict):
    """Save analysis result"""
    return {
        "message": "Analysis saved successfully",
        "data": {"id": str(uuid.uuid4())}
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
