"""
Skill Gap Analyzer

Purpose:
Classify missing skills and application readiness from matcher output.
"""


def analyze_skill_gaps(matcher_output: dict) -> dict:
    """Analyze matcher output into V1 skill gaps and readiness.

    V1 treats every missing skill as a critical gap, does not produce minor
    gaps, and derives application readiness only from the matcher score.
    """
    missing_skills = matcher_output.get("missing_skills", [])
    score = matcher_output.get("score", 0)

    if score >= 80:
        application_readiness = "high"
    elif score >= 50:
        application_readiness = "medium"
    else:
        application_readiness = "low"

    return {
        "critical_gaps": missing_skills,
        "minor_gaps": [],
        "application_readiness": application_readiness,
    }
