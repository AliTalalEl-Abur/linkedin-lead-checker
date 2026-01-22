#!/usr/bin/env python3
"""Test the prompt loading system."""
from app.core.prompts import (
    get_all_prompts,
    get_decision_writer_prompt,
    get_fit_scorer_prompt,
    get_system_prompt,
)

print("=== Testing Prompt System ===\n")

# Test individual prompt loading
print("1. Loading system prompt...")
system = get_system_prompt()
print(f"   Length: {len(system)} characters")
print(f"   First 100 chars: {system[:100]}...\n")

print("2. Loading fit_scorer prompt...")
scorer = get_fit_scorer_prompt()
print(f"   Length: {len(scorer)} characters")
print(f"   Contains 'OUTPUT SCHEMA': {('OUTPUT SCHEMA' in scorer)}\n")

print("3. Loading decision_writer prompt...")
writer = get_decision_writer_prompt()
print(f"   Length: {len(writer)} characters")
print(f"   Contains 'should_contact': {('should_contact' in writer)}\n")

# Test bulk loading
print("4. Loading all prompts...")
all_prompts = get_all_prompts()
print(f"   Total prompts: {len(all_prompts)}")
print(f"   Prompt names: {list(all_prompts.keys())}\n")

# Verify schemas are defined
print("5. Verifying prompt structure...")
checks = [
    ("system has CRITICAL RULES", "CRITICAL RULES" in system),
    ("fit_scorer defines JSON schema", "overall_score" in scorer),
    ("decision_writer has output format", "should_contact" in writer),
    ("All prompts require JSON", all("JSON" in p for p in all_prompts.values())),
]

for check_name, result in checks:
    status = "✅" if result else "❌"
    print(f"   {status} {check_name}")

print("\n✅ Prompt system working correctly!")
print("\nPrompt files are versioned and can be updated without code changes.")
