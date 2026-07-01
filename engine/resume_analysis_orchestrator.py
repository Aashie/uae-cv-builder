"""
Resume Analysis Orchestrator

Purpose:
Coordinate the completed resume analysis engines into a single output package.
"""

from engine.ai_response_validator import validate_ai_response
from engine.career_insights_engine import analyze_career_insights
from engine.evidence_extractor import extract_evidence
from engine.experience_bullet_generator import generate_experience_bullets
from engine.hallucination_checker import check_hallucinations
from engine.matcher import match_job_to_profile
from engine.professional_summary_generator import generate_professional_summary
from engine.prompt_builder import build_prompt_package
from engine.recommendation_engine import generate_recommendations
from engine.resume_output_assembler import assemble_resume_output
from engine.resume_draft_builder import build_resume_draft
from engine.scorer import calculate_match_score
from engine.skill_gap_analyzer import analyze_skill_gaps


def _default_skill_gaps() -> dict:
    """Return the default skill gap output."""
    return {
        "critical_gaps": [],
        "minor_gaps": [],
    }


def _default_recommendations() -> dict:
    """Return the default recommendation output."""
    return {
        "readiness_tier": "",
        "resume_recommendations": [],
        "career_recommendations": [],
    }


def _default_career_insights() -> dict:
    """Return the default career insights output."""
    return {
        "strongest_skills": [],
        "skill_frequency": {},
        "total_evidence_items": 0,
        "total_unique_skills": 0,
    }


def _default_ai_validation() -> dict:
    """Return the default AI validation output."""
    return {
        "is_valid": False,
        "errors": [],
    }


def _default_hallucination_check() -> dict:
    """Return the default hallucination check output."""
    return {
        "passed_bullets": [],
        "failed_bullets": [],
        "hallucination_count": 0,
    }


def _default_experience_bullet_validation() -> dict:
    """Return the default experience bullet validation output."""
    return {
        "is_valid": False,
        "errors": [],
    }


def _empty_ai_output() -> dict:
    """Return an empty AI Generation Contract output."""
    return {
        "summary": "",
        "experience_bullets": [],
        "skills": {
            "technical": [],
            "soft": [],
            "domain": [],
        },
    }


def _empty_experience_bullet_output() -> dict:
    """Return an empty deterministic experience bullet output wrapper."""
    return {
        "status": "success",
        "errors": [],
        "provider": "gemini",
        "mode": "deterministic",
        "ai_output": _empty_ai_output(),
    }


def _default_resume_output() -> dict:
    """Return the default resume output assembler wrapper."""
    return {
        "status": "",
        "errors": [],
        "final_resume": {},
    }


def _default_output() -> dict:
    """Return the full orchestrator output schema with default values."""
    return {
        "status": "",
        "errors": [],
        "match_score": 0,
        "matched_skills": [],
        "missing_skills": [],
        "skill_gaps": _default_skill_gaps(),
        "recommendations": {
            "resume_recommendations": [],
            "career_recommendations": [],
        },
        "readiness_tier": "",
        "career_insights": {},
        "resume_draft": {},
        "summary": "",
        "ai_validation": _default_ai_validation(),
        "experience_bullet_output": {},
        "experience_bullet_validation": _default_experience_bullet_validation(),
        "hallucination_check": _default_hallucination_check(),
        "resume_output": _default_resume_output(),
        "final_resume": {},
    }


def _extract_profile_skills(profile: dict) -> list[str]:
    """Flatten supported profile skill shapes into a single list."""
    skills = profile.get("skills", [])
    if isinstance(skills, list):
        return [skill for skill in skills if isinstance(skill, str)]
    if isinstance(skills, dict):
        flattened_skills: list[str] = []
        for skill_group in skills.values():
            if isinstance(skill_group, list):
                flattened_skills.extend(
                    skill for skill in skill_group if isinstance(skill, str)
                )
        return flattened_skills
    return []


def _is_empty_profile(profile: dict | None) -> bool:
    """Return whether a profile should hard-stop as missing or empty."""
    if not profile:
        return True

    has_skills = bool(_extract_profile_skills(profile))
    evidence_sections = (
        profile.get("experience"),
        profile.get("projects"),
        profile.get("certifications"),
        profile.get("achievements"),
    )
    has_evidence_source = any(bool(section) for section in evidence_sections)

    return not has_skills and not has_evidence_source


def _has_required_skills(job_description) -> bool:
    """Return whether a job description has non-empty required skills."""
    return bool(getattr(job_description, "required_skills", None))


def _ai_output_from_resume_draft(resume_draft: dict) -> dict:
    """Build a contract-shaped AI output from a deterministic resume draft."""
    return {
        "summary": resume_draft.get("professional_summary", ""),
        "experience_bullets": [],
        "skills": {
            "technical": [],
            "soft": [],
            "domain": [],
        },
    }


def _replace_experience_bullets(
    experience_bullet_output: dict,
    bullets: list[dict],
) -> dict:
    """Replace experience bullets in a wrapper with approved bullets only."""
    if not experience_bullet_output:
        experience_bullet_output = _empty_experience_bullet_output()
    experience_bullet_output.setdefault("ai_output", _empty_ai_output())
    experience_bullet_output["ai_output"]["experience_bullets"] = bullets
    return experience_bullet_output


