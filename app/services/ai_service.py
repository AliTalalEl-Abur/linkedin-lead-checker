"""AI service for profile analysis using OpenAI."""
import json
import logging
import os
import time
from typing import Dict, Optional, Union

try:
    # Lazy import; only required when not using mock mode
    from openai import OpenAI, APIError, APIConnectionError, RateLimitError, APITimeoutError  # type: ignore
except Exception:
    OpenAI = None  # type: ignore
    APIError = Exception  # type: ignore
    APIConnectionError = Exception  # type: ignore
    RateLimitError = Exception  # type: ignore
    APITimeoutError = Exception  # type: ignore

from app.core.prompts import (
    get_decision_writer_prompt,
    get_fit_scorer_prompt,
    get_system_prompt,
)
from app.schemas.ai_responses import DecisionResult, FitScoringResult, ICPConfig
from app.core.config import get_settings

# Configure logging
logger = logging.getLogger(__name__)

# Hardening Configuration
OPENAI_TIMEOUT = 30  # seconds
MAX_RETRIES = 3
BASE_RETRY_DELAY = 1  # seconds
MAX_RETRY_DELAY = 10  # seconds


class AIAnalysisService:
    """Service for analyzing LinkedIn profiles using AI prompts."""
    
    def __init__(self, openai_api_key: Optional[str] = None):
        """
        Initialize the AI service.
        
        Args:
            openai_api_key: OpenAI API key (if None, will use mock responses)
        
        Note: Does NOT validate API key at initialization - validation happens
        only when analysis is attempted. This allows the backend to start even
        with invalid/missing keys.
        """
        settings = get_settings()
        
        # Check if OpenAI is globally enabled
        if not settings.openai_enabled:
            self.openai_api_key = None
            self.use_mock = True
            self._client = None
            logger.info("AIAnalysisService: OpenAI DISABLED (OPENAI_ENABLED=false)")
            return
        
        # Allow defaulting to environment variable if not explicitly provided
        self.openai_api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.use_mock = self.openai_api_key is None
        self._client = None
        
        if not self.use_mock and OpenAI is not None:
            try:
                self._client = OpenAI(
                    api_key=self.openai_api_key,
                    timeout=OPENAI_TIMEOUT,
                    max_retries=0,  # We handle retries ourselves for better control
                )
                logger.info("AIAnalysisService initialized with OpenAI client (timeout=%ds)", OPENAI_TIMEOUT)
            except Exception as e:
                # Don't crash on init - just log and use mock mode
                logger.warning("Failed to initialize OpenAI client: %s - using MOCK mode", str(e))
                self._client = None
                self.use_mock = True
        else:
            logger.warning("AIAnalysisService running in MOCK mode (no OpenAI API key)")
    
    def analyze_profile(
        self,
        profile_data: Dict,
        icp_config: Optional[ICPConfig] = None,
    ) -> DecisionResult:
        """
        Analyze a LinkedIn profile and return a decision.
        
        Args:
            profile_data: LinkedIn profile data as dict
            icp_config: Ideal Customer Profile configuration
        
        Returns:
            DecisionResult with recommendation and reasoning
            
        Raises:
            RuntimeError: If OpenAI API fails after retries
        """
        # CRITICAL: Final safety check - block if OpenAI disabled
        settings = get_settings()
        if not settings.openai_enabled:
            logger.error("AI_CALL_BLOCKED_OPENAI_DISABLED: analyze_profile called but OpenAI is disabled")
            raise RuntimeError("OpenAI API is disabled. Cannot perform AI analysis.")
        
        logger.info("Starting profile analysis (mock=%s)", self.use_mock)
        start_time = time.time()
        
        try:
            if self.use_mock:
                return self._mock_analysis(profile_data)
            
            # Step 1: Score the fit
            fit_result = self._score_fit(profile_data, icp_config)
            logger.info("Fit scoring completed: overall_score=%.1f", fit_result.overall_score)
            
            # Step 2: Generate decision
            decision = self._generate_decision(profile_data, fit_result)
            logger.info("Decision generated: should_contact=%s, priority=%s", 
                       decision.should_contact, decision.priority)
            
            elapsed = time.time() - start_time
            logger.info("Profile analysis completed in %.2fs", elapsed)
            return decision
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error("Profile analysis failed after %.2fs: %s", elapsed, str(e), exc_info=True)
            raise
    
    def _score_fit(
        self,
        profile_data: Dict,
        icp_config: Optional[ICPConfig],
    ) -> FitScoringResult:
        """
        Score how well the profile fits the ICP.
        
        Uses the fit_scorer prompt.
        """
        # If no API key, return deterministic mock scoring
        if self.use_mock or self._client is None:
            return FitScoringResult(
                overall_score=85.0,
                dimension_scores={
                    "seniority_match": 90.0,
                    "industry_match": 85.0,
                    "company_size_match": 80.0,
                    "skills_match": 88.0,
                    "experience_match": 85.0,
                    "engagement_level": 75.0,
                },
                positive_signals=[
                    "Senior leadership position at target company size",
                    "Active on LinkedIn with recent posts",
                    "Strong technical background in target domain",
                ],
                negative_signals=[
                    "Recent job change (3 months ago)",
                ],
                data_quality=90.0,
                confidence=85.0,
            )

        system_prompt = get_system_prompt()
        scorer_prompt = get_fit_scorer_prompt()

        user_payload = {
            "profile": profile_data,
            "icp": icp_config.dict() if icp_config else None,
        }

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"{scorer_prompt}\n\nINPUT JSON:\n{json.dumps(user_payload, ensure_ascii=False)}",
            },
        ]

        raw = _run_chat_json(self._client, messages)
        try:
            return FitScoringResult(**raw)
        except Exception as e:
            raise ValueError(f"Invalid JSON for FitScoringResult: {e}")
    
    def _generate_decision(
        self,
        profile_data: Dict,
        fit_result: FitScoringResult,
    ) -> DecisionResult:
        """
        Generate a decision based on fit scoring.
        
        Uses the decision_writer prompt.
        """
        # If no API key, return deterministic mock decision derived from scoring
        if self.use_mock or self._client is None:
            should_contact = fit_result.overall_score >= 60
            if fit_result.overall_score >= 80:
                priority = "high"
            elif fit_result.overall_score >= 60:
                priority = "medium"
            else:
                priority = "low"
            return DecisionResult(
                should_contact=should_contact,
                priority=priority,
                score=fit_result.overall_score,
                reasoning=(
                    f"Strong match with overall score of {fit_result.overall_score}. "
                    f"Profile shows {len(fit_result.positive_signals)} positive signals "
                    f"and {len(fit_result.negative_signals)} areas of concern."
                ),
                key_points=fit_result.positive_signals[:3],
                suggested_approach=(
                    "Lead with personalized message about their recent role change "
                    "and how your solution addresses challenges in their industry."
                ),
                red_flags=fit_result.negative_signals,
                next_steps="Send personalized LinkedIn message or email within 48 hours.",
            )

        system_prompt = get_system_prompt()
        decision_prompt = get_decision_writer_prompt()

        user_payload = {
            "qualification": fit_result.model_dump(),
            "profile": profile_data,
        }
        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": f"{decision_prompt}\n\nINPUT JSON:\n{json.dumps(user_payload, ensure_ascii=False)}",
            },
        ]

        raw = _run_chat_json(self._client, messages)
        try:
            return DecisionResult(**raw)
        except Exception as e:
            raise ValueError(f"Invalid JSON for DecisionResult: {e}")
    
    def _mock_analysis(self, profile_data: Dict) -> DecisionResult:
        """Mock analysis for testing without OpenAI API."""
        return DecisionResult(
            should_contact=True,
            priority="high",
            score=85.5,
            reasoning="Strong technical background with relevant experience in target industry. "
            "Active on LinkedIn with recent posts showing thought leadership.",
            key_points=[
                "Senior leadership at 500+ employee company",
                "10+ years in SaaS industry",
                "Active LinkedIn presence with weekly posts",
            ],
            suggested_approach="Lead with their recent post about scaling engineering teams. "
            "Position product as solution for their growth challenges.",
            red_flags=[],
            next_steps="Send personalized outreach within 24 hours while they're active.",
        )


