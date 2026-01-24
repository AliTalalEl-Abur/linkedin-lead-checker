"""
Simple event tracking endpoint - privacy-respecting, no cookies.
Only tracks user intent signals (button clicks).
"""
import logging
from datetime import datetime
from typing import Literal

from fastapi import APIRouter, Request
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/events", tags=["events"])


class TrackEvent(BaseModel):
    """Event tracking payload"""
    event: Literal["install_extension_click", "waitlist_join"]
    page: str = "landing"
    referrer: str | None = None


@router.post("/track")
async def track_event(event_data: TrackEvent, request: Request):
    """
    Track user intent signals.
    No cookies, no persistent tracking, just server-side logs.
    """
    # Get minimal, non-invasive context
    client_ip = request.client.host if request.client else "unknown"
    user_agent = request.headers.get("user-agent", "unknown")
    
    # Log to server (you can later send this to a database or analytics service)
    logger.info(
        "EVENT_TRACK | %s | page=%s | ip=%s | ua=%s | referrer=%s",
        event_data.event,
        event_data.page,
        client_ip[:8] + "***",  # Partially mask IP for privacy
        user_agent[:50],  # Truncate user agent
        event_data.referrer or "direct"
    )
    
    return {
        "status": "tracked",
        "event": event_data.event,
        "timestamp": datetime.utcnow().isoformat()
    }
