import json
from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class AnalysisCache(Base):
    __tablename__ = "analysis_cache"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    profile_hash: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    response_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    response_json: Mapped[dict] = mapped_column(JSON, nullable=False)
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    def dump_response(self) -> dict:
        """Return a shallow copy of the cached payload."""
        # Ensure consistent serialization even if DB driver returns a string
        if isinstance(self.response_json, str):
            try:
                return json.loads(self.response_json)
            except Exception:
                return {}
        return dict(self.response_json)
