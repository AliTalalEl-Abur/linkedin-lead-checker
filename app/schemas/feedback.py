from datetime import datetime
from pydantic import BaseModel, Field


class FeedbackCreate(BaseModel):
    """Schema for creating feedback"""
    message: str = Field(..., min_length=5, max_length=2000, description="Feedback message")


class FeedbackResponse(BaseModel):
    """Schema for feedback response"""
    id: int
    message: str
    created_at: datetime

    class Config:
        from_attributes = True
