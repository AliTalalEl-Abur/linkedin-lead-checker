# LinkedIn Lead Checker — OpenAI JSON Client Demo

This repo includes a JSON-only OpenAI client for lead fit scoring and decision writing.

Functions:
- `run_fit(profile, icp)`: returns `FitScoringResult`
- `run_decision(qualification, profile=None)`: returns `DecisionResult`

Key behaviors:
- Uses cheap model `gpt-4o-mini` with low temperature
- Forces `response_format=json_object` to ensure JSON-only
- Parses JSON and fails if invalid (raises `ValueError`)
- Falls back to mock mode when `OPENAI_API_KEY` is not set

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

## Notes
- In mock mode (no API key), results are deterministic and suited for local tests.
- With an API key set, the client calls OpenAI and strictly validates JSON against Pydantic schemas.
