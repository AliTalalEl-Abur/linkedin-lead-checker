from typing import Literal, Optional

from pydantic import BaseModel, Field
from pydantic import ConfigDict
from app.schemas.ai_responses import DecisionResult, FitScoringResult


class AnalyzeProfileRequest(BaseModel):
    linkedin_profile_data: dict  # Raw profile data from extension


class AnalyzeProfileResponse(BaseModel):
    should_contact: bool
    score: float  # 0-100
    reasoning: str
    usage_remaining: int
    preview: bool = False
    message: Optional[str] = None


class AnalyzeLinkedInRequest(BaseModel):
    """Request payload for /analyze/linkedin endpoint."""
    profile_extract: dict


class AnalyzeLinkedInWithModeRequest(BaseModel):
    """Request payload for /analyze endpoint with explicit mode."""
    model_config = ConfigDict(populate_by_name=True)

    profile_url: str | None = Field(default=None, alias="profileUrl")
    profile_extract: dict | None = Field(default=None, alias="profileExtract")
    mode: Literal["preview", "ai"] = "ai"


class AnalyzeStableResponse(BaseModel):
    """Stable response payload for /analyze endpoint."""
    mode: Literal["preview", "ai"]
    score: float
    stars: int
    insights: list[str]
    decision: bool
    remaining: Optional[int] = None


class AnalyzeLinkedInUI(BaseModel):
    """UI-friendly subset of decision fields for frontend consumption."""
    should_contact: bool
    priority: Literal["high", "medium", "low"]
    score: float
    reasoning: str
    key_points: list[str]
    suggested_approach: str
    red_flags: list[str]
    next_steps: str


class AnalyzeLinkedInResponse(BaseModel):
    """Response payload for /analyze/linkedin endpoint."""
    qualification: FitScoringResult
    ui: AnalyzeLinkedInUI
    plan: Literal["free", "pro", "team"]
    preview: bool = False
    message: Optional[str] = None
    cache_hit: bool = False
