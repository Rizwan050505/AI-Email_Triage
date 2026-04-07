from sqlalchemy.orm import Session
from backend.models import db_models, schemas

def create_feedback(db: Session, feedback: schemas.FeedbackCreate, email: schemas.EmailInput, pred_priority: str, pred_action: str):
    db_feedback = db_models.DBFeedback(
        email_id=feedback.email_id,
        sender=email.sender,
        subject=email.subject,
        body=email.body,
        predicted_priority=pred_priority,
        predicted_action=pred_action,
        correct_priority=feedback.correct_priority,
        correct_action=feedback.correct_action
    )
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

def get_all_feedback(db: Session):
    return db.query(db_models.DBFeedback).all()