def _set_status(output: dict) -> None:
    """Set final status from collected errors unless already failed."""
    if output["status"] == "failed":
        return
    output["status"] = "partial" if output["errors"] else "success"


def run_resume_analysis(profile: dict, job_description) -> dict:
    """Run the full resume analysis pipeline and return a unified output package."""
    output = _default_output()

    if _is_empty_profile(profile):
        output["status"] = "failed"
        output["errors"].append("Profile is missing or empty.")
        return output

    if job_description is None:
        output["status"] = "failed"
        output["errors"].append("Job description is missing.")
        return output

    if not _has_required_skills(job_description):
        output["status"] = "failed"
        output["errors"].append("Job description has no required skills.")
        return output

    try:
        evidence_items = extract_evidence(profile)
        profile_skills = _extract_profile_skills(profile)

        try:
            career_insights_output = analyze_career_insights(evidence_items)
        except Exception as error:
            career_insights_output = _default_career_insights()
            output["errors"].append(f"Career insights failed: {error}")

        matcher_output = match_job_to_profile(
            job_description,
            profile_skills,
            evidence_items,
        )
        score_output = calculate_match_score(matcher_output, job_description)
        skill_gap_output = analyze_skill_gaps(matcher_output)

        try:
            recommendation_output = generate_recommendations(
                matcher_output,
                skill_gap_output,
                score_output,
            )
        except Exception as error:
            recommendation_output = _default_recommendations()
            output["errors"].append(f"Recommendation engine failed: {error}")

        prompt_package = build_prompt_package(
            job_description,
            matcher_output,
            score_output,
            skill_gap_output,
            recommendation_output,
            career_insights_output,
        )
        resume_draft = build_resume_draft(prompt_package)

        try:
            ai_output = generate_professional_summary(prompt_package, resume_draft)
        except Exception as error:
            ai_output = _ai_output_from_resume_draft(resume_draft)
            output["errors"].append(f"Professional summary generation failed: {error}")

        ai_validation = validate_ai_response(ai_output)
        professional_summary_output_for_assembler = ai_output
        if not ai_validation["is_valid"]:
            output["errors"].append(
                f"Professional summary validation failed: {ai_validation['errors']}"
            )
            professional_summary_output_for_assembler = _empty_ai_output()

        try:
            experience_bullet_output = generate_experience_bullets(evidence_items)
        except Exception:
            experience_bullet_output = _empty_experience_bullet_output()
            output["errors"].append("Experience bullet generation failed.")

        if experience_bullet_output.get("status") == "failed":
            output["errors"].append("Experience bullet generation failed.")
            experience_bullet_output = _replace_experience_bullets(
                experience_bullet_output,
                [],
            )

        experience_bullet_validation = _default_experience_bullet_validation()
        hallucination_check = _default_hallucination_check()

        if experience_bullet_output.get("status") != "failed":
            experience_bullet_validation = validate_ai_response(
                experience_bullet_output.get("ai_output", _empty_ai_output()),
                context="experience_bullets",
            )

            if not experience_bullet_validation["is_valid"]:
                output["errors"].append(
                    "Experience bullet validation failed: "
                    f"{experience_bullet_validation['errors']}"
                )
                experience_bullet_output = _replace_experience_bullets(
                    experience_bullet_output,
                    [],
                )
            else:
                hallucination_check = check_hallucinations(
                    experience_bullet_output["ai_output"],
                    evidence_items,
                )
            if hallucination_check["hallucination_count"] > 0:
                output["errors"].append(
                    "Hallucination checker removed unsupported bullets."
                )
                experience_bullet_output = _replace_experience_bullets(
                    experience_bullet_output,
                    hallucination_check["passed_bullets"],
                )

        resume_output = assemble_resume_output(
            resume_draft,
            professional_summary_output_for_assembler,
            experience_bullet_output,
        )
        if resume_output.get("status") == "partial":
            output["errors"].append("Resume output assembly returned partial status.")
            output["errors"].extend(resume_output.get("errors", []))
        elif resume_output.get("status") == "failed":
            output["errors"].append("Resume output assembly failed.")

    except Exception as error:
        output = _default_output()
        output["status"] = "failed"
        output["errors"].append(f"Resume analysis failed: {error}")
        return output

    output["match_score"] = score_output.get("match_score", 0)
    output["matched_skills"] = matcher_output.get("matched_skills", [])
    output["missing_skills"] = matcher_output.get("missing_skills", [])
    output["skill_gaps"] = {
        "critical_gaps": skill_gap_output.get("critical_gaps", []),
        "minor_gaps": skill_gap_output.get("minor_gaps", []),
    }
    output["recommendations"] = {
        "resume_recommendations": recommendation_output.get(
            "resume_recommendations",
            [],
        ),
        "career_recommendations": recommendation_output.get(
            "career_recommendations",
            [],
        ),
    }
    output["readiness_tier"] = recommendation_output.get("readiness_tier", "")
    output["career_insights"] = career_insights_output
    output["resume_draft"] = resume_draft
    output["summary"] = ai_output.get("summary", "")
    output["ai_validation"] = ai_validation
    output["experience_bullet_output"] = experience_bullet_output
    output["experience_bullet_validation"] = experience_bullet_validation
    output["hallucination_check"] = hallucination_check
    output["resume_output"] = resume_output
    output["final_resume"] = resume_output.get("final_resume", {})
    _set_status(output)

    return output
