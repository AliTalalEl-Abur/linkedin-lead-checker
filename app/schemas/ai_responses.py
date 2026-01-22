"""Schemas for AI responses - ensures type safety and validation."""
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class DimensionScores(BaseModel):
    """Individual dimension scores for lead fit."""
    seniority_match: float = Field(..., ge=0, le=100)
    industry_match: float = Field(..., ge=0, le=100)
    company_size_match: float = Field(..., ge=0, le=100)
    skills_match: float = Field(..., ge=0, le=100)
    experience_match: float = Field(..., ge=0, le=100)
    engagement_level: float = Field(..., ge=0, le=100)


class FitScoringResult(BaseModel):
    """Result from fit_scorer prompt."""
    overall_score: float = Field(..., ge=0, le=100)
    dimension_scores: DimensionScores
    positive_signals: List[str]
    negative_signals: List[str]
    data_quality: float = Field(..., ge=0, le=100)
    confidence: float = Field(..., ge=0, le=100)


class DecisionResult(BaseModel):
    """Result from decision_writer prompt."""
    should_contact: bool
    priority: Literal["high", "medium", "low"]
    score: float = Field(..., ge=0, le=100)
    reasoning: str
    key_points: List[str] = Field(..., max_items=3)
    suggested_approach: str
    red_flags: List[str] = Field(default_factory=list)
    next_steps: str


class ICPConfig(BaseModel):
    """Ideal Customer Profile configuration."""
    target_industries: Optional[List[str]] = None
    target_seniority: Optional[List[str]] = None  # e.g., ["C-level", "VP", "Director"]
    company_size_min: Optional[int] = None
    company_size_max: Optional[int] = None
    required_skills: Optional[List[str]] = None
    min_years_experience: Optional[int] = None
    target_locations: Optional[List[str]] = None
    exclude_keywords: Optional[List[str]] = None
