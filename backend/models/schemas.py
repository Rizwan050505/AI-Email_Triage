from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EmailBase(BaseModel):
    sender: str
    subject: str
    body: str

class EmailInput(EmailBase):
    pass

class EmailCreate(EmailBase):
    timestamp: str

class EmailResponse(EmailBase):
    id: int
    timestamp: str
    predicted_priority: Optional[str] = None
    predicted_action: Optional[str] = None
    
    class Config:
        from_attributes = True

class FeedbackCreate(BaseModel):
    email_id: int
    correct_priority: str
    correct_action: str

class ProcessedEmailResponse(BaseModel):
    email: EmailResponse
    predicted_priority: str
    predicted_action: str

class ChatRequest(BaseModel):
    message: str
    context: Optional[dict] = None

class ChatResponse(BaseModel):
    reply: str
