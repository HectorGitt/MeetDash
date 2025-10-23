from sqlalchemy import Column, Integer, String, DateTime, Text, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class Meeting(Base):
    __tablename__ = "meetings"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    date = Column(DateTime, nullable=False)
    duration = Column(Integer)  # Duration in minutes
    participants_count = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    participants = relationship("Participant", back_populates="meeting")
    analytics = relationship("MeetingAnalytics", back_populates="meeting", uselist=False)

class Participant(Base):
    __tablename__ = "participants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    role = Column(String)
    department = Column(String)
    meeting_id = Column(Integer, ForeignKey("meetings.id"))
    
    # Relationships
    meeting = relationship("Meeting", back_populates="participants")
    sentiment_data = relationship("SentimentData", back_populates="participant")

class MeetingAnalytics(Base):
    __tablename__ = "meeting_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    meeting_id = Column(Integer, ForeignKey("meetings.id"), unique=True)
    overall_sentiment_score = Column(Float)
    engagement_score = Column(Float)
    productivity_score = Column(Float)
    key_topics = Column(Text)  # JSON string of topics
    action_items = Column(Text)  # JSON string of action items
    summary = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    meeting = relationship("Meeting", back_populates="analytics")

class SentimentData(Base):
    __tablename__ = "sentiment_data"
    
    id = Column(Integer, primary_key=True, index=True)
    participant_id = Column(Integer, ForeignKey("participants.id"))
    timestamp = Column(DateTime, nullable=False)
    sentiment_score = Column(Float)  # -1 to 1 scale
    emotion = Column(String)  # happy, sad, neutral, etc.
    confidence = Column(Float)  # 0 to 1 scale
    text_snippet = Column(Text)
    
    # Relationships
    participant = relationship("Participant", back_populates="sentiment_data")

class DataConnector(Base):
    __tablename__ = "data_connectors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    connector_type = Column(String, nullable=False)  # fivetran, custom, etc.
    status = Column(String, default="active")  # active, inactive, error
    last_sync = Column(DateTime)
    config = Column(Text)  # JSON configuration
    created_at = Column(DateTime, server_default=func.now())
    
class WorkforceMetrics(Base):
    __tablename__ = "workforce_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    department = Column(String, nullable=False)
    metric_name = Column(String, nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())