"""
Job Description Text Parser

Purpose:
Deterministically parse pasted job description text into a
JobDescription-compatible payload without inferring missing details.
"""

from dataclasses import fields
import re

from models.job_description import JobDescription


PARSER_METADATA = {
    "parser": "job_description_text_parser",
    "version": "v1",
    "source": "pasted_job_description",
}

SECTION_ALIASES = {
    "responsibilities": {
        "responsibilities",
        "duties",
        "key responsibilities",
        "job responsibilities",
        "responsibilities and duties",
    },
    "requirements": {
        "requirements",
        "qualifications",
        "requirements and skills",
        "requirements & skills",
        "requirements/skills",
        "requirements and qualifications",
        "skills and qualifications",
    },
    "skills": {"skills", "required skills"},
    "preferred_skills": {"preferred skills"},
    "experience": {"experience"},
    "education": {"education"},
}

SOFT_SKILL_TERMS = {
    "communication",
    "leadership",
    "teamwork",
    "collaboration",
    "organization",
    "organisational",
    "organizational",
    "problem solving",
    "attention to detail",
}


def _empty_job_description() -> dict:
    """Return the JobDescription-compatible empty payload."""
    return {
        "job_title": "",
        "required_skills": [],
        "soft_skills": [],
        "experience_level": "",
        "education": "",
        "certifications": [],
        "keywords": [],
    }


def _result(
    status: str,
    job_description: dict | None = None,
    errors: list[str] | None = None,
    warnings: list[str] | None = None,
    metadata: dict | None = None,
) -> dict:
    """Return the parser result shape."""
    result_metadata = PARSER_METADATA.copy()
    if metadata:
        result_metadata.update(metadata)
    return {
        "status": status,
        "job_description": job_description or _empty_job_description(),
        "errors": errors or [],
        "warnings": warnings or [],
        "metadata": result_metadata,
    }


def _normalize_item(text: str) -> str:
    """Normalize spacing in extracted JD text without rewriting content."""
    return " ".join(str(text).replace("\xa0", " ").split())


def _strip_bullet_marker(line: str) -> str:
    """Remove common bullet/list prefixes from a line."""
    return _normalize_item(re.sub(r"^\s*(?:[-*•]|\d+[\.)])\s+", "", line))


def _canonical_heading(line: str) -> str | None:
    """Return canonical heading when a line is standalone heading-like text."""
    stripped = _normalize_item(line).rstrip(":")
    if not stripped:
        return None
    lowered = stripped.lower()
    for canonical, aliases in SECTION_ALIASES.items():
        if lowered in aliases:
            return canonical
    if len(stripped.split()) > 3:
        return None
    return None


def _append_unique(items: list[str], value: str) -> None:
    """Append value once, preserving first-seen order."""
    if value and value not in items:
        items.append(value)


def _parse_sections(lines: list[str]) -> tuple[dict[str, list[str]], str]:
    """Parse heading-led sections and job title from text lines."""
    sections = {key: [] for key in SECTION_ALIASES}
    current_section = ""
    job_title = ""

    for raw_line in lines:
        line = _normalize_item(raw_line)
        if not line:
            continue

        if line.lower().startswith("job title:"):
            job_title = _normalize_item(line.split(":", 1)[1])
            if not job_title:
                current_section = "job_title"
            else:
                current_section = ""
            continue

        if line.lower().rstrip(":") == "job title":
            current_section = "job_title"
            continue

        heading = _canonical_heading(line)
        if heading:
            current_section = heading
            continue

        item = _strip_bullet_marker(line)
        if current_section == "job_title" and not job_title:
            job_title = item
            current_section = ""
        elif current_section in sections:
            _append_unique(sections[current_section], item)

    return sections, job_title


def _split_skill_item(item: str) -> list[str]:
    """Split comma/semicolon separated skills while preserving line items."""
    pieces = re.split(r"[,;]", item)
    return [_normalize_item(piece) for piece in pieces if _normalize_item(piece)]


def _is_education_requirement(item: str) -> bool:
    """Return whether item is clearly an education requirement."""
    lowered = item.lower()
    education_patterns = [
        r"\bhigh school (?:degree|diploma)\b",
        r"\bbachelor'?s degree\b",
        r"\bbachelor degree\b",
        r"\bdiploma\b",
        r"\bdegree in\b",
        r"\bbsc in\b",
        r"\bba in\b",
        r"\bmaster'?s degree\b",
    ]
    ambiguous_skill_terms = ("skill", "skills", "technical skill", "technical skills")
    if any(term in lowered for term in ambiguous_skill_terms):
        return False
    return any(re.search(pattern, lowered) for pattern in education_patterns)


def _is_experience_requirement(item: str) -> bool:
    """Return whether item is clearly a work-experience requirement."""
    lowered = item.lower()
    experience_patterns = [
        r"\bproven experience as\b",
        r"\bwork experience as\b",
        r"\b\d+\+?\s+years? of experience\b",
        r"\bminimum\s+\d+\s+years?\s+experience\b",
        r"\bminimum\s+\d+\s+year\s+experience\b",
        r"\bprevious experience in\b",
    ]
    return any(re.search(pattern, lowered) for pattern in experience_patterns)


