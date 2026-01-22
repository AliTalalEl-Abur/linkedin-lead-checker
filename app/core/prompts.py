"""Prompt management system for loading and caching prompts from files."""
from functools import lru_cache
from pathlib import Path
from typing import Dict

PROMPTS_DIR = Path(__file__).parent.parent / "prompts"


@lru_cache(maxsize=10)
def load_prompt(prompt_name: str) -> str:
    """
    Load a prompt from a file in the prompts directory.
    Results are cached for performance.
    
    Args:
        prompt_name: Name of the prompt file (without .txt extension)
    
    Returns:
        Content of the prompt file
    
    Raises:
        FileNotFoundError: If prompt file doesn't exist
    """
    prompt_path = PROMPTS_DIR / f"{prompt_name}.txt"
    
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    
    with open(prompt_path, "r", encoding="utf-8") as f:
        return f.read().strip()


def get_all_prompts() -> Dict[str, str]:
    """
    Load all available prompts into a dictionary.
    Useful for debugging or prompt management UI.
    
    Returns:
        Dictionary mapping prompt names to their content
    """
    prompts = {}
    
    if not PROMPTS_DIR.exists():
        return prompts
    
    for prompt_file in PROMPTS_DIR.glob("*.txt"):
        prompt_name = prompt_file.stem
        prompts[prompt_name] = load_prompt(prompt_name)
    
    return prompts


def get_system_prompt() -> str:
    """Get the system prompt with global rules."""
    return load_prompt("system")


def get_fit_scorer_prompt() -> str:
    """Get the prompt for evaluating lead fit."""
    return load_prompt("fit_scorer")


def get_decision_writer_prompt() -> str:
    """Get the prompt for converting analysis to decision."""
    return load_prompt("decision_writer")


def reload_prompts() -> None:
    """Clear the prompt cache to force reload from disk."""
    load_prompt.cache_clear()
