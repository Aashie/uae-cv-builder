"""
Candidate Profile Text Parser

Purpose:
Deterministically parse extracted CV text into a candidate-profile-compatible
payload without inferring missing candidate claims.
"""

import re


PARSER_METADATA = {
    "parser": "candidate_profile_text_parser",
    "version": "v1",
    "source": "extracted_cv_text",
}

PROFILE_KEYS = [
    "name",
    "skills",
    "experience",
    "projects",
    "certifications",
    "achievements",
]

SECTION_ALIASES = {
    "summary": {"summary", "profile", "professional summary"},
    "contact": {"contact"},
    "skills": {"skills", "technical skills", "tools"},
    "experience": {
        "work experience",
        "professional experience",
        "employment history",
        "experience",
    },
    "education": {"education"},
    "certifications": {"certifications"},
    "projects": {"projects"},
    "languages": {"languages"},
}

KNOWN_NAME_HEADINGS = {
    "resume",
    "cv",
    "curriculum vitae",
    "biodata",
    "summary",
    "profile",
    "professional summary",
    "contact",
    "skills",
    "technical skills",
    "tools",
    "experience",
    "work experience",
    "professional experience",
    "employment history",
    "education",
    "certifications",
    "projects",
    "languages",
}

EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_PATTERNS = [
    re.compile(r"(?<!\d)(?:\+971|00971)[\s-]?(?:5\d|[234679])(?:[\s-]?\d){7,8}(?!\d)"),
    re.compile(r"(?<!\d)05\d(?:[\s-]?\d){7}(?!\d)"),
]


def _empty_candidate_profile() -> dict:
    """Return the current candidate profile shape."""
    return {
        "name": "",
        "skills": [],
        "experience": [],
        "projects": [],
        "certifications": [],
        "achievements": [],
    }


def _result(
    status: str,
    candidate_profile: dict | None = None,
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
        "candidate_profile": candidate_profile or _empty_candidate_profile(),
        "errors": errors or [],
        "warnings": warnings or [],
        "metadata": result_metadata,
    }


def _normalize_item(text: str) -> str:
    """Normalize spacing without rewriting the candidate's content."""
    return " ".join(str(text).replace("\xa0", " ").split())


def _strip_bullet_marker(line: str) -> str:
    """Remove common bullet/list prefixes."""
    return _normalize_item(re.sub(r"^\s*(?:[-*•]|\d+[\.)])\s+", "", line))


def _canonical_heading(line: str) -> str | None:
    """Return a canonical section name for standalone heading-like lines."""
    stripped = _normalize_item(line).rstrip(":")
    if not stripped:
        return None
    if len(stripped.split()) > 3:
        return None

    lowered = stripped.lower()
    for canonical, aliases in SECTION_ALIASES.items():
        if lowered in aliases:
            return canonical
    return None


def _append_unique(items: list[str], value: str) -> None:
    """Append value once, preserving first-seen order."""
    if value and value not in items:
        items.append(value)


def _is_phone_like(line: str) -> bool:
    """Return whether a line looks like a UAE/international phone number."""
    return any(pattern.search(line) for pattern in PHONE_PATTERNS)


def _is_url_like(line: str) -> bool:
    """Return whether a line looks like a URL or LinkedIn reference."""
    lowered = line.lower()
    return "linkedin.com" in lowered or "http" in lowered or "www." in lowered


def _is_mostly_digits_or_date_like(line: str) -> bool:
    """Return whether a line is mostly numeric or date-like."""
    compact = re.sub(r"\s+", "", line)
    if not compact:
        return False
    digits = sum(character.isdigit() for character in compact)
    if digits / len(compact) >= 0.5:
        return True
    return bool(re.search(r"\b\d{4}\s*[-/]\s*\d{2,4}\b", line))


def _is_rejected_name_line(line: str) -> bool:
    """Return whether the first meaningful line is unsafe to use as a name."""
    lowered = line.lower().rstrip(":")
    return (
        lowered in KNOWN_NAME_HEADINGS
        or "@" in line
        or _is_phone_like(line)
        or _is_url_like(line)
        or _is_mostly_digits_or_date_like(line)
    )


def _extract_name(lines: list[str]) -> tuple[str, list[str]]:
    """Extract candidate name from the first meaningful non-heading line."""
    warnings: list[str] = []
    for raw_line in lines:
        line = _normalize_item(raw_line)
        if not line:
            continue
        if _is_rejected_name_line(line):
            warnings.append("Candidate name was not found in the first meaningful CV line.")
            return "", warnings
        return line, warnings
    warnings.append("Candidate name was not found in extracted CV text.")
    return "", warnings


