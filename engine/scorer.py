"""
Scorer

Purpose:
Calculate ATS match score, missing skill count, and formatting pass/fail using pure Python logic, no AI.
"""


def calculate_match_score(matcher_output: dict, job_description) -> dict:
    """Calculate a transparent skill-only match score.

    V1 scoring uses only matched skills from matcher output and required skills
    from the job description. Education, certifications, and experience are not
    included in the score.
    """
    matched_skills = matcher_output.get("matched_skills", [])
    required_skills = getattr(job_description, "required_skills", [])

    matched_skill_count = len(matched_skills)
    required_skill_count = len(required_skills)

    if required_skill_count == 0:
        match_score = 0
    else:
        match_score = round((matched_skill_count / required_skill_count) * 100, 2)

    return {
        "match_score": match_score,
        "matched_skill_count": matched_skill_count,
        "required_skill_count": required_skill_count,
    }
