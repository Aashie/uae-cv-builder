"""
Resume Output Assembler

Purpose:
Assemble already-generated resume components into a final structured resume.
"""


def _empty_final_resume() -> dict:
    """Return the default final resume schema."""
    return {
        "job_title": "",
        "professional_summary": "",
        "skills": {
            "key_skills": [],
            "matched_skills": [],
        },
        "experience_bullets": [],
        "metadata": {
            "assembled_by": "resume_output_assembler",
            "version": "v1",
            "summary_source": "empty",
            "bullet_source": "empty",
        },
    }


def _wrapper(status: str, errors: list[str], final_resume: dict) -> dict:
    """Return the assembler wrapper schema."""
    return {
        "status": status,
        "errors": errors,
        "final_resume": final_resume,
    }


def _status_from_errors(errors: list[str]) -> str:
    """Return success when no errors exist, otherwise partial."""
    return "partial" if errors else "success"


def _resolve_summary(
    resume_draft: dict,
    professional_summary_output: dict,
    errors: list[str],
) -> tuple[str, str]:
    """Resolve summary text and summary_source metadata."""
    if professional_summary_output is None:
        errors.append("Professional summary output is missing.")
    elif professional_summary_output.get("status") == "failed":
        errors.append("Professional summary output failed.")
    else:
        summary = professional_summary_output.get("summary", "")
        if summary:
            return summary, "ai_generated"
        errors.append("Professional summary missing; used resume draft fallback.")

    fallback_summary = resume_draft.get("professional_summary", "")
    if fallback_summary:
        return fallback_summary, "deterministic_fallback"

    errors.append("Professional summary missing from all sources.")
    return "", "empty"


def _resolve_experience_bullets(
    experience_bullet_output: dict,
    errors: list[str],
) -> tuple[list[dict], str]:
    """Resolve bullets and bullet_source metadata."""
    if experience_bullet_output is None:
        errors.append("Experience bullet output is missing.")
        return [], "empty"

    if experience_bullet_output.get("status") == "failed":
        errors.append("Experience bullet output failed.")
        return [], "empty"

    ai_output = experience_bullet_output.get("ai_output")
    if ai_output is None:
        errors.append("Experience bullet ai_output is missing.")
        return [], "empty"

    if "experience_bullets" not in ai_output:
        errors.append("Experience bullets missing; used empty list.")
        return [], "empty"

    bullets = ai_output["experience_bullets"]
    if not bullets:
        return [], "empty"

    if experience_bullet_output.get("mode") == "deterministic":
        return bullets, "deterministic_evidence"
    return bullets, "ai_generated"


def _resolve_skills(resume_draft: dict, errors: list[str]) -> dict:
    """Resolve key_skills and matched_skills from resume_draft only."""
    if "key_skills" in resume_draft:
        key_skills = resume_draft["key_skills"]
    else:
        key_skills = []
        errors.append("Resume draft key_skills missing; used empty list.")

    if "matched_skills" in resume_draft:
        matched_skills = resume_draft["matched_skills"]
    else:
        matched_skills = []
        errors.append("Resume draft matched_skills missing; used empty list.")

    return {
        "key_skills": key_skills,
        "matched_skills": matched_skills,
    }


def _resolve_job_title(resume_draft: dict, errors: list[str]) -> str:
    """Resolve job_title from resume_draft."""
    if "job_title" in resume_draft:
        return resume_draft["job_title"]

    errors.append("Resume draft job_title missing; used empty string.")
    return ""


def assemble_resume_output(
    resume_draft: dict,
    professional_summary_output: dict,
    experience_bullet_output: dict,
) -> dict:
    """Assemble already-generated resume components into a final resume output."""
    if resume_draft is None or resume_draft == {}:
        return _wrapper(
            "failed",
            ["Resume draft is missing or empty."],
            _empty_final_resume(),
        )

    errors: list[str] = []
    final_resume = _empty_final_resume()

    summary, summary_source = _resolve_summary(
        resume_draft,
        professional_summary_output,
        errors,
    )
    bullets, bullet_source = _resolve_experience_bullets(
        experience_bullet_output,
        errors,
    )

    final_resume["job_title"] = _resolve_job_title(resume_draft, errors)
    final_resume["professional_summary"] = summary
    final_resume["skills"] = _resolve_skills(resume_draft, errors)
    final_resume["experience_bullets"] = bullets
    final_resume["metadata"]["summary_source"] = summary_source
    final_resume["metadata"]["bullet_source"] = bullet_source

    return _wrapper(_status_from_errors(errors), errors, final_resume)
