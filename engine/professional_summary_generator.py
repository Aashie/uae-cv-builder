"""
Professional Summary Generator

Purpose:
Generate a professional summary through a provider dispatcher while preserving
the AI Generation Contract.
"""

import time


class ProviderTimeoutError(Exception):
    """Raised when a provider request times out."""


class ProviderAuthenticationError(Exception):
    """Raised when a provider request fails authentication."""


class ProviderRateLimitError(Exception):
    """Raised when a provider request is rate limited."""


def _empty_skills() -> dict:
    """Return the empty skills contract for V1 summary-only generation."""
    return {
        "technical": [],
        "soft": [],
        "domain": [],
    }


def _fallback_response(resume_draft: dict) -> dict:
    """Build deterministic fallback output from resume draft summary."""
    return {
        "summary": resume_draft.get("professional_summary", ""),
        "experience_bullets": [],
        "skills": _empty_skills(),
    }


def _generate_with_gemini(prompt_package: dict, resume_draft: dict) -> dict:
    """Return deterministic V1 Gemini-style output without making API calls."""
    return _fallback_response(resume_draft)


def _retry_delay() -> None:
    """Wait before retrying provider generation."""
    time.sleep(2)


def _is_valid_ai_output(response: object) -> bool:
    """Return whether provider output satisfies the Sprint 16 V1 schema."""
    if not response or not isinstance(response, dict):
        return False

    if not isinstance(response.get("summary"), str) or not response["summary"].strip():
        return False

    if response.get("experience_bullets") != []:
        return False

    skills = response.get("skills")
    if not isinstance(skills, dict):
        return False

    return (
        skills.get("technical") == []
        and skills.get("soft") == []
        and skills.get("domain") == []
    )


def generate_professional_summary(
    prompt_package: dict,
    resume_draft: dict,
    provider: str = "gemini",
) -> dict:
    """Generate a professional summary through the selected provider."""
    if provider != "gemini":
        raise ValueError(f"Unsupported provider: {provider}")

    try:
        response = _generate_with_gemini(prompt_package, resume_draft)
    except (ProviderTimeoutError, ProviderAuthenticationError, ProviderRateLimitError):
        return _fallback_response(resume_draft)

    if _is_valid_ai_output(response):
        return response

    _retry_delay()

    try:
        response = _generate_with_gemini(prompt_package, resume_draft)
    except (ProviderTimeoutError, ProviderAuthenticationError, ProviderRateLimitError):
        return _fallback_response(resume_draft)

    if _is_valid_ai_output(response):
        return response

    return _fallback_response(resume_draft)
