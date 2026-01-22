import hashlib
import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.models.analysis_cache import AnalysisCache

logger = logging.getLogger(__name__)

CACHE_TTL = timedelta(hours=24)


def _extract_experience_titles(profile_data: dict) -> list[str]:
    titles: list[str] = []
    experience = (
        profile_data.get("experience")
        or profile_data.get("positions")
        or profile_data.get("experience_titles")
        or []
    )
    if isinstance(experience, list):
        for item in experience:
            if isinstance(item, str):
                titles.append(item)
            elif isinstance(item, dict):
                title = (
                    item.get("title")
                    or item.get("position")
                    or item.get("role")
                    or item.get("headline")
                )
                if title:
                    titles.append(str(title))
    return titles


def build_profile_hash(profile_data: dict) -> str:
    """Generate a deterministic profile hash using url, headline, and experience titles."""
    profile_url = (
        profile_data.get("profile_url")
        or profile_data.get("url")
        or profile_data.get("publicIdentifier")
        or profile_data.get("public_identifier")
        or ""
    )
    headline = profile_data.get("headline") or profile_data.get("title") or profile_data.get("bio") or ""
    titles = _extract_experience_titles(profile_data)
    normalized = "|".join(
        [str(profile_url).strip(), str(headline).strip(), "|".join([t.strip() for t in titles])]
    )
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def get_cached_analysis(db: Session, profile_hash: str, response_type: str) -> Optional[Dict[str, Any]]:
    """Return cached analysis payload if younger than CACHE_TTL."""
    cutoff = datetime.now(timezone.utc) - CACHE_TTL
    entry = (
        db.query(AnalysisCache)
        .filter(
            AnalysisCache.profile_hash == profile_hash,
            AnalysisCache.response_type == response_type,
            AnalysisCache.created_at >= cutoff,
        )
        .order_by(AnalysisCache.created_at.desc())
        .first()
    )
    if entry:
        logger.info("Cache hit for profile_hash=%s (type=%s)", profile_hash, response_type)
        return entry.dump_response()
    return None


def cache_analysis(
    db: Session,
    *,
    profile_hash: str,
    response_type: str,
    payload: Any,
    user_id: int | None,
) -> Dict[str, Any]:
    """Persist analysis response for reuse within CACHE_TTL."""
    if not isinstance(payload, dict):
        try:
            payload = payload.model_dump()
        except Exception:
            payload = json.loads(json.dumps(payload, default=str))

    entry = AnalysisCache(
        profile_hash=profile_hash,
        response_type=response_type,
        response_json=payload,
        user_id=user_id,
    )
    db.add(entry)
    db.commit()
    logger.info("Cached analysis for profile_hash=%s (type=%s)", profile_hash, response_type)
    return entry.dump_response()
