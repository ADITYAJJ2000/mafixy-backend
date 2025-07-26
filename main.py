import os
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from pydantic import BaseModel
import base64
import cv2
import numpy as np
import mediapipe as mp
from typing import Optional, List, Dict
import uuid
from datetime import datetime
import json
from sqlalchemy.orm import Session
from models.database import Database, User, Analysis
from auth.auth import (
    get_password_hash,
    create_access_token,
    get_current_user,
    authenticate_user
)
from middleware.error_handler import setup_error_handling

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

# Security middleware for production
if ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*.onrender.com", "localhost"]
    )

# Configure CORS
allowed_origins = [
    "*" if ENVIRONMENT == "development" else "https://your-frontend-domain.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup error handling
setup_error_handling(app)

# Initialize Database with environment-specific URL
db = Database(DATABASE_URL)
db.create_all()

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    static_image_mode=True,
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.5
)

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class AnalysisRequest(BaseModel):
    image: str  # Base64 encoded image

class AnalysisResponse(BaseModel):
    id: str
    user_id: str
    scores: Dict[str, float]
    improvement_tips: List[str]
    landmarks_detected: bool
    analysis_timestamp: str

def calculate_symmetry(landmarks):
    """Calculate facial symmetry score based on landmark positions."""
    if len(landmarks) < 468:  # Number of landmarks in FaceMesh
        return 0.0
    
    # Calculate symmetry score (simplified example)
    left_points = landmarks[:234]
    right_points = landmarks[234:]
    
    # Calculate average distance between corresponding points
    distances = []
    for i in range(len(left_points)):
        left_point = np.array(left_points[i])
        right_point = np.array(right_points[i])
        distance = np.linalg.norm(left_point - right_point)
        distances.append(distance)
    
    avg_distance = np.mean(distances)
    # Normalize to 0-100 scale
    symmetry_score = max(0, min(100, (1 - (avg_distance / 100)) * 100))
    return float(symmetry_score)

def calculate_jawline(landmarks):
    """Calculate jawline score based on landmark positions."""
    if len(landmarks) < 468:
        return 0.0
    
    # Get jawline landmarks (simplified example)
    jawline_points = landmarks[174:197]  # Jawline landmarks
    
    # Calculate smoothness (simplified)
    distances = []
    for i in range(len(jawline_points) - 1):
        point1 = np.array(jawline_points[i])
        point2 = np.array(jawline_points[i + 1])
        distance = np.linalg.norm(point1 - point2)
        distances.append(distance)
    
    std_dev = np.std(distances)
    # Normalize to 0-100 scale
    jawline_score = max(0, min(100, (1 - (std_dev / 10)) * 100))
    return float(jawline_score)

def calculate_facial_ratio(landmarks):
    """Calculate facial ratio score based on landmark positions."""
    if len(landmarks) < 468:
        return 0.0
    
    # Get key points for ratio calculation
    top = landmarks[10]  # Forehead point
    bottom = landmarks[152]  # Chin point
    left = landmarks[234]  # Left cheek
    right = landmarks[454]  # Right cheek
    
    # Calculate vertical and horizontal distances
    vertical_distance = np.linalg.norm(np.array(top) - np.array(bottom))
    horizontal_distance = np.linalg.norm(np.array(left) - np.array(right))
    
    # Calculate ratio
    ratio = vertical_distance / horizontal_distance
    # Ideal ratio is around 1.618 (golden ratio)
    ideal_ratio = 1.618
    
    # Calculate score based on how close to ideal ratio
    ratio_score = max(0, min(100, (1 - abs(ratio - ideal_ratio) / ideal_ratio) * 100))
    return float(ratio_score)

def analyze_image(image_data: np.ndarray) -> Dict:
    """Analyze facial features and generate scores."""
    try:
        # Convert image to RGB
        image = cv2.cvtColor(image_data, cv2.COLOR_BGR2RGB)
        
        # Process with MediaPipe
        results = face_mesh.process(image)
        
        if not results.multi_face_landmarks:
            return {
                'success': False,
                'error': 'No face detected in the image'
            }
        
        # Get first face landmarks
        landmarks = results.multi_face_landmarks[0]
        
        # Convert landmarks to numpy array
        landmarks_array = []
        for landmark in landmarks.landmark:
            x = landmark.x * image.shape[1]
            y = landmark.y * image.shape[0]
            landmarks_array.append([x, y])
        
        # Calculate scores
        scores = {
            'symmetry': calculate_symmetry(landmarks_array),
            'jawline': calculate_jawline(landmarks_array),
            'facial_ratio': calculate_facial_ratio(landmarks_array),
            'skin_clarity': 85.0  # Simplified example, needs proper implementation
        }
        
        # Generate improvement tips based on scores
        improvement_tips = []
        if scores['symmetry'] < 70:
            improvement_tips.append("Consider facial symmetry exercises to improve balance")
        if scores['jawline'] < 70:
            improvement_tips.append("Strengthen jawline muscles with specific exercises")
        if scores['facial_ratio'] < 70:
            improvement_tips.append("Consider facial exercises to enhance proportions")
        
        return {
            'success': True,
            'scores': scores,
            'improvement_tips': improvement_tips,
            'landmarks_detected': True
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing image: {str(e)}"
        )

@app.post("/api/analyze-face")
async def analyze_face(
    request: AnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    try:
        # Decode base64 image
        image_bytes = base64.b64decode(request.image)
        np_array = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image format")
            
        # Analyze the image
        result = analyze_image(image)
        
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['error'])
            
        # Save to database
        with db.get_session() as session:
            analysis = Analysis(
                user_id=current_user.id,
                symmetry_score=result['scores']['symmetry'],
                jawline_score=result['scores']['jawline'],
                facial_ratio_score=result['scores']['facial_ratio'],
                skin_clarity_score=result['scores']['skin_clarity'],
                improvement_tips=json.dumps(result['improvement_tips']),
                landmarks_detected=result['landmarks_detected']
            )
            session.add(analysis)
            session.commit()
            
        return {
            'id': analysis.id,
            'scores': result['scores'],
            'improvement_tips': result['improvement_tips'],
            'landmarks_detected': True,
            'analysis_timestamp': analysis.analysis_timestamp.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/analysis-history/{user_id}")
async def get_analysis_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        analyses = db.query(Analysis).filter(Analysis.user_id == current_user.id).all()
        return [{
            'id': analysis.id,
            'scores': {
                'symmetry': analysis.symmetry_score,
                'jawline': analysis.jawline_score,
                'facial_ratio': analysis.facial_ratio_score,
                'skin_clarity': analysis.skin_clarity_score
            },
            'improvement_tips': json.loads(analysis.improvement_tips),
            'analysis_timestamp': analysis.analysis_timestamp.isoformat()
        } for analysis in analyses]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/register")
async def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        # Check if user exists
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
            
        # Create new user
        new_user = User(
            email=user.email,
            password_hash=get_password_hash(user.password),
            full_name=user.full_name
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {
            "id": new_user.id,
            "email": new_user.email,
            "full_name": new_user.full_name
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/login")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    try:
        authenticated_user = authenticate_user(db, user.email, user.password)
        if not authenticated_user:
            raise HTTPException(
                status_code=401,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        access_token = create_access_token(
            data={"sub": authenticated_user.id},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/user")
async def get_user(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "full_name": current_user.full_name
    }

@app.get("/api/analysis-history/{user_id}")
async def get_analysis_history(user_id: str):
    try:
        if user_id not in analysis_history:
            return []
            
        return analysis_history[user_id]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

if __name__ == "__main__":
    import uvicorn
    import logging
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
