from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import create_access_token
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse, summary="Magic login - creates user if doesn't exist")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Magic login endpoint:
    - If email doesn't exist, creates a new free user
    - Returns JWT token valid for 30 days
    """
    # Check if user exists
    user = db.query(User).filter(User.email == request.email).first()
    
    # If not, create new free user
    if not user:
        user = User(email=request.email, plan="free")
        db.add(user)
        db.commit()
        db.refresh(user)
    
    # Create JWT token
    access_token = create_access_token(
        data={"sub": user.id, "email": user.email}
    )
    
    return TokenResponse(access_token=access_token)
