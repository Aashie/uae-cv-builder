"""
Recommendation Engine

Purpose:
Convert match results, score data, and skill gaps into deterministic recommendations.
"""

import re


MATCHED_RECOMMENDATION_TEMPLATE = (
    "Evidence-supported match: {skill}. Consider highlighting this only where it "
    "is supported by your CV."
)
MISSING_RECOMMENDATION_TEMPLATE = (
    "Requirement to address: {skill}. Add this to your resume only if it is true "
    "and supported by your experience; otherwise treat it as a learning or "
    "interview preparation target."
)

DISPLAY_NORMALIZATIONS = {
    "excellent knowledge of ms office": "Microsoft Office",
    "hands-on experience with crm software is a plus": "CRM software",
}

DISPLAY_PREFIXES = (
    "hands-on experience with",
    "experience with",
    "excellent knowledge of",
    "thorough understanding of",
    "knowledge of",
)


def _get_readiness_tier(match_score: float) -> str:
    """Return the readiness tier for a numeric match score."""
    if match_score >= 90:
        return "Ready to Apply"
    if match_score >= 70:
        return "Apply with Minor Gaps"
    if match_score >= 40:
        return "Targeted Upskilling Recommended"
    return "Significant Upskilling Required"


def _normalize_display_skill(skill: str) -> str:
    """Return a display-only skill phrase without changing matcher data."""
    display_skill = str(skill).strip()
    normalized_skill = display_skill.casefold()
    if normalized_skill in DISPLAY_NORMALIZATIONS:
        return DISPLAY_NORMALIZATIONS[normalized_skill]

    for prefix in DISPLAY_PREFIXES:
        display_skill = re.sub(
            rf"^{re.escape(prefix)}\s+",
            "",
            display_skill,
            flags=re.IGNORECASE,
        ).strip()

    display_skill = re.sub(
        r"\s+(is\s+a\s+plus|preferred|required)\.?$",
        "",
        display_skill,
        flags=re.IGNORECASE,
    ).strip()

    return display_skill


def generate_recommendations(
    matcher_output: dict,
    skill_gap_output: dict,
    score_output: dict,
) -> dict:
    """Generate deterministic resume and career recommendations.

    Resume recommendations are created only from matched skills. Career
    recommendations are created only from critical gaps.
    """
    match_score = score_output.get("match_score", 0)
    matched_skills = matcher_output.get("matched_skills", [])
    critical_gaps = skill_gap_output.get("critical_gaps", [])

    resume_recommendations = [
        MATCHED_RECOMMENDATION_TEMPLATE.format(skill=_normalize_display_skill(skill))
        for skill in matched_skills
        if skill not in critical_gaps
    ]
    career_recommendations = [
        MISSING_RECOMMENDATION_TEMPLATE.format(skill=_normalize_display_skill(skill))
        for skill in critical_gaps
        if skill not in matched_skills
    ]

    return {
        "readiness_tier": _get_readiness_tier(match_score),
        "resume_recommendations": resume_recommendations,
        "career_recommendations": career_recommendations,
    }
