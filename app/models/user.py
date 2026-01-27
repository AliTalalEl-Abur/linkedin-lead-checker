from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    plan: Mapped[str] = mapped_column(String(20), nullable=False, default="free")
    
    # Stripe subscription details
    stripe_customer_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    stripe_subscription_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    subscription_status: Mapped[str | None] = mapped_column(String(50), nullable=True, default=None)  # active, canceled, past_due, etc.
    
    # ICP configuration
    icp_config_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    # Usage tracking
    # FREE: Lifetime counter (no reset)
    lifetime_analyses_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # PAID PLANS: Monthly counter (resets each billing period)
    monthly_analyses_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    monthly_analyses_reset_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Rate limiting: timestamp of last analysis
    last_analysis_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
