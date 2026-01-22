from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.dependencies import get_current_user
from app.core.usage import get_usage_stats
from app.models.user import User
from app.schemas.ai_responses import ICPConfig

router = APIRouter(prefix="/user", tags=["user"])


@router.get("", summary="Get current user profile")
def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Protected endpoint that returns the current authenticated user."""
    usage_stats = get_usage_stats(current_user, db)
    
    return {
        "id": current_user.id,
        "email": current_user.email,
        "plan": current_user.plan,
        "created_at": current_user.created_at,
        "usage": usage_stats,
        "icp_config": current_user.icp_config_json,
    }


@router.get("/me/usage", summary="Get current user usage statistics")
def get_my_usage(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get detailed usage statistics for the current user."""
    return get_usage_stats(current_user, db)


@router.put("/icp", summary="Update user's ICP configuration")
def update_user_icp(
    icp_config: ICPConfig,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update the user's Ideal Customer Profile configuration.
    This is used to personalize lead scoring.
    """
    current_user.icp_config_json = icp_config.model_dump()
    db.commit()
    db.refresh(current_user)
    
    return {
        "message": "ICP configuration saved successfully",
        "icp_config": current_user.icp_config_json,
    }
