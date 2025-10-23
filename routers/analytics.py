from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Dict, Any
from datetime import datetime, timedelta

from database import get_db
from models import (
    Meeting, 
    MeetingAnalytics, 
    SentimentData, 
    WorkforceMetrics, 
    Participant
)
from schemas import (
    MeetingAnalytics as MeetingAnalyticsSchema,
    MeetingAnalyticsCreate,
    WorkforceMetrics as WorkforceMetricsSchema,
    WorkforceMetricsCreate,
    AnalyticsResponse,
    DashboardData
)

router = APIRouter()

@router.get("/dashboard", response_model=DashboardData)
async def get_dashboard_data(db: Session = Depends(get_db)):
    try:
        # Get recent meetings
        recent_meetings = db.query(Meeting).order_by(desc(Meeting.created_at)).limit(5).all()
        
        # Get analytics summary
        total_meetings = db.query(Meeting).count()
        avg_sentiment_result = db.query(func.avg(MeetingAnalytics.overall_sentiment_score)).scalar()
        avg_engagement_result = db.query(func.avg(MeetingAnalytics.engagement_score)).scalar()
        
        analytics_summary = {
            "total_meetings": total_meetings,
            "average_sentiment": round(avg_sentiment_result or 0.0, 2),
            "average_engagement": round(avg_engagement_result or 0.0, 2),
            "active_participants": db.query(Participant).count()
        }
        
        # Get sentiment trends (last 7 days)
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        sentiment_trends = []
        
        for i in range(7):
            date = seven_days_ago + timedelta(days=i)
            daily_sentiment_result = db.query(func.avg(SentimentData.sentiment_score)).filter(
                func.date(SentimentData.timestamp) == date.date()
            ).scalar()
            
            sentiment_trends.append({
                "date": date.strftime("%Y-%m-%d"),
                "sentiment": round(daily_sentiment_result or 0.0, 2)
            })
        
        # Get workforce insights by department
        workforce_insights = db.query(
            WorkforceMetrics.department,
            func.avg(WorkforceMetrics.metric_value).label("avg_value"),
            func.count(WorkforceMetrics.id).label("count")
        ).group_by(WorkforceMetrics.department).all()
        
        workforce_data = [
            {
                "department": insight.department or "Unknown",
                "average_metric": round(float(insight.avg_value or 0), 2),
                "data_points": insight.count
            }
            for insight in workforce_insights
        ]
        
        return DashboardData(
            recent_meetings=recent_meetings,
            analytics_summary=analytics_summary,
            sentiment_trends=sentiment_trends,
            workforce_insights=workforce_data
        )
    except Exception as e:
        print(f"Dashboard error: {e}")
        # Return empty data structure if there's an error
        return DashboardData(
            recent_meetings=[],
            analytics_summary={
                "total_meetings": 0,
                "average_sentiment": 0.0,
                "average_engagement": 0.0,
                "active_participants": 0
            },
            sentiment_trends=[],
            workforce_insights=[]
        )

@router.get("/meetings/{meeting_id}/analytics", response_model=MeetingAnalyticsSchema)
async def get_meeting_analytics(meeting_id: int, db: Session = Depends(get_db)):
    analytics = db.query(MeetingAnalytics).filter(
        MeetingAnalytics.meeting_id == meeting_id
    ).first()
    
    if analytics is None:
        raise HTTPException(status_code=404, detail="Analytics not found for this meeting")
    
    return analytics

@router.post("/meetings/{meeting_id}/analytics", response_model=MeetingAnalyticsSchema)
async def create_meeting_analytics(
    meeting_id: int, 
    analytics: MeetingAnalyticsCreate, 
    db: Session = Depends(get_db)
):
    # Check if meeting exists
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    # Check if analytics already exist
    existing_analytics = db.query(MeetingAnalytics).filter(
        MeetingAnalytics.meeting_id == meeting_id
    ).first()
    
    if existing_analytics:
        raise HTTPException(status_code=400, detail="Analytics already exist for this meeting")
    
    analytics_data = analytics.dict()
    analytics_data["meeting_id"] = meeting_id
    
    db_analytics = MeetingAnalytics(**analytics_data)
    db.add(db_analytics)
    db.commit()
    db.refresh(db_analytics)
    
    return db_analytics

