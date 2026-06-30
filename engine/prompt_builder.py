"""
Prompt Builder

Purpose:
Aggregate intelligence-layer outputs into a structured prompt package.
"""


def build_prompt_package(
    job_description,
    matcher_output: dict,
    score_output: dict,
    skill_gap_output: dict,
    recommendation_output: dict,
    career_insights_output: dict,
) -> dict:
    """Build a structured prompt package from engine outputs."""
    return {
        "job_title": getattr(job_description, "job_title", ""),
        "match_score": score_output.get("match_score", 0),
        "strongest_skills": career_insights_output.get("strongest_skills", []),
        "matched_skills": matcher_output.get("matched_skills", []),
        "critical_gaps": skill_gap_output.get("critical_gaps", []),
        "resume_recommendations": recommendation_output.get("resume_recommendations", []),
        "career_recommendations": recommendation_output.get("career_recommendations", []),
    }
