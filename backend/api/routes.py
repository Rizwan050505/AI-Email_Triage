from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from backend.models import schemas, db_models
from backend.database.database import get_db
from backend.database import crud
from backend.services.nlp_classifier import classifier
from backend.services.decision_engine import decision_engine
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from chatbot.agent import NLPChatbotAgent

router = APIRouter()
chatbot_agent = NLPChatbotAgent()

@router.post("/predict", response_model=Dict[str, str])
def predict_priority(email: schemas.EmailInput):
    priority = classifier.predict(email.subject, email.body)
    return {"priority": priority}

@router.post("/decide", response_model=Dict[str, str])
def decide_action(email: schemas.EmailCreate, predicted_priority: str):
    action = decision_engine.decide(predicted_priority, email.sender, email.timestamp)
    return {"action": action}

@router.post("/process", response_model=schemas.ProcessedEmailResponse)
def process_email(email: schemas.EmailCreate):
    priority = classifier.predict(email.subject, email.body)
    action = decision_engine.decide(priority, email.sender, email.timestamp)
    
    response_email = schemas.EmailResponse(
        id=int(datetime.now().timestamp()), # dummy ID for stateless processing
        sender=email.sender,
        subject=email.subject,
        body=email.body,
        timestamp=email.timestamp,
        predicted_priority=priority,
        predicted_action=action
    )
    
    return schemas.ProcessedEmailResponse(
        email=response_email,
        predicted_priority=priority,
        predicted_action=action
    )

@router.post("/feedback")
def submit_feedback(feedback: schemas.FeedbackCreate, db: Session = Depends(get_db)):
    # In a real system, you'd fetch the original email. Here we assume we only have feedback ID and need to associate.
    # For a robust implementation, let's create a minimal record.
    dummy_email = schemas.EmailInput(sender="unknown", subject="unknown", body="unknown")
    crud.create_feedback(db=db, feedback=feedback, email=dummy_email, pred_priority="unknown", pred_action="unknown")
    return {"message": "Feedback received successfully."}

@router.post("/chat", response_model=schemas.ChatResponse)
def get_chat_response(request: schemas.ChatRequest):
    reply = chatbot_agent.get_response(request.message, context=request.context)
    return schemas.ChatResponse(reply=reply)

@router.get("/dataset", response_model=List[schemas.EmailResponse])
def get_dataset():
    # Helper endpoint for the frontend to fetch emails
    import json
    from backend.config.settings import settings
    import os
    
    if not os.path.exists(settings.DATASET_PATH):
       return []
       
    with open(settings.DATASET_PATH, 'r') as f:
        data = json.load(f)
        
    responses = []
    for item in data[:50]: # limit to 50 for UI
        priority = classifier.predict(item['subject'], item['body'])
        action = decision_engine.decide(priority, item['sender'], item['timestamp'])
        responses.append(schemas.EmailResponse(
            id=item["id"],
            sender=item["sender"],
            subject=item["subject"],
            body=item["body"],
            timestamp=item["timestamp"],
            predicted_priority=priority,
            predicted_action=action
        ))
    return responses
