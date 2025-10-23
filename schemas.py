from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional, Dict, Any


class MeetingBase(BaseModel):
    title: str
    description: Optional[str] = None
    date: datetime
    duration: Optional[int] = None

class MeetingCreate(MeetingBase):
    pass

class Meeting(MeetingBase):
    id: int
    participants_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ParticipantBase(BaseModel):
    name: str
    email: str
    role: Optional[str] = None
    department: Optional[str] = None

class ParticipantCreate(ParticipantBase):
    meeting_id: int

class Participant(ParticipantBase):
    id: int
    meeting_id: int
    
    class Config:
        from_attributes = True


class MeetingAnalyticsBase(BaseModel):
    overall_sentiment_score: Optional[float] = None
    engagement_score: Optional[float] = None
    productivity_score: Optional[float] = None
    key_topics: Optional[str] = None
    action_items: Optional[str] = None
    summary: Optional[str] = None

class MeetingAnalyticsCreate(MeetingAnalyticsBase):
    meeting_id: int

class MeetingAnalytics(MeetingAnalyticsBase):
    id: int
    meeting_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Sentiment data schemas
class SentimentDataBase(BaseModel):
    timestamp: datetime
    sentiment_score: float
    emotion: Optional[str] = None
    confidence: Optional[float] = None
    text_snippet: Optional[str] = None

class SentimentDataCreate(SentimentDataBase):
    participant_id: int

class SentimentData(SentimentDataBase):
    id: int
    participant_id: int
    
    class Config:
        from_attributes = True


class DataConnectorBase(BaseModel):
    name: str
    connector_type: str
    status: Optional[str] = "active"
    config: Optional[str] = None

class DataConnectorCreate(DataConnectorBase):
    pass

class DataConnector(DataConnectorBase):
    id: int
    last_sync: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class WorkforceMetricsBase(BaseModel):
    department: str
    metric_name: str
    metric_value: float
    metric_date: datetime

class WorkforceMetricsCreate(WorkforceMetricsBase):
    pass

class WorkforceMetrics(WorkforceMetricsBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Response schemas
class AnalyticsResponse(BaseModel):
    meeting_analytics: List[MeetingAnalytics]
    workforce_metrics: List[WorkforceMetrics]
    total_meetings: int
    average_sentiment: float

class DashboardData(BaseModel):
    recent_meetings: List[Meeting]
    analytics_summary: Dict[str, Any]
    sentiment_trends: List[Dict[str, Any]]
    workforce_insights: List[Dict[str, Any]]