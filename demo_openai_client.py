#!/usr/bin/env python3
"""Demo script for the JSON-only OpenAI client.
- Shows run_fit and run_decision usage
- Works in mock mode if OPENAI_API_KEY is not set
"""
import os
from app.services import run_fit, run_decision
from app.schemas.ai_responses import ICPConfig

profile = {
    "name": "Jane Smith",
    "headline": "VP of Engineering at TechCorp",
    "company": "TechCorp",
    "company_size": 750,
    "location": "San Francisco, CA",
    "current_title": "VP of Engineering",
    "years_experience": 12,
    "skills": ["Python", "Team Leadership", "Cloud Architecture", "DevOps"],
    "recent_activity": "Posted 3 times this week about scaling engineering teams",
}

icp = ICPConfig(
    target_industries=["Technology", "SaaS"],
    target_seniority=["VP", "Director", "C-level"],
    company_size_min=100,
    company_size_max=2000,
    required_skills=["Team Leadership", "Cloud Architecture"],
    min_years_experience=8,
)

api_key_present = bool(os.getenv("OPENAI_API_KEY"))
print("Using OpenAI API:", "Yes" if api_key_present else "No (mock mode)")

try:
    fit = run_fit(profile, icp)
    print("\nFIT Scoring:")
    print(" - overall_score:", fit.overall_score)
    print(" - confidence:", fit.confidence)
    print(" - positive_signals:", fit.positive_signals[:3])

    decision = run_decision(fit, profile)
    print("\nDecision:")
    print(" - should_contact:", decision.should_contact)
    print(" - priority:", decision.priority)
    print(" - score:", decision.score)
    print(" - reasoning:", decision.reasoning)

except ValueError as e:
    # Raised when the model returns non-JSON or JSON not matching schema
    print("\nError:", e)