def _parse_sections(lines: list[str]) -> dict[str, list[str]]:
    """Parse heading-led CV sections."""
    sections = {key: [] for key in SECTION_ALIASES}
    current_section = ""

    for raw_line in lines:
        line = _normalize_item(raw_line)
        if not line:
            continue

        heading = _canonical_heading(line)
        if heading:
            current_section = heading
            continue

        if current_section in sections:
            item = _strip_bullet_marker(line)
            _append_unique(sections[current_section], item)

    return sections


def _split_list_item(item: str) -> list[str]:
    """Split comma/semicolon separated list items."""
    pieces = re.split(r"[,;]", item)
    return [_normalize_item(piece) for piece in pieces if _normalize_item(piece)]


def _extract_skills(sections: dict[str, list[str]]) -> list[str]:
    """Extract skills only from explicit skills/technical/tools sections."""
    skills: list[str] = []
    for item in sections["skills"]:
        for skill in _split_list_item(item):
            _append_unique(skills, skill)
    return skills


def _extract_experience(sections: dict[str, list[str]], skills: list[str]) -> list[dict]:
    """Build sample-compatible experience entries from explicit experience lines."""
    experience: list[dict] = []
    for index, item in enumerate(sections["experience"], start=1):
        entry_skills = [
            skill
            for skill in skills
            if re.search(rf"\b{re.escape(skill)}\b", item, flags=re.IGNORECASE)
        ]
        experience.append(
            {
                "id": f"exp-{index}",
                "text": item,
                "skills": entry_skills,
            }
        )
    return experience


def _extract_projects(sections: dict[str, list[str]]) -> list[str]:
    """Extract projects from explicit project section lines."""
    projects: list[str] = []
    for item in sections["projects"]:
        _append_unique(projects, item)
    return projects


def _extract_certifications(sections: dict[str, list[str]]) -> list[str]:
    """Extract certifications from explicit certification section lines."""
    certifications: list[str] = []
    for item in sections["certifications"]:
        _append_unique(certifications, item)
    return certifications


def _extract_contact(cv_text: str) -> dict:
    """Extract conservative contact details from CV text."""
    email_match = EMAIL_PATTERN.search(cv_text)
    phone = ""
    for pattern in PHONE_PATTERNS:
        phone_match = pattern.search(cv_text)
        if phone_match:
            phone = phone_match.group(0)
            break
    return {
        "email": email_match.group(0) if email_match else "",
        "phone": phone,
    }


def _warnings_for_profile(sections: dict[str, list[str]], profile: dict) -> list[str]:
    """Build useful warnings for missing parsed sections."""
    warnings: list[str] = []
    if not profile["skills"]:
        warnings.append("Skills section was not found or contained no items.")
    if not profile["experience"]:
        warnings.append("Experience section was not found or contained no items.")
    if not sections["education"]:
        warnings.append("Education section was not found or contained no items.")
    if not profile["certifications"]:
        warnings.append("Certifications section was not found or contained no items.")
    return warnings


def parse_candidate_profile_text(cv_text) -> dict:
    """Parse extracted CV text into a structured candidate profile payload."""
    if not isinstance(cv_text, str):
        return _result("failed", errors=["cv_text must be a string."])

    if not cv_text.strip():
        return _result("failed", errors=["cv_text must be a non-empty string."])

    lines = cv_text.splitlines()
    name, name_warnings = _extract_name(lines)
    sections = _parse_sections(lines)
    skills = _extract_skills(sections)
    candidate_profile = {
        "name": name,
        "skills": skills,
        "experience": _extract_experience(sections, skills),
        "projects": _extract_projects(sections),
        "certifications": _extract_certifications(sections),
        "achievements": [],
    }
    ordered_profile = {key: candidate_profile[key] for key in PROFILE_KEYS}
    warnings = name_warnings + _warnings_for_profile(sections, ordered_profile)

    return _result(
        "success",
        candidate_profile=ordered_profile,
        warnings=warnings,
        metadata={
            "contact": _extract_contact(cv_text),
            "sections": {
                "summary": sections["summary"],
                "contact": sections["contact"],
                "education": sections["education"],
                "languages": sections["languages"],
            },
        },
    )
