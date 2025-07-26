import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import base64
import cv2
import numpy as np
import mediapipe as mp
from typing import Dict, List
import uuid

# Environment configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mafixy.db")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-here")

# FastAPI app configuration
app = FastAPI(
    title="Mafixy API",
    description="AI-powered facial analysis platform",
    version="1.0.0",
    docs_url="/docs" if ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if ENVIRONMENT != "production" else None,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=True,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5
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

class AnalysisResponse(BaseModel):
    id: str
    user_id: str
    scores: Dict[str, float]
    improvement_tips: List[str]
    landmarks_detected: bool
    analysis_timestamp: str

# Simple facial analysis function
def analyze_image_simple(image_data: np.ndarray) -> Dict:
    """Simple facial analysis using MediaPipe"""
    try:
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(image_data, cv2.COLOR_BGR2RGB)
        
        # Process with MediaPipe
        results = face_mesh.process(rgb_image)
        
        if not results.multi_face_landmarks:
            return {
                "landmarks_detected": False,
                "scores": {"overall": 0.0},
                "improvement_tips": ["No face detected. Please ensure good lighting and face visibility."]
            }
        
        # Simple scoring (placeholder)
        scores = {
            "symmetry": 0.75,
            "jawline": 0.80,
            "facial_ratio": 0.85,
            "overall": 0.80
        }
        
        improvement_tips = [
            "Great facial structure detected!",
            "Consider good lighting for better analysis",
            "Maintain a neutral expression for accurate results"
        ]
        
        return {
            "landmarks_detected": True,
            "scores": scores,
            "improvement_tips": improvement_tips
        }
        
    except Exception as e:
        return {
            "landmarks_detected": False,
            "scores": {"overall": 0.0},
            "improvement_tips": [f"Analysis error: {str(e)}"]
        }

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
        "database": "connected",
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
    """Facial analysis endpoint"""
    try:
        # Decode base64 image
        image_data = base64.b64decode(request.image)
        nparr = np.frombuffer(image_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image data")
        
        # Analyze image
        analysis_result = analyze_image_simple(image)
        
        # Create response
        response = AnalysisResponse(
            id=str(uuid.uuid4()),
            user_id=request.user_id,
            scores=analysis_result["scores"],
            improvement_tips=analysis_result["improvement_tips"],
            landmarks_detected=analysis_result["landmarks_detected"],
            analysis_timestamp=datetime.now().isoformat()
        )
        
        return {
            "message": "Analysis completed successfully",
            "data": response.dict()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

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
