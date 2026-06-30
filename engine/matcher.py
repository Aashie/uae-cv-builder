"""
Matcher

Purpose:
Compare extracted job requirements against the candidate's master profile to produce matched, missing, and recommended skill lists. Pure Python and local embeddings only, no API calls.
"""

from models.evidence import Evidence
from models.job_description import JobDescription


def _normalize_skill(skill: str) -> str:
    """Return a trimmed, case-insensitive representation of a skill."""
    return skill.strip().casefold()


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
        normalized_skill = _normalize_skill(skill)
        if normalized_skill and normalized_skill not in required_skills:
            required_skills[normalized_skill] = skill.strip()

    if not required_skills:
        return {
            "matched_skills": [],
            "missing_skills": [],
            "evidence_matches": {},
            "score": 0,
        }

    normalized_profile_skills = {
        _normalize_skill(skill)
        for skill in profile_skills
        if _normalize_skill(skill)
    }

    evidence_skill_matches: dict[str, list[str]] = {}
    for evidence in evidence_items:
        for skill in evidence.skills:
            normalized_skill = _normalize_skill(skill)
            if normalized_skill in required_skills:
                evidence_skill_matches.setdefault(normalized_skill, [])
                if evidence.id not in evidence_skill_matches[normalized_skill]:
                    evidence_skill_matches[normalized_skill].append(evidence.id)

    matched_skills: list[str] = []
    missing_skills: list[str] = []
    evidence_matches: dict[str, list[str]] = {}

    for normalized_skill, display_skill in required_skills.items():
        matched_by_profile = normalized_skill in normalized_profile_skills
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
