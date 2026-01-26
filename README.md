# LinkedIn Lead Checker

AI-powered LinkedIn profile analysis tool to help you identify and qualify leads faster.

## Features
- AI-powered profile fit scoring
- Smart lead qualification
- Multiple subscription tiers (Free, Starter, Pro, Business)
- Chrome extension + Web dashboard
- **Commercial AI Activation**: OpenAI only activates when you have paying subscribers

## Commercial AI Activation 💰

This system ensures **you never pay OpenAI before having revenue**:
- ✅ AI activates ONLY with `OPENAI_ENABLED=true` + 1+ active subscribers
- ✅ Before first subscriber: Shows "AI launching soon"
- ✅ First activation: Clear log message 🚀
- ✅ Budget auto-calculated from subscriber revenue

📚 **Quick Guide:** [AI_ACTIVATION_QUICKSTART.md](AI_ACTIVATION_QUICKSTART.md)  
📖 **Full Docs:** [AI_COMMERCIAL_ACTIVATION.md](AI_COMMERCIAL_ACTIVATION.md)

## Key Components
- `run_fit(profile, icp)`: Returns `FitScoringResult`
- `run_decision(qualification, profile)`: Returns `DecisionResult`

## Tech Stack
- Backend: FastAPI + SQLite
- AI: OpenAI GPT-4o-mini with structured JSON responses
- Payments: Stripe subscriptions
- Frontend: Chrome Extension + Next.js web app

## Quick Start

1) Install dependencies

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2) Optional: set your OpenAI API key

```powershell
$env:OPENAI_API_KEY = "sk-your-key"
```

3) Run the demo script

```powershell
C:/Users/LENOVO/Desktop/linkedin-lead-checker/.venv/Scripts/python.exe demo_openai_client.py
```

You can also call the functions directly in your code:

```python
from app.services import run_fit, run_decision
from app.schemas.ai_responses import ICPConfig

profile = {"name": "Jane", "current_title": "VP of Engineering", "company": "TechCorp", "company_size": 750,
           "years_experience": 12, "skills": ["Python", "Team Leadership"], "recent_activity": "Posted 3 times"}

icp = ICPConfig(target_industries=["Technology"], target_seniority=["VP"], company_size_min=100, company_size_max=2000,
                required_skills=["Team Leadership"], min_years_experience=8)

fit = run_fit(profile, icp)
decision = run_decision(fit, profile)
print(fit.model_dump())
print(decision.model_dump())
```

## Privacy-Respecting Tracking

This project includes a minimal, privacy-first tracking system:
- ✅ Only tracks 2 events: Install Extension clicks & Waitlist joins
- ✅ No cookies, no Google Analytics, no persistent user IDs
- ✅ Fire-and-forget (doesn't block UI)
- ✅ IP partially masked, GDPR compliant

**Quick Start:**
```powershell
# Test tracking
./test_tracking.ps1

# Analyze events
python analyze_tracking.py
```

📚 **Full Documentation:** [TRACKING_INDEX.md](TRACKING_INDEX.md)

## Notes
- In mock mode (no API key), results are deterministic and suited for local tests.
- With an API key set, the client calls OpenAI and strictly validates JSON against Pydantic schemas.
