from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from database import get_db
from models import Meeting, Participant, DataConnector, SentimentData
from schemas import (
    Meeting as MeetingSchema,
    MeetingCreate,
    Participant as ParticipantSchema,
    ParticipantCreate,
    DataConnector as DataConnectorSchema,
    DataConnectorCreate,
    SentimentData as SentimentDataSchema,
    SentimentDataCreate
)

router = APIRouter()

# Meeting endpoints
@router.get("/meetings", response_model=List[MeetingSchema])
async def get_meetings(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    meetings = db.query(Meeting).offset(skip).limit(limit).all()
    return meetings

@router.post("/meetings", response_model=MeetingSchema)
async def create_meeting(meeting: MeetingCreate, db: Session = Depends(get_db)):
    db_meeting = Meeting(**meeting.dict())
    db.add(db_meeting)
    db.commit()
    db.refresh(db_meeting)
    return db_meeting

@router.get("/meetings/{meeting_id}", response_model=MeetingSchema)
async def get_meeting(meeting_id: int, db: Session = Depends(get_db)):
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if meeting is None:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting

@router.put("/meetings/{meeting_id}", response_model=MeetingSchema)
async def update_meeting(meeting_id: int, meeting_update: MeetingCreate, db: Session = Depends(get_db)):
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if meeting is None:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    for key, value in meeting_update.dict().items():
        setattr(meeting, key, value)
    
    meeting.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(meeting)
    return meeting

@router.delete("/meetings/{meeting_id}")
async def delete_meeting(meeting_id: int, db: Session = Depends(get_db)):
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    if meeting is None:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    db.delete(meeting)
    db.commit()
    return {"message": "Meeting deleted successfully"}

# Participant endpoints
@router.get("/participants", response_model=List[ParticipantSchema])
async def get_participants(meeting_id: int = None, db: Session = Depends(get_db)):
    query = db.query(Participant)
    if meeting_id:
        query = query.filter(Participant.meeting_id == meeting_id)
    participants = query.all()
    return participants

@router.post("/participants", response_model=ParticipantSchema)
async def create_participant(participant: ParticipantCreate, db: Session = Depends(get_db)):
    # Check if meeting exists
    meeting = db.query(Meeting).filter(Meeting.id == participant.meeting_id).first()
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    db_participant = Participant(**participant.dict())
    db.add(db_participant)
    
    
    meeting.participants_count += 1
    
    db.commit()
    db.refresh(db_participant)
    return db_participant

# Data connector endpoints
@router.get("/connectors", response_model=List[DataConnectorSchema])
async def get_connectors(db: Session = Depends(get_db)):
    connectors = db.query(DataConnector).all()
    return connectors

@router.post("/connectors", response_model=DataConnectorSchema)
async def create_connector(connector: DataConnectorCreate, db: Session = Depends(get_db)):
    db_connector = DataConnector(**connector.dict())
    db.add(db_connector)
    db.commit()
    db.refresh(db_connector)
    return db_connector

@router.put("/connectors/{connector_id}/sync")
async def sync_connector(connector_id: int, db: Session = Depends(get_db)):
    connector = db.query(DataConnector).filter(DataConnector.id == connector_id).first()
    if connector is None:
        raise HTTPException(status_code=404, detail="Connector not found")
    
    # Update last sync time
    connector.last_sync = datetime.utcnow()
    db.commit()
    
    return {"message": f"Connector {connector.name} synced successfully"}

# Sentiment data endpoints
@router.get("/sentiment", response_model=List[SentimentDataSchema])
async def get_sentiment_data(participant_id: int = None, db: Session = Depends(get_db)):
    query = db.query(SentimentData)
    if participant_id:
        query = query.filter(SentimentData.participant_id == participant_id)
    sentiment_data = query.all()
    return sentiment_data

@router.post("/sentiment", response_model=SentimentDataSchema)
async def create_sentiment_data(sentiment: SentimentDataCreate, db: Session = Depends(get_db)):
    db_sentiment = SentimentData(**sentiment.dict())
    db.add(db_sentiment)
    db.commit()
    db.refresh(db_sentiment)
    return db_sentiment