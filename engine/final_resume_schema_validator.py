"""
Final Resume Schema Validator

Purpose:
Validate the assembled final resume structure without mutating or repairing it.
"""


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


def _result(errors: list[str]) -> dict:
    """Return the validator result shape."""
    return {
        "is_valid": not errors,
        "errors": errors,
        "warnings": [],
    }


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

    return _result(errors)
