from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", summary="Health check")
def healthcheck():
    """
    Independent health check that confirms the backend is running.
    
    Does NOT depend on:
    - Database connectivity
    - OpenAI API
    - Stripe API
    - Active subscribers
    
    Always returns 200 OK if the app is serving requests.
    """
    settings = get_settings()
    return {
        "ok": True,
        "env": settings.env,
        "soft_launch_mode": settings.soft_launch_mode,
        "daily_registration_limit": settings.daily_registration_limit if settings.soft_launch_mode else None
    }
