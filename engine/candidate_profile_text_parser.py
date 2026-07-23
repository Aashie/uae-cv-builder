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
    "skills": {"skills", "technical skills", "tools", "core competencies", "key skills"},
    "experience": {
        "work experience",
        "professional experience",
        "employment history",
        "experience",
    },
    "education": {"education"},
    "certifications": {"certifications", "certifications & leadership"},
    "projects": {"projects"},
    "languages": {"languages"},
}

INLINE_SECTION_HEADINGS = [
    "CERTIFICATIONS & LEADERSHIP",
    "PROFESSIONAL EXPERIENCE",
    "PROFESSIONAL SUMMARY",
    "TECHNICAL SKILLS",
    "CORE COMPETENCIES",
    "WORK EXPERIENCE",
    "KEY SKILLS",
    "CERTIFICATIONS",
    "EXPERIENCE",
    "EDUCATION",
    "LANGUAGES",
    "SKILLS",
]

TITLE_WORDS = {
    "administrative",
    "operations",
    "executive",
    "manager",
    "assistant",
    "teacher",
    "engineer",
    "coordinator",
    "officer",
    "specialist",
    "consultant",
    "analyst",
    "developer",
    "representative",
    "supervisor",
    "director",
    "instructor",
    "associate",
    "administrator",
}

NON_NAME_STARTS = {"curriculum", "resume", "cv", "name", "profile", "summary"}

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

SKILL_BULLET_SEPARATORS = (
    "\u25b8",
    "\u2022",
    "\u25cf",
    "\u25aa",
    "\u25e6",
    "â–¸",
    "â€¢",
    "â—",
    "â–ª",
    "â—¦",
    "Ã¢â‚¬Â¢",
)
SKILL_BULLET_SEPARATOR_PATTERN = "|".join(
    re.escape(separator) for separator in SKILL_BULLET_SEPARATORS
)

EXPERIENCE_SKILL_TERMS = (
    ("Microsoft Office", re.compile(r"\bMicrosoft\s+Office\b", flags=re.IGNORECASE)),
    ("MS Office", re.compile(r"\bMS\s+Office\b", flags=re.IGNORECASE)),
    ("HTML/CSS", re.compile(r"\bHTML\s*/\s*CSS\b", flags=re.IGNORECASE)),
    ("Advanced Excel", re.compile(r"\bAdvanced\s+Excel\b", flags=re.IGNORECASE)),
    ("Meta Ads", re.compile(r"\bMeta\s+Ads\b", flags=re.IGNORECASE)),
    ("keyword research", re.compile(r"\bkeyword\s+research\b", flags=re.IGNORECASE)),
    (
        "social media scheduling",
        re.compile(r"\bsocial\s+media\s+scheduling\b", flags=re.IGNORECASE),
    ),
    ("HTML", re.compile(r"\bHTML\b", flags=re.IGNORECASE)),
    ("CSS", re.compile(r"\bCSS\b", flags=re.IGNORECASE)),
    ("Excel", re.compile(r"\bExcel\b", flags=re.IGNORECASE)),
)

SUBSUMED_EXPERIENCE_SKILLS = {
    "HTML/CSS": {"HTML", "CSS"},
    "Advanced Excel": {"Excel"},
    "Microsoft Excel": {"Excel"},
}


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


def _insert_section_breaks(text: str) -> str:
    """Add safe line breaks around uppercase section headings and bullets."""
    prepared = str(text).replace("\xa0", " ")
    headings = sorted(INLINE_SECTION_HEADINGS, key=len, reverse=True)
    heading_pattern = "|".join(re.escape(heading) for heading in headings)
    pattern = re.compile(rf"(?<![A-Za-z])({heading_pattern})(?![A-Za-z])")
    prepared = pattern.sub(r"\n\1\n", prepared)
    prepared = re.sub(r"\s+(?=(?:[-*•]|â€¢)\s+)", "\n", prepared)
    return prepared


def _strip_bullet_marker(line: str) -> str:
    """Remove common bullet/list prefixes."""
    return _normalize_item(re.sub(r"^\s*(?:[-*•]|â€¢|\d+[\.)])\s+", "", line))


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


def _extract_inline_uppercase_name(line: str) -> str:
    """Extract a conservative all-uppercase name from the start of a line."""
    tokens = re.findall(r"[A-Za-z]+", line)
    if len(tokens) < 2:
        return ""
    if tokens[0].lower() in NON_NAME_STARTS:
        return ""

    name_tokens: list[str] = []
    for token in tokens[:4]:
        if not token.isupper():
            break
        if token.lower() in TITLE_WORDS:
            break
        name_tokens.append(token)

    if not 2 <= len(name_tokens) <= 4:
        return ""
    return " ".join(token.title() for token in name_tokens)


def _extract_name(lines: list[str]) -> tuple[str, list[str]]:
    """Extract candidate name from the first meaningful non-heading line."""
    warnings: list[str] = []
    for raw_line in lines:
        line = _normalize_item(raw_line)
        if not line:
            continue
        inline_name = _extract_inline_uppercase_name(line)
        if inline_name:
            return inline_name, warnings
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
    """Split safely separated list items without rewriting candidate text."""
    separator_pattern = rf"(?:{SKILL_BULLET_SEPARATOR_PATTERN}|[,;|](?![^()]*\)))"
    pieces = re.split(separator_pattern, item)
    stripped_pieces = [
        re.sub(
            rf"^(?:{SKILL_BULLET_SEPARATOR_PATTERN}|[;|])+\s*|\s*(?:{SKILL_BULLET_SEPARATOR_PATTERN}|[;|])+$",
            "",
            piece,
        )
        for piece in pieces
    ]
    return [
        _normalize_item(piece)
        for piece in stripped_pieces
        if _normalize_item(piece)
    ]


