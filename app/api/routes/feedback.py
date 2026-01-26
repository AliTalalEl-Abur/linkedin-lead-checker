import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import get_current_user
from app.models.feedback import Feedback
from app.models.user import User
from app.schemas.feedback import FeedbackCreate, FeedbackResponse

router = APIRouter(prefix="/feedback", tags=["feedback"])
logger = logging.getLogger(__name__)


@router.post("/", response_model=FeedbackResponse, summary="Submit user feedback")
def submit_feedback(
    request: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Submit feedback from logged-in users.
    Feedback is stored in the database for review.
    """
    try:
        feedback = Feedback(
            user_id=current_user.id,
            email=current_user.email,
            message=request.message,
            status="new"
        )
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        
        logger.info(f"New feedback received from user {current_user.email} (ID: {current_user.id})")
        
        return FeedbackResponse(
            id=feedback.id,
            message="Thank you for your feedback! We'll review it soon.",
            created_at=feedback.created_at
        )
    except Exception as e:
        logger.error(f"Error submitting feedback: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to submit feedback")


@router.post("/anonymous", response_model=FeedbackResponse, summary="Submit anonymous feedback")
def submit_anonymous_feedback(
    request: FeedbackCreate,
    db: Session = Depends(get_db)
):
    """
    Submit anonymous feedback without authentication.
    Useful for users who can't complete registration due to soft launch limits.
    """
    try:
        feedback = Feedback(
            user_id=None,
            email=None,
            message=request.message,
            status="new"
        )
        db.add(feedback)
        db.commit()
        db.refresh(feedback)
        
        logger.info("New anonymous feedback received")
        
        return FeedbackResponse(
            id=feedback.id,
            message="Thank you for your feedback! We'll review it soon.",
            created_at=feedback.created_at
        )
    except Exception as e:
        logger.error(f"Error submitting anonymous feedback: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to submit feedback")
