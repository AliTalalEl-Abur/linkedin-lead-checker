#!/usr/bin/env python3
"""Test the JSON-only OpenAI client.
- Uses run_fit and run_decision
- Skips live API call if OPENAI_API_KEY is not set
"""
import os
import sys

from app.schemas.ai_responses import ICPConfig
from app.services import run_fit, run_decision

print("=== Testing OpenAI JSON Client ===\n")

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

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    print("⚠️  Skipping live API test: OPENAI_API_KEY not set.")
    print("   Verifying mock mode outputs instead...\n")
    fit = run_fit(profile, icp)
    decision = run_decision(fit, profile)
    print("Mock FIT overall_score:", fit.overall_score)
    print("Mock DECISION should_contact:", decision.should_contact)
    print("\n✅ JSON client mock mode verified.")
    sys.exit(0)

print("Using OpenAI API (gpt-4o-mini) with JSON-only response...\n")
try:
    fit = run_fit(profile, icp, api_key=api_key, model="gpt-4o-mini")
    print("Live FIT:")
    print(" - overall_score:", fit.overall_score)
    print(" - confidence:", fit.confidence)
    assert 0 <= fit.overall_score <= 100
    assert 0 <= fit.confidence <= 100

    decision = run_decision(fit, profile, api_key=api_key, model="gpt-4o-mini")
    print("\nLive DECISION:")
    print(" - should_contact:", decision.should_contact)
    print(" - priority:", decision.priority)
    print(" - score:", decision.score)
    assert decision.priority in {"high", "medium", "low"}
    assert 0 <= decision.score <= 100

    print("\n✅ Live API JSON parsing and schema validation OK.")
    sys.exit(0)

except ValueError as e:
    # Raised when the model returns non-JSON or mismatched schema
    print("\n❌ Error: model did not return valid JSON:", e)
    sys.exit(1)
except Exception as e:
    print("\n❌ Unexpected error:", e)
    sys.exit(1)
