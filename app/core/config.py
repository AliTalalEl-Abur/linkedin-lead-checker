from functools import lru_cache
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic import AliasChoices
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    env: str = Field(default="dev")
    cors_allow_origins: List[str] | str = Field(
        default="http://localhost,http://localhost:3000,http://127.0.0.1:3000"
    )
    cors_allow_origin_regex: Optional[str] = Field(
        default=r"chrome-extension://.*"
    )
    database_url: str = Field(
        default="sqlite:///./linkedin_lead_checker.db"
    )

    # Stripe (unificado; acepta múltiples nombres de variables de entorno)
    stripe_api_key: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "STRIPE_API_KEY",
            "STRIPE_SECRET_KEY",
            "stripe_api_key",
            "stripe_secret_key",
        ),
    )
    stripe_price_pro_id: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "STRIPE_PRICE_PRO_ID",
            "STRIPE_PRO_PRICE_ID",
            "stripe_price_pro_id",
            "stripe_pro_price_id",
        ),
    )
    stripe_price_team_id: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "STRIPE_PRICE_TEAM_ID",
            "STRIPE_TEAM_PRICE_ID",
            "stripe_price_team_id",
            "stripe_team_price_id",
        ),
    )
    stripe_webhook_secret: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices(
            "STRIPE_WEBHOOK_SECRET",
            "stripe_webhook_secret",
        ),
    )

    # Usage Limits & Cost Control
    # FREE: 3 análisis TOTAL lifetime (no reset) - Cost: $0.09 máx
    # PRO: 100 análisis/semana - Cost: $12/mes máx @ $19/mes
    # TEAM: 300 análisis/semana - Cost: $36/mes máx @ $39/mes
    usage_limit_free: int = Field(default=3, description="FREE plan lifetime limit")
    usage_limit_pro: int = Field(default=100, description="PRO plan weekly limit")
    usage_limit_team: int = Field(default=300, description="TEAM plan weekly limit")
    revenue_per_pro_user: float = Field(default=12.0, description="Monthly AI budget contribution per active Pro user")
    revenue_per_team_user: float = Field(default=36.0, description="Monthly AI budget contribution per active Team user")
    ai_cost_per_analysis_usd: float = Field(default=0.03, description="Estimated AI cost per successful analysis in USD")
    
    # Rate Limiting: 1 análisis cada 30 segundos
    rate_limit_seconds: int = Field(default=30, description="Minimum seconds between analyses")
    
    # Kill Switches (seguridad económica)
    disable_free_plan: bool = Field(default=False, description="Emergency: disable all FREE analyses")
    disable_all_analyses: bool = Field(default=False, description="Emergency: disable ALL analyses globally")

    # Redirect URLs (pueden apuntar a extensión o webapp)
    stripe_success_url: str = Field(default="http://localhost:3000/billing/success")
    stripe_cancel_url: str = Field(default="http://localhost:3000/billing/cancel")

    jwt_secret_key: str = Field(
        default="dev-secret-key-change-in-production-at-least-32-chars-long"
    )
    jwt_algorithm: str = Field(default="HS256")
    jwt_expire_days: int = Field(default=30)

    # OpenAI
    openai_enabled: bool = Field(
        default=False,
        description="Enable OpenAI API calls (requires active subscribers and valid API key)"
    )
    openai_api_key: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("OPENAI_API_KEY", "openai_api_key"),
    )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("cors_allow_origins", mode="after")
    @classmethod
    def split_origins(cls, v: str) -> List[str]:
        """Convert comma-separated CORS origins to list."""
        return [item.strip() for item in v.split(",") if item.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