@router.put("/meetings/{meeting_id}/analytics", response_model=MeetingAnalyticsSchema)
async def update_meeting_analytics(
    meeting_id: int, 
    analytics_update: MeetingAnalyticsCreate, 
    db: Session = Depends(get_db)
):
    analytics = db.query(MeetingAnalytics).filter(
        MeetingAnalytics.meeting_id == meeting_id
    ).first()
    
    if analytics is None:
        raise HTTPException(status_code=404, detail="Analytics not found for this meeting")
    
    for key, value in analytics_update.dict(exclude_unset=True).items():
        setattr(analytics, key, value)
    
    db.commit()
    db.refresh(analytics)
    return analytics

@router.get("/sentiment/trends")
async def get_sentiment_trends(days: int = 30, db: Session = Depends(get_db)):
    start_date = datetime.utcnow() - timedelta(days=days)
    
    trends = db.query(
        func.date(SentimentData.timestamp).label("date"),
        func.avg(SentimentData.sentiment_score).label("avg_sentiment"),
        func.count(SentimentData.id).label("data_points")
    ).filter(
        SentimentData.timestamp >= start_date
    ).group_by(
        func.date(SentimentData.timestamp)
    ).order_by("date").all()
    
    return [
        {
            "date": trend.date.strftime("%Y-%m-%d"),
            "average_sentiment": round(trend.avg_sentiment, 3),
            "data_points": trend.data_points
        }
        for trend in trends
    ]

@router.get("/workforce/metrics", response_model=List[WorkforceMetricsSchema])
async def get_workforce_metrics(
    department: str = None, 
    metric_name: str = None,
    db: Session = Depends(get_db)
):
    query = db.query(WorkforceMetrics)
    
    if department:
        query = query.filter(WorkforceMetrics.department == department)
    if metric_name:
        query = query.filter(WorkforceMetrics.metric_name == metric_name)
    
    metrics = query.order_by(desc(WorkforceMetrics.metric_date)).all()
    return metrics

@router.post("/workforce/metrics", response_model=WorkforceMetricsSchema)
async def create_workforce_metric(metric: WorkforceMetricsCreate, db: Session = Depends(get_db)):
    db_metric = WorkforceMetrics(**metric.dict())
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    return db_metric

@router.get("/summary")
async def get_analytics_summary(db: Session = Depends(get_db)):
    # Overall statistics
    total_meetings = db.query(Meeting).count()
    total_participants = db.query(Participant).count()
    
    # Sentiment analysis
    avg_sentiment = db.query(func.avg(MeetingAnalytics.overall_sentiment_score)).scalar() or 0
    positive_meetings = db.query(MeetingAnalytics).filter(
        MeetingAnalytics.overall_sentiment_score > 0.5
    ).count()
    
    # Engagement metrics
    avg_engagement = db.query(func.avg(MeetingAnalytics.engagement_score)).scalar() or 0
    high_engagement_meetings = db.query(MeetingAnalytics).filter(
        MeetingAnalytics.engagement_score > 0.7
    ).count()
    
    # Department breakdown
    dept_metrics = db.query(
        Participant.department,
        func.count(Participant.id).label("participant_count")
    ).filter(
        Participant.department.isnot(None)
    ).group_by(Participant.department).all()
    
    return {
        "overview": {
            "total_meetings": total_meetings,
            "total_participants": total_participants,
            "average_sentiment": round(avg_sentiment, 3),
            "positive_meetings_percentage": round((positive_meetings / max(total_meetings, 1)) * 100, 1),
            "average_engagement": round(avg_engagement, 3),
            "high_engagement_percentage": round((high_engagement_meetings / max(total_meetings, 1)) * 100, 1)
        },
        "departments": [
            {
                "name": dept.department,
                "participant_count": dept.participant_count
            }
            for dept in dept_metrics
        ]
    }