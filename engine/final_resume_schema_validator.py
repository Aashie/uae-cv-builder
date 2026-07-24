"""
Final Resume Schema Validator

Purpose:
Validate the assembled final resume structure without mutating or repairing it.
"""

import re


REQUIRED_TOP_LEVEL_KEYS = {
    "job_title",
    "professional_summary",
    "skills",
    "experience_bullets",
    "metadata",
}

REQUIRED_SKILL_KEYS = {
    "technical",
    "soft",
    "tools",
    "domain",
    "matched_skills",
    "strongest_skills",
}

GENERIC_MATCH_SCORE_SUMMARY_PATTERN = re.compile(
    r"^Professional with a \d+(\.\d+)?% match score for\s+opportunities\.?$"
)

GENERIC_MATCH_SCORE_SUMMARY_ERROR = (
    "Section 'professional_summary' contains a generic match-score placeholder "
    "or is missing target role context."
)


def _result(errors: list[str]) -> dict:
    """Return the validator result shape."""
    return {
        "is_valid": not errors,
        "errors": errors,
        "warnings": [],
    }


def _non_whitespace_length(value: str) -> int:
    """Return the number of non-whitespace characters in a string."""
    return len(re.sub(r"\s+", "", value))


def _has_visible_skill(skills: dict) -> bool:
    """Return whether any accepted skills list contains visible content."""
    for key in REQUIRED_SKILL_KEYS:
        for skill in skills.get(key, []):
            if isinstance(skill, str) and skill.strip():
                return True
    return False


def _has_visible_experience_bullet(experience_bullets: list) -> bool:
    """Return whether any bullet has visible text content."""
    for bullet in experience_bullets:
        if isinstance(bullet, str) and bullet.strip():
            return True
        if isinstance(bullet, dict):
            text = bullet.get("text", "")
            if isinstance(text, str) and text.strip():
                return True
    return False


def validate_final_resume(final_resume: dict) -> dict:
    """Validate the current final_resume schema produced by the assembler."""
    if not isinstance(final_resume, dict):
        return _result(["final_resume must be a dictionary."])

    errors: list[str] = []

    for key in REQUIRED_TOP_LEVEL_KEYS:
        if key not in final_resume:
            errors.append(f"Missing required section: {key}.")

    if "job_title" in final_resume and not isinstance(final_resume["job_title"], str):
        errors.append("Section 'job_title' must be a string.")

    if "professional_summary" in final_resume and not isinstance(
        final_resume["professional_summary"],
        str,
    ):
        errors.append("Section 'professional_summary' must be a string.")
    elif "professional_summary" in final_resume:
        professional_summary = final_resume["professional_summary"]
        if not professional_summary.strip():
            errors.append("Section 'professional_summary' must not be empty.")
        elif _non_whitespace_length(professional_summary) < 10:
            errors.append("Section 'professional_summary' is too weak.")
        elif GENERIC_MATCH_SCORE_SUMMARY_PATTERN.fullmatch(
            professional_summary.strip()
        ):
            errors.append(GENERIC_MATCH_SCORE_SUMMARY_ERROR)

    if "skills" in final_resume and not isinstance(final_resume["skills"], dict):
        errors.append("Section 'skills' must be a dictionary.")

    if "experience_bullets" in final_resume and not isinstance(
        final_resume["experience_bullets"],
        list,
    ):
        errors.append("Section 'experience_bullets' must be a list.")

    if "metadata" in final_resume and not isinstance(final_resume["metadata"], dict):
        errors.append("Section 'metadata' must be a dictionary.")

    skills = final_resume.get("skills")
    if isinstance(skills, dict):
        for key in REQUIRED_SKILL_KEYS:
            if key not in skills:
                errors.append(f"Missing skills category: {key}.")
            elif not isinstance(skills[key], list):
                errors.append(f"Skills category '{key}' must be a list.")
        if all(isinstance(skills.get(key), list) for key in REQUIRED_SKILL_KEYS):
            if not _has_visible_skill(skills):
                errors.append("Section 'skills' must contain at least one visible skill.")

    experience_bullets = final_resume.get("experience_bullets")
    if isinstance(experience_bullets, list):
        if not _has_visible_experience_bullet(experience_bullets):
            errors.append(
                "Section 'experience_bullets' must contain at least one visible bullet."
            )

    return _result(errors)