def _extract_skills(sections: dict[str, list[str]]) -> list[str]:
    """Extract skills only from explicit skills/technical/tools sections."""
    skills: list[str] = []
    for item in sections["skills"]:
        skill_item = item.split(":", 1)[1] if ":" in item else item
        for skill in _split_list_item(skill_item):
            _append_unique(skills, skill)
    return skills


def _append_unique_case_insensitive(items: list[str], value: str) -> None:
    """Append value once case-insensitively, preserving first-seen spelling."""
    normalized_value = value.casefold()
    if value and normalized_value not in {item.casefold() for item in items}:
        items.append(value)


def _split_language_item(item: str) -> list[str]:
    """Split explicit language section items on safe separators only."""
    separator_pattern = rf"(?:{SKILL_BULLET_SEPARATOR_PATTERN}|[;|])"
    pieces = re.split(separator_pattern, item)
    stripped_pieces = [
        re.sub(
            rf"^(?:{SKILL_BULLET_SEPARATOR_PATTERN}|[;|])+\s*|\s*(?:{SKILL_BULLET_SEPARATOR_PATTERN}|[;|])+$",
            "",
            piece,
        )
        for piece in pieces
    ]
    return [
        _normalize_item(piece)
        for piece in stripped_pieces
        if _normalize_item(piece)
    ]


def _add_language_skills(skills: list[str], sections: dict[str, list[str]]) -> None:
    """Add exact explicit language section entries to skills."""
    for item in sections["languages"]:
        for language in _split_language_item(item):
            _append_unique_case_insensitive(skills, language)


def _looks_like_role_heading(item: str) -> bool:
    """Return whether an experience line looks like a source role heading."""
    if "|" in item:
        return True
    if re.search(r"\b(?:19|20)\d{2}\b", item) and re.search(r"\s[-–â€“]\s|,", item):
        return True
    if re.search(r"\b(?:present|current)\b", item, flags=re.IGNORECASE) and (
        "," in item or "|" in item or re.search(r"\s[-–â€“]\s", item)
    ):
        return True
    return False


def _is_negated_experience_skill_match(text: str, start: int, end: int) -> bool:
    """Return whether a skill match appears in a local negative context."""
    prefix = text[max(0, start - 60):start].casefold()
    suffix = text[end:min(len(text), end + 40)].casefold()

    if re.search(r"\b(?:no|without|lacks)\s+(?:\w+\s+){0,4}$", prefix):
        return True
    if re.search(r"\bnot\s+using\s+(?:\w+\s+){0,4}$", prefix):
        return True
    if re.match(r"^\s+(?:\w+\s+){0,4}(?:access|provided)\b", suffix):
        return True
    return False


def _extract_closed_list_experience_skills(text: str) -> list[str]:
    """Extract explicit closed-list skills from experience text."""
    extracted_skills: list[str] = []
    for skill, pattern in EXPERIENCE_SKILL_TERMS:
        for match in pattern.finditer(text):
            if _is_negated_experience_skill_match(text, match.start(), match.end()):
                continue
            if any(
                skill in SUBSUMED_EXPERIENCE_SKILLS.get(existing_skill, set())
                for existing_skill in extracted_skills
            ):
                continue
            _append_unique_case_insensitive(extracted_skills, skill)
            break
    return extracted_skills


def extract_experience_skills_from_text(
    text: str,
    known_skills: list[str] | None = None,
) -> list[str]:
    """Return known and closed-list skills explicitly present in experience text."""
    item = str(text)
    skills = list(known_skills) if isinstance(known_skills, list) else []
    entry_skills = [
        skill
        for skill in skills
        if isinstance(skill, str)
        if re.search(rf"\b{re.escape(skill)}\b", item, flags=re.IGNORECASE)
    ]
    for skill in _extract_closed_list_experience_skills(item):
        if any(
            skill in SUBSUMED_EXPERIENCE_SKILLS.get(existing_skill, set())
            for existing_skill in entry_skills
        ):
            continue
        _append_unique_case_insensitive(entry_skills, skill)
    return entry_skills


def _extract_experience(sections: dict[str, list[str]], skills: list[str]) -> list[dict]:
    """Build sample-compatible experience entries from explicit experience lines."""
    experience: list[dict] = []
    experience_items = sections["experience"]
    role_heading_count = sum(1 for item in experience_items if _looks_like_role_heading(item))

    if role_heading_count:
        role_blocks: list[str] = []
        current_block: list[str] = []
        for item in experience_items:
            if _looks_like_role_heading(item) and current_block:
                role_blocks.append(" ".join(current_block))
                current_block = [item]
            else:
                current_block.append(item)
        if current_block:
            role_blocks.append(" ".join(current_block))
        experience_items = role_blocks if len(role_blocks) == role_heading_count else [" ".join(experience_items)]

    for index, item in enumerate(experience_items, start=1):
        entry_skills = extract_experience_skills_from_text(item, skills)
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

    prepared_cv_text = _insert_section_breaks(cv_text)
    lines = prepared_cv_text.splitlines()
    name, name_warnings = _extract_name(lines)
    sections = _parse_sections(lines)
    skills = _extract_skills(sections)
    _add_language_skills(skills, sections)
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
