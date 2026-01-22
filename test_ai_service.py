#!/usr/bin/env python3
"""Test the AI service with prompts."""
from app.schemas.ai_responses import ICPConfig
from app.services import get_ai_service

print("=== Testing AI Analysis Service ===\n")

# Mock LinkedIn profile data
profile_data = {
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

# ICP configuration
icp_config = ICPConfig(
    target_industries=["Technology", "SaaS"],
    target_seniority=["VP", "Director", "C-level"],
    company_size_min=100,
    company_size_max=2000,
    required_skills=["Team Leadership", "Cloud Architecture"],
    min_years_experience=8,
)

print("1. Profile Summary:")
print(f"   Name: {profile_data['name']}")
print(f"   Title: {profile_data['current_title']}")
print(f"   Company: {profile_data['company']} ({profile_data['company_size']} employees)")
print(f"   Experience: {profile_data['years_experience']} years\n")

print("2. Running AI Analysis...")
ai_service = get_ai_service()
result = ai_service.analyze_profile(profile_data, icp_config)

print(f"\n3. Analysis Results:")
print(f"   Should Contact: {result.should_contact}")
print(f"   Priority: {result.priority}")
print(f"   Score: {result.score}/100")
print(f"\n   Reasoning:")
print(f"   {result.reasoning}")
print(f"\n   Key Points:")
for i, point in enumerate(result.key_points, 1):
    print(f"   {i}. {point}")
print(f"\n   Suggested Approach:")
print(f"   {result.suggested_approach}")
print(f"\n   Next Steps:")
print(f"   {result.next_steps}")

if result.red_flags:
    print(f"\n   Red Flags:")
    for flag in result.red_flags:
        print(f"   ⚠️  {flag}")

print("\n✅ AI service working with prompt system!")
print("\nNote: Currently using mock responses. Integrate OpenAI API for real analysis.")
