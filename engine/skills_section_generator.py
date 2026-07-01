"""
Skills Section Generator

Purpose:
Generate a deterministic resume skills section from approved input sources.
"""

import re

from utils.reference_loader import load_reference_data


NO_SKILLS_ERROR = "No skills found. Cannot generate skills section."
TECHNICAL_REFERENCE_ERROR = "Technical skills reference data could not be loaded."
SOFT_REFERENCE_ERROR = "Soft skills reference data could not be loaded."

ACRONYMS = {
    "ai",
    "aws",
    "crm",
    "css",
    "gis",
    "html",
    "ielts",
    "it",
    "json",
    "llm",
    "ms",
    "pdf",
    "sdlc",
    "seo",
    "sql",
    "uae",
    "ui",
    "uat",
    "ux",
    "wan",
    "lan",
}

TOOLS_KEYWORDS = {
    "excel",
    "microsoft excel",
    "word",
    "microsoft word",
    "powerpoint",
    "microsoft powerpoint",
    "outlook",
    "crm",
    "salesforce",
    "hubspot",
    "wordpress",
    "canva",
    "capcut",
    "google analytics",
    "meta ads",
    "jira",
    "trello",
    "asana",
    "notion",
    "slack",
    "selenium",
    "jupyter",
    "mysql",
    "linux",
    "ubuntu",
    "aws",
    "arcgis",
    "qgis",
    "autocad",
}


def _empty_skills_section() -> dict:
    """Return an empty skills section schema."""
    return {
        "technical": [],
        "soft": [],
        "tools": [],
        "domain": [],
        "matched_skills": [],
        "strongest_skills": [],
    }


def _wrapper(status: str, errors: list[str], skills_section: dict) -> dict:
    """Return the output wrapper schema."""
    return {
        "status": status,
        "errors": errors,
        "skills_section": skills_section,
    }


def _safe_dict(value: dict | None) -> dict:
    """Return a dict or an empty dict for missing inputs."""
    return value if isinstance(value, dict) else {}


def _safe_list(value: list | None) -> list:
    """Return a list or an empty list for missing and unsupported fields."""
    return value if isinstance(value, list) else []


def _normalize_key(skill: str) -> str:
    """Return a case-insensitive normalized key for matching and deduplication."""
    return re.sub(r"\s+", " ", skill.strip()).casefold()


def _format_word(word: str) -> str:
    """Return a readable word while preserving known acronyms."""
    normalized_word = word.casefold()
    if normalized_word in ACRONYMS:
        return normalized_word.upper()
    return normalized_word.capitalize()


def _format_skill(skill: str) -> str:
    """Normalize spacing and readable casing while preserving known acronyms."""
    normalized_skill = re.sub(r"\s+", " ", skill.strip())
    return " ".join(_format_word(word) for word in normalized_skill.split(" "))


def _dedupe_skills(skills: list) -> list[str]:
    """Deduplicate valid string skills case-insensitively."""
    deduped_skills: list[str] = []
    seen_keys: set[str] = set()

    for skill in skills:
        if not isinstance(skill, str):
            continue
        normalized_key = _normalize_key(skill)
        if not normalized_key or normalized_key in seen_keys:
            continue
        seen_keys.add(normalized_key)
        deduped_skills.append(_format_skill(skill))

    return deduped_skills


def _collect_all_skills(
    resume_draft: dict,
    matcher_output: dict,
    career_insights: dict,
) -> list[str]:
    """Collect skills from approved input fields only."""
    return _dedupe_skills(
        _safe_list(resume_draft.get("key_skills"))
        + _safe_list(resume_draft.get("matched_skills"))
        + _safe_list(matcher_output.get("matched_skills"))
        + _safe_list(career_insights.get("strongest_skills"))
    )


def _build_matched_skills(resume_draft: dict, matcher_output: dict) -> list[str]:
    """Build matched_skills metadata from approved matched skill sources."""
    return _dedupe_skills(
        _safe_list(resume_draft.get("matched_skills"))
        + _safe_list(matcher_output.get("matched_skills"))
    )


def _build_strongest_skills(career_insights: dict) -> list[str]:
    """Build strongest_skills metadata from career insights."""
    return _dedupe_skills(_safe_list(career_insights.get("strongest_skills")))


def _load_reference_set(filename: str, error_message: str, errors: list[str]) -> set[str]:
    """Load reference data as a normalized set, adding an error on failure."""
    try:
        reference_data = load_reference_data(filename)
    except Exception:
        errors.append(error_message)
        return set()

    if not isinstance(reference_data, list):
        errors.append(error_message)
        return set()

    return {
        _normalize_key(reference_skill)
        for reference_skill in reference_data
        if isinstance(reference_skill, str) and _normalize_key(reference_skill)
    }


def _categorize_skills(
    skills: list[str],
    technical_reference: set[str],
    soft_reference: set[str],
) -> dict:
    """Categorize skills into technical, soft, tools, and domain."""
    categorized_skills = {
        "technical": [],
        "soft": [],
        "tools": [],
        "domain": [],
    }

    for skill in skills:
        normalized_key = _normalize_key(skill)
        if normalized_key in technical_reference:
            categorized_skills["technical"].append(skill)
        elif normalized_key in soft_reference:
            categorized_skills["soft"].append(skill)
        elif normalized_key in TOOLS_KEYWORDS:
            categorized_skills["tools"].append(skill)
        else:
            categorized_skills["domain"].append(skill)

    return categorized_skills


def generate_skills_section(
    resume_draft: dict,
    matcher_output: dict,
    career_insights: dict,
) -> dict:
    """Generate a deterministic resume skills section from approved inputs."""
    resume_draft = _safe_dict(resume_draft)
    matcher_output = _safe_dict(matcher_output)
    career_insights = _safe_dict(career_insights)

    all_skills = _collect_all_skills(resume_draft, matcher_output, career_insights)
    if not all_skills:
        return _wrapper("failed", [NO_SKILLS_ERROR], _empty_skills_section())

    errors: list[str] = []
    technical_reference = _load_reference_set(
        "skills.json",
        TECHNICAL_REFERENCE_ERROR,
        errors,
    )
    soft_reference = _load_reference_set(
        "soft_skills.json",
        SOFT_REFERENCE_ERROR,
        errors,
    )

    categorized_skills = _categorize_skills(
        all_skills,
        technical_reference,
        soft_reference,
    )
    skills_section = {
        **categorized_skills,
        "matched_skills": _build_matched_skills(resume_draft, matcher_output),
        "strongest_skills": _build_strongest_skills(career_insights),
    }
    status = "partial" if errors else "success"

    return _wrapper(status, errors, skills_section)
