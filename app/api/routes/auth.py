from datetime import datetime, timedelta

import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.db import get_db
from app.core.security import create_access_token
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)


def _mask_email(email: str) -> str:
    if not email or "@" not in email:
        return "redacted"
    name, domain = email.split("@", 1)
    if not name:
        return f"***@{domain}"
    return f"{name[0]}***@{domain}"


@router.post("/login", response_model=TokenResponse, summary="User authentication")
def login(request: LoginRequest, http_request: Request, db: Session = Depends(get_db)):
    """
    Authenticate user and return access token.
    Creates new account if email doesn't exist (subject to registration limits).
    """
    request_id = getattr(getattr(http_request, "state", None), "request_id", "unknown")
    logger.info(
        "AUTH_LOGIN_ATTEMPT | request_id=%s | email=%s",
        request_id,
        _mask_email(request.email),
    )
    settings = get_settings()
    
    # Check if user exists
    user = db.query(User).filter(User.email == request.email).first()
    
    # If not, create new free user (with soft launch limits)
    if not user:
        # Soft Launch Mode: Check daily registration limit
        if settings.soft_launch_mode:
            # Count registrations in the last 24 hours
            yesterday = datetime.utcnow() - timedelta(days=1)
            registrations_today = db.query(func.count(User.id))\
                .filter(User.created_at >= yesterday)\
                .scalar()
            
            if registrations_today >= settings.daily_registration_limit:
                raise HTTPException(
                    status_code=429,
                    detail={
                        "message": "We're in Early Access! Daily registration limit reached. Please try again tomorrow.",
                        "limit_reached": True,
                        "early_access": True
                    }
                )
        
        user = User(email=request.email, plan="free")
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Create JWT token
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email}
    )

    logger.info(
        "AUTH_LOGIN_SUCCESS | request_id=%s | user_id=%s",
        request_id,
        user.id,
    )
    
    return TokenResponse(access_token=access_token)
