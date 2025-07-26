from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    image_url = Column(String)  # Stored in S3 or similar
    analysis_timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Scores
    symmetry_score = Column(Float)
    jawline_score = Column(Float)
    facial_ratio_score = Column(Float)
    skin_clarity_score = Column(Float)
    overall_score = Column(Float)
    
    # Analysis metadata
    landmarks_detected = Column(Boolean, default=False)
    face_detected = Column(Boolean, default=False)
    improvement_tips = Column(JSON)  # JSON array of tips
    
    # Relationships
    user = relationship("User", back_populates="analyses")
    exercise_recommendations = relationship("ExerciseRecommendation", back_populates="analysis")

class ExerciseRecommendation(Base):
    __tablename__ = "exercise_recommendations"

    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id"))
    exercise_id = Column(Integer, ForeignKey("exercises.id"))
    priority = Column(Integer)
    reason = Column(String)
    
    analysis = relationship("Analysis", back_populates="exercise_recommendations")
    exercise = relationship("Exercise")