# Singleton instance
_ai_service: Optional[AIAnalysisService] = None


def get_ai_service(openai_api_key: Optional[str] = None) -> AIAnalysisService:
    """Get or create the AI service instance."""
    global _ai_service
    if _ai_service is None:
        # Default to settings if no key provided
        settings = get_settings()
        key = openai_api_key or settings.openai_api_key
        _ai_service = AIAnalysisService(key)
    return _ai_service


# --- JSON-only OpenAI client helpers and exported functions ---

def _run_chat_json(client: Optional[object], messages: list, model: str = "gpt-4o-mini", temperature: float = 0.1) -> Dict:
    """
    Execute a chat completion that must return valid JSON.
    - Uses low temperature
    - Forces JSON-only via response_format
    - Implements retry logic with exponential backoff
    - Handles OpenAI errors gracefully
    - Raises if JSON can't be parsed
    
    Raises:
        RuntimeError: If client not initialized or all retries exhausted
        ValueError: If response is not valid JSON
    """
    if client is None:
        raise RuntimeError("OpenAI client not initialized. Provide OPENAI_API_KEY or pass a key.")

    last_error = None
    
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.debug("OpenAI API call attempt %d/%d (model=%s)", attempt, MAX_RETRIES, model)
            
            completion = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=max(0.0, min(temperature, 0.3)),
                response_format={"type": "json_object"},
            )
            
            content = completion.choices[0].message.content
            if not content:
                raise ValueError("OpenAI returned empty response")
            
            logger.debug("OpenAI response received (length=%d chars)", len(content))
            
            try:
                parsed = json.loads(content)
                logger.info("OpenAI JSON parsed successfully on attempt %d", attempt)
                return parsed
            except json.JSONDecodeError as e:
                logger.error("Invalid JSON from OpenAI: %s. Content: %s", str(e), content[:200])
                raise ValueError(f"Model did not return valid JSON: {e}")
        
        except APITimeoutError as e:
            last_error = e
            logger.warning("OpenAI timeout on attempt %d/%d: %s", attempt, MAX_RETRIES, str(e))
            if attempt < MAX_RETRIES:
                delay = min(BASE_RETRY_DELAY * (2 ** (attempt - 1)), MAX_RETRY_DELAY)
                logger.info("Retrying in %.1fs...", delay)
                time.sleep(delay)
            else:
                logger.error("All retry attempts exhausted after timeout")
                raise RuntimeError(f"OpenAI API timeout after {MAX_RETRIES} attempts: {str(e)}")
        
        except RateLimitError as e:
            last_error = e
            logger.warning("OpenAI rate limit on attempt %d/%d: %s", attempt, MAX_RETRIES, str(e))
            if attempt < MAX_RETRIES:
                # Rate limits need longer backoff
                delay = min(BASE_RETRY_DELAY * (2 ** attempt), MAX_RETRY_DELAY * 2)
                logger.info("Rate limited. Retrying in %.1fs...", delay)
                time.sleep(delay)
            else:
                logger.error("Rate limit persists after %d attempts", MAX_RETRIES)
                raise RuntimeError(f"OpenAI rate limit exceeded after {MAX_RETRIES} attempts: {str(e)}")
        
        except APIConnectionError as e:
            last_error = e
            logger.warning("OpenAI connection error on attempt %d/%d: %s", attempt, MAX_RETRIES, str(e))
            if attempt < MAX_RETRIES:
                delay = min(BASE_RETRY_DELAY * (2 ** (attempt - 1)), MAX_RETRY_DELAY)
                logger.info("Connection failed. Retrying in %.1fs...", delay)
                time.sleep(delay)
            else:
                logger.error("Connection failed after %d attempts", MAX_RETRIES)
                raise RuntimeError(f"OpenAI connection failed after {MAX_RETRIES} attempts: {str(e)}")
        
        except APIError as e:
            last_error = e
            # Check if it's a retryable error (5xx server errors)
            status_code = getattr(e, 'status_code', None)
            if status_code and 500 <= status_code < 600:
                logger.warning("OpenAI server error %d on attempt %d/%d: %s", 
                             status_code, attempt, MAX_RETRIES, str(e))
                if attempt < MAX_RETRIES:
                    delay = min(BASE_RETRY_DELAY * (2 ** (attempt - 1)), MAX_RETRY_DELAY)
                    logger.info("Server error. Retrying in %.1fs...", delay)
                    time.sleep(delay)
                else:
                    logger.error("Server error persists after %d attempts", MAX_RETRIES)
                    raise RuntimeError(f"OpenAI server error after {MAX_RETRIES} attempts: {str(e)}")
            else:
                # Non-retryable error (4xx client errors)
                logger.error("OpenAI client error (status=%s): %s", status_code, str(e))
                raise RuntimeError(f"OpenAI API error: {str(e)}")
        
        except Exception as e:
            # Unexpected error - don't retry
            logger.error("Unexpected error calling OpenAI: %s", str(e), exc_info=True)
            raise RuntimeError(f"Unexpected OpenAI error: {str(e)}")
    
    # Should never reach here, but just in case
    raise RuntimeError(f"OpenAI request failed after {MAX_RETRIES} attempts: {str(last_error)}")


