from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import Base

class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)
    category = Column(String)  # e.g., symmetry, jawline, etc.
    difficulty = Column(String)  # easy, medium, hard
    duration_minutes = Column(Float)
    video_url = Column(String)  # URL to exercise video
    instructions = Column(JSON)  # JSON array of step-by-step instructions
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    recommendations = relationship("ExerciseRecommendation", back_populates="exercise")
    history = relationship("ExerciseHistory", back_populates="exercise")

class ExerciseHistory(Base):
    __tablename__ = "exercise_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    exercise_id = Column(Integer, ForeignKey("exercises.id"))
    completed_at = Column(DateTime, default=datetime.utcnow)
    duration_seconds = Column(Float)
    success_rate = Column(Float)  # 0.0 to 1.0
    notes = Column(String)
    
    user = relationship("User", back_populates="exercise_history")
    exercise = relationship("Exercise", back_populates="history")

class Achievement(Base):
    __tablename__ = "achievements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, nullable=False)
    description = Column(String)
    type = Column(String)  # streak, milestone, etc.
    unlocked_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON)  # JSON for achievement-specific data
    
    user = relationship("User", back_populates="achievements")
