"""
Matcher

Purpose:
Compare extracted job requirements against the candidate's master profile to produce matched, missing, and recommended skill lists. Pure Python and local embeddings only, no API calls.
"""

from models.evidence import Evidence
from models.job_description import JobDescription


GENERIC_UNSAFE_CORES = {
    "communication",
    "management",
    "reporting",
    "leadership",
    "sales",
    "support",
    "operations",
}

JD_PREFIXES = (
    "excellent knowledge of ",
    "hands-on experience with ",
    "proficiency in ",
    "experience with ",
    "knowledge of ",
)

JD_SUFFIXES = (
    " is a plus",
)

REMOVABLE_TOKENS = {
    "software",
    "tools",
    "suite",
}

SAFE_CORE_ALIASES = {
    "crm": {"crm"},
    "ms office": {"microsoft office", "ms office"},
}

NEGATED_CORE_PHRASES = {
    "crm": (
        "no crm",
        "without crm",
        "not crm",
    ),
}


def _normalize_skill(skill: str) -> str:
    """Return a trimmed, case-insensitive representation of a skill."""
    return skill.strip().casefold()


def _normalize_core_text(skill: str) -> str:
    """Return alphanumeric normalized text for conservative core matching."""
    normalized = _normalize_skill(skill)
    for prefix in JD_PREFIXES:
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix):]
            break
    for suffix in JD_SUFFIXES:
        if normalized.endswith(suffix):
            normalized = normalized[: -len(suffix)]
            break
    normalized = normalized.replace("&", " and ")
    normalized = "".join(
        character if character.isalnum() or character.isspace() else " "
        for character in normalized
    )
    tokens = [
        token
        for token in normalized.split()
        if token not in REMOVABLE_TOKENS
    ]
    return " ".join(tokens)


def _skill_cores(skill: str) -> set[str]:
    """Return conservative match cores for a skill phrase."""
    normalized = _normalize_core_text(skill)
    cores = {normalized} if normalized else set()
    for alias, triggers in SAFE_CORE_ALIASES.items():
        if any(trigger in normalized.split() or trigger in normalized for trigger in triggers):
            cores.add(alias)
    return {core for core in cores if core and core not in GENERIC_UNSAFE_CORES}


def _is_negated_core(required_core: str, candidate_core: str) -> bool:
    """Return whether candidate text explicitly negates a safe core."""
    return any(
        phrase in candidate_core
        for phrase in NEGATED_CORE_PHRASES.get(required_core, ())
    )


def _is_supported_by_candidate_core(required_core: str, candidate_skill: str) -> bool:
    """Return whether candidate skill safely supports a JD core."""
    if not required_core:
        return False
    candidate_core = _normalize_core_text(candidate_skill)
    if not candidate_core:
        return False
    if _is_negated_core(required_core, candidate_core):
        return False
    if required_core == candidate_core:
        return True
    if required_core in GENERIC_UNSAFE_CORES:
        return False
    if required_core in SAFE_CORE_ALIASES and required_core in _skill_cores(candidate_skill):
        return True
    return f" {required_core} " in f" {candidate_core} "


def skill_is_supported_by_candidate(required_skill: str, candidate_skill: str) -> bool:
    """Return whether a candidate skill safely supports a required skill phrase."""
    return _is_supported_by_candidate_core(
        _normalize_core_text(required_skill),
        candidate_skill,
    )


def _matches_required_skill(required_core: str, candidate_skills: list[str]) -> bool:
    """Return whether any candidate skill safely matches the required core."""
    return any(
        _is_supported_by_candidate_core(required_core, skill)
        for skill in candidate_skills
    )


def match_job_to_profile(
    job_description: JobDescription,
    profile_skills: list[str],
    evidence_items: list[Evidence],
) -> dict:
    """Compare required job skills against profile skills and supporting evidence.

    Matching is case-insensitive. Duplicate required skills are evaluated once,
    preserving their first-seen display value in the returned matched and
    missing skill lists.
    """
    required_skills: dict[str, str] = {}
    for skill in job_description.required_skills:
        normalized_skill = _normalize_core_text(skill)
        if normalized_skill and normalized_skill not in required_skills:
            required_skills[normalized_skill] = skill.strip()

    if not required_skills:
        return {
            "matched_skills": [],
            "missing_skills": [],
            "evidence_matches": {},
            "score": 0,
        }

    profile_skill_values = [
        skill for skill in profile_skills if isinstance(skill, str) and _normalize_skill(skill)
    ]

    evidence_skill_matches: dict[str, list[str]] = {}
    for evidence in evidence_items:
        for skill in evidence.skills:
            if not isinstance(skill, str):
                continue
            for normalized_skill in required_skills:
                if _is_supported_by_candidate_core(normalized_skill, skill):
                    evidence_skill_matches.setdefault(normalized_skill, [])
                    if evidence.id not in evidence_skill_matches[normalized_skill]:
                        evidence_skill_matches[normalized_skill].append(evidence.id)

    matched_skills: list[str] = []
    missing_skills: list[str] = []
    evidence_matches: dict[str, list[str]] = {}

    for normalized_skill, display_skill in required_skills.items():
        matched_by_profile = _matches_required_skill(
            normalized_skill,
            profile_skill_values,
        )
        matched_by_evidence = normalized_skill in evidence_skill_matches

        if matched_by_profile or matched_by_evidence:
            matched_skills.append(display_skill)
            if matched_by_evidence:
                evidence_matches[display_skill] = evidence_skill_matches[normalized_skill]
        else:
            missing_skills.append(display_skill)

    score = len(matched_skills) / len(required_skills) * 100

    return {
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "evidence_matches": evidence_matches,
        "score": score,
    }
