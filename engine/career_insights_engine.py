"""
Career Insights Engine

Purpose:
Analyze evidence items to identify the strongest demonstrated candidate skills.
"""

from collections import Counter


def _normalize_skill(skill: str) -> str:
    """Return a normalized title-case skill name for reporting."""
    return skill.strip().casefold().title()


def analyze_career_insights(evidence_items: list) -> dict:
    """Analyze evidence skills and return deterministic career insight metrics.

    Skills are counted case-insensitively and reported in title case. Evidence
    items without skills are included in the total evidence count but ignored
    for skill frequency.
    """
    skill_counts: Counter[str] = Counter()

    for evidence in evidence_items:
        for skill in getattr(evidence, "skills", []):
            normalized_skill = _normalize_skill(skill)
            if normalized_skill:
                skill_counts[normalized_skill] += 1

    strongest_skills = sorted(
        skill_counts,
        key=lambda skill: (-skill_counts[skill], skill),
    )

    return {
        "strongest_skills": strongest_skills,
        "skill_frequency": dict(skill_counts),
        "total_evidence_items": len(evidence_items),
        "total_unique_skills": len(skill_counts),
    }