def run_fit(profile: Dict, icp: Optional[Union[ICPConfig, Dict]] = None, *, api_key: Optional[str] = None, model: str = "gpt-4o-mini") -> FitScoringResult:
    """Run the fit scoring prompt and return parsed JSON as FitScoringResult.
    Fails if the model does not return valid JSON.
    """
    # CRITICAL: Final safety check - block if OpenAI disabled
    settings = get_settings()
    if not settings.openai_enabled:
        logger.error("AI_CALL_BLOCKED_OPENAI_DISABLED: run_fit called but OpenAI is disabled")
        raise RuntimeError("OpenAI API is disabled. Cannot perform AI analysis.")
    
    service = get_ai_service(api_key)
    # Ensure ICP config is the right type
    icp_config = icp if isinstance(icp, ICPConfig) else (ICPConfig(**icp) if isinstance(icp, dict) else None)
    if service.use_mock:
        # In mock mode, return deterministic data
        return service._score_fit(profile, icp_config)
    # Build messages and call
    system_prompt = get_system_prompt()
    scorer_prompt = get_fit_scorer_prompt()
    user_payload = {"profile": profile, "icp": icp_config.dict() if icp_config else None}
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"{scorer_prompt}\n\nINPUT JSON:\n{json.dumps(user_payload, ensure_ascii=False)}"},
    ]
    raw = _run_chat_json(service._client, messages, model=model)
    return FitScoringResult(**raw)


