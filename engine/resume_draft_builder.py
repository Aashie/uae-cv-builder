"""
Resume Draft Builder

Purpose:
Convert a prompt package into a deterministic resume draft.
"""


def build_resume_draft(prompt_package: dict) -> dict:
    """Build a deterministic resume draft from a prompt package."""
    job_title = prompt_package.get("job_title", "")
    match_score = prompt_package.get("match_score", 0)

    return {
        "job_title": job_title,
        "professional_summary": (
            f"Professional with a {match_score}% match score for {job_title} opportunities."
        ),
        "key_skills": prompt_package.get("strongest_skills", []),
        "matched_skills": prompt_package.get("matched_skills", []),
        "resume_bullets": prompt_package.get("resume_recommendations", []),
    }
