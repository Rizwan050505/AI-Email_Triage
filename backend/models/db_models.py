from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class DBEmail(Base):
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String, index=True)
    subject = Column(String)
    body = Column(Text)
    timestamp = Column(String)
    
class DBFeedback(Base):
    __tablename__ = "feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(Integer)
    sender = Column(String)
    subject = Column(String)
    body = Column(Text)
    predicted_priority = Column(String)
    predicted_action = Column(String)
    correct_priority = Column(String)
    correct_action = Column(String)
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