def run_decision(qualification: Union[FitScoringResult, Dict], profile: Optional[Dict] = None, *, api_key: Optional[str] = None, model: str = "gpt-4o-mini") -> DecisionResult:
    """Run the decision writer prompt and return parsed JSON as DecisionResult.
    Fails if the model does not return valid JSON.
    """
    # CRITICAL: Final safety check - block if OpenAI disabled
    settings = get_settings()
    if not settings.openai_enabled:
        logger.error("AI_CALL_BLOCKED_OPENAI_DISABLED: run_decision called but OpenAI is disabled")
        raise RuntimeError("OpenAI API is disabled. Cannot perform AI analysis.")
    
    service = get_ai_service(api_key)
    fit_result = qualification if isinstance(qualification, FitScoringResult) else FitScoringResult(**qualification)
    if service.use_mock:
        # In mock mode, derive decision locally
        return service._generate_decision(profile or {}, fit_result)
    system_prompt = get_system_prompt()
    decision_prompt = get_decision_writer_prompt()
    user_payload = {"qualification": fit_result.model_dump(), "profile": profile or {}}
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"{decision_prompt}\n\nINPUT JSON:\n{json.dumps(user_payload, ensure_ascii=False)}"},
    ]
    raw = _run_chat_json(service._client, messages, model=model)
    return DecisionResult(**raw)
