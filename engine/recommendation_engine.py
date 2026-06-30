"""
Recommendation Engine

Purpose:
Convert match results, score data, and skill gaps into deterministic recommendations.
"""


def _get_readiness_tier(match_score: float) -> str:
    """Return the readiness tier for a numeric match score."""
    if match_score >= 90:
        return "Ready to Apply"
    if match_score >= 70:
        return "Apply with Minor Gaps"
    if match_score >= 40:
        return "Targeted Upskilling Recommended"
    return "Significant Upskilling Required"


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
        f"Highlight {skill} experience."
        for skill in matched_skills
        if skill not in critical_gaps
    ]
    career_recommendations = [
        f"Develop {skill} skills."
        for skill in critical_gaps
        if skill not in matched_skills
    ]

    return {
        "readiness_tier": _get_readiness_tier(match_score),
        "resume_recommendations": resume_recommendations,
        "career_recommendations": career_recommendations,
    }