def _is_certification_requirement(item: str) -> bool:
    """Return whether item is clearly a certification requirement."""
    lowered = item.lower()
    return (
        "certification" in lowered
        or "certified" in lowered
        or re.search(r"\b(?:cpa|cma)\b", lowered) is not None
    )


def _requirement_classification(item: str) -> str:
    """Classify obvious non-skill requirements while preserving uncertain items."""
    if _is_education_requirement(item):
        return "education"
    if _is_experience_requirement(item):
        return "experience"
    if _is_certification_requirement(item):
        return "certification"
    return "skill"


def _append_requirement_skill_phrases(skills: list[str], item: str) -> None:
    """Append visible requirement skill phrases without inventing content."""
    if _requirement_classification(item) != "skill":
        return
    for skill in _split_skill_item(item):
        _append_unique(skills, skill)

    patterns = [
        r"\bGAAP\b",
        r"\bFreshBooks\b",
        r"\bQuickBooks\b",
        r"\bAdvanced MS Excel\b",
        r"\bVlookups\b",
        r"\bpivot tables\b",
        r"\bgeneral ledger functions\b",
        r"\battention to detail\b",
        r"\banalytical skills\b",
        r"\bAccounting\b",
        r"\bFinance\b",
        r"\bCPA\b",
        r"\bCMA\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, item, flags=re.IGNORECASE)
        if match:
            _append_unique(skills, match.group(0))


def _extract_required_skills(sections: dict[str, list[str]]) -> list[str]:
    """Extract skills explicitly listed in required/skills sections."""
    skills: list[str] = []
    source_items = sections["skills"] if sections["skills"] else sections["requirements"]
    for item in source_items:
        _append_requirement_skill_phrases(skills, item)
    return skills


def _extract_soft_skills(required_skills: list[str]) -> list[str]:
    """Return explicitly listed skills that are known soft skills."""
    soft_skills: list[str] = []
    for skill in required_skills:
        if skill.lower() in SOFT_SKILL_TERMS:
            _append_unique(soft_skills, skill)
    return soft_skills


def _extract_certifications(requirements: list[str]) -> list[str]:
    """Extract certification lines only when certification wording is present."""
    certifications: list[str] = []
    for item in requirements:
        if _requirement_classification(item) == "certification":
            _append_unique(certifications, item)
    return certifications


def _extract_requirement_field(requirements: list[str], classification: str) -> str:
    """Extract classified requirement lines into a single schema field."""
    items: list[str] = []
    for item in requirements:
        if _requirement_classification(item) == classification:
            _append_unique(items, item)
    return " ".join(items)


def _warnings_for_sections(sections: dict[str, list[str]], job_description: dict) -> list[str]:
    """Build useful warnings for missing parsed sections."""
    warnings: list[str] = []
    if not job_description["job_title"]:
        warnings.append("Job title was not found in pasted job description.")
    if not sections["responsibilities"]:
        warnings.append("Responsibilities section was not found.")
    if not job_description["required_skills"]:
        warnings.append("Required skills section was not found or contained no items.")
    if not sections["requirements"]:
        warnings.append("Requirements or qualifications section was not found.")
    if not job_description["experience_level"]:
        warnings.append("Experience section was not found.")
    if not job_description["education"]:
        warnings.append("Education section was not found.")
    return warnings


def parse_job_description_text(job_text) -> dict:
    """Parse a pasted job description string into a structured payload."""
    if not isinstance(job_text, str):
        return _result("failed", errors=["job_text must be a string."])

    if not job_text.strip():
        return _result("failed", errors=["job_text must be a non-empty string."])

    lines = job_text.splitlines()
    sections, job_title = _parse_sections(lines)
    required_skills = _extract_required_skills(sections)
    requirements = sections["requirements"]
    experience_level = " ".join(sections["experience"])
    education = " ".join(sections["education"])
    requirement_experience = _extract_requirement_field(requirements, "experience")
    requirement_education = _extract_requirement_field(requirements, "education")
    if requirement_experience:
        experience_level = " ".join(
            item for item in [experience_level, requirement_experience] if item
        )
    if requirement_education:
        education = " ".join(item for item in [education, requirement_education] if item)

    job_description = {
        "job_title": job_title,
        "required_skills": required_skills,
        "soft_skills": _extract_soft_skills(required_skills),
        "experience_level": experience_level,
        "education": education,
        "certifications": _extract_certifications(requirements),
        "keywords": requirements.copy(),
    }

    model_keys = [field.name for field in fields(JobDescription)]
    ordered_job_description = {key: job_description[key] for key in model_keys}
    warnings = _warnings_for_sections(sections, ordered_job_description)

    return _result(
        "success",
        job_description=ordered_job_description,
        warnings=warnings,
        metadata={
            "sections": {
                "responsibilities": sections["responsibilities"],
                "requirements": requirements,
                "preferred_skills": sections["preferred_skills"],
            }
        },
    )
