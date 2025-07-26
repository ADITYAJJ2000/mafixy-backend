from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import uuid
from typing import List

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    analyses = relationship("Analysis", back_populates="user")

class Analysis(Base):
    __tablename__ = 'analyses'
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    
    # Scores
    symmetry_score = Column(Float, nullable=False)
    jawline_score = Column(Float, nullable=False)
    facial_ratio_score = Column(Float, nullable=False)
    skin_clarity_score = Column(Float, nullable=False)
    
    # Improvement tips
    improvement_tips = Column(Text, nullable=False)  # JSON string
    
    # Metadata
    landmarks_detected = Column(Boolean, nullable=False)
    analysis_timestamp = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="analyses")

class Database:
    def __init__(self, db_url: str):
        self.engine = create_engine(db_url)
        self.Session = sessionmaker(bind=self.engine)
        
    def create_all(self):
        Base.metadata.create_all(self.engine)
        
    def get_session(self):
        return self.Session()

def get_db():
    """Dependency for FastAPI"""
    db = Database('sqlite:///./mafixy.db')  # Change to PostgreSQL in production
    try:
        yield db
    finally:
        pass  # Session is handled by FastAPI context
