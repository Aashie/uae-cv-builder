"""
Professional Summary Generator

Purpose:
Generate a professional summary through a provider dispatcher while preserving
the AI Generation Contract.
"""

import time


SUMMARY_DISPLAY_OVERRIDES = {
    "excellent knowledge of ms office": "Microsoft Office",
}

ACRONYM_SEGMENTS = {
    "css": "CSS",
    "html": "HTML",
}


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


def _response(summary: str) -> dict:
    """Build a summary-only output matching the AI Generation Contract."""
    return {
        "summary": summary,
        "experience_bullets": [],
        "skills": _empty_skills(),
    }


def _safe_list(value) -> list:
    """Return a list for list-like summary inputs."""
    return value if isinstance(value, list) else []


def _clean_text(value) -> str:
    """Return normalized plain text for a summary fragment."""
    return " ".join(str(value or "").split())


def _format_slash_acronyms(text: str) -> str:
    """Preserve slash-delimited acronyms in supported skill labels."""
    if "/" not in text:
        return text
    return "/".join(
        ACRONYM_SEGMENTS.get(part.casefold(), part)
        for part in text.split("/")
    )


def _summary_display_label(value) -> str:
    """Return the safe display label for a supported summary input string."""
    text = _clean_text(value)
    override = SUMMARY_DISPLAY_OVERRIDES.get(text.casefold())
    if override:
        return override
    return _format_slash_acronyms(text)


def _unique_strings(values: list) -> list[str]:
    """Return unique non-empty strings while preserving order."""
    unique = []
    seen = set()
    for value in values:
        if not isinstance(value, str):
            continue
        text = _summary_display_label(value)
        key = text.casefold()
        if not text or key in seen:
            continue
        seen.add(key)
        unique.append(text)
    return unique


def _plain_join(items: list[str]) -> str:
    """Join plain-text items without synthetic labels or punctuation tricks."""
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return f"{', '.join(items[:-1])}, and {items[-1]}"


def _candidate_supported_skills(prompt_package: dict, resume_draft: dict) -> list[str]:
    """Return summary-safe candidate-supported skill strings."""
    return _unique_strings(
        _safe_list(resume_draft.get("key_skills"))
        + _safe_list(prompt_package.get("strongest_skills"))
    )


def _supported_matched_skills(prompt_package: dict, resume_draft: dict) -> list[str]:
    """Return summary-safe matched skill strings without using missing skills."""
    return _unique_strings(
        _safe_list(resume_draft.get("matched_skills"))
        + _safe_list(prompt_package.get("matched_skills"))
    )


def _deterministic_summary(prompt_package: dict, resume_draft: dict) -> str:
    """Build a deterministic candidate-safe summary from supported inputs."""
    prompt_package = prompt_package if isinstance(prompt_package, dict) else {}
    resume_draft = resume_draft if isinstance(resume_draft, dict) else {}

    target_job_title = _clean_text(prompt_package.get("job_title"))
    candidate_skills = _candidate_supported_skills(prompt_package, resume_draft)
    matched_skills = _supported_matched_skills(prompt_package, resume_draft)

    sentences = []
    if target_job_title and candidate_skills:
        sentences.append(
            f"Professional targeting {target_job_title} roles with reviewed skills in "
            f"{_plain_join(candidate_skills)}."
        )
    elif candidate_skills:
        sentences.append(
            f"Professional profile includes reviewed skills in {_plain_join(candidate_skills)}."
        )
    elif target_job_title and matched_skills:
        sentences.append(
            f"Professional targeting {target_job_title} roles with supported matched strengths in "
            f"{_plain_join(matched_skills)}."
        )
    elif matched_skills:
        sentences.append(
            f"Professional profile includes supported matched strengths in {_plain_join(matched_skills)}."
        )
    else:
        return (
            "Professional profile requires reviewed candidate evidence before "
            "a tailored summary can be generated."
        )

    if matched_skills:
        sentences.append(
            f"Supported matched strengths include {_plain_join(matched_skills)}."
        )

    return " ".join(sentences)


def _fallback_response(resume_draft: dict) -> dict:
    """Build deterministic fallback output from available draft evidence."""
    return _response(_deterministic_summary({}, resume_draft))


def _generate_with_gemini(prompt_package: dict, resume_draft: dict) -> dict:
    """Return deterministic V1 Gemini-style output without making API calls."""
    return _response(_deterministic_summary(prompt_package, resume_draft))


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
