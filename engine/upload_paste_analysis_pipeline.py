"""
Upload/Paste Analysis Pipeline

Purpose:
Connect extracted CV text and pasted JD text to the existing resume analysis
pipeline through deterministic parser stage gates.
"""

from engine.candidate_profile_text_parser import parse_candidate_profile_text
from engine.job_description_text_parser import parse_job_description_text
from engine.resume_analysis_orchestrator import run_resume_analysis
from models.job_description import JobDescription


HELPER_METADATA = {
    "helper": "upload_paste_analysis_pipeline",
    "version": "v1",
    "source": "cv_text_and_pasted_job_description",
}
PROFILE_KEYS = (
    "name",
    "skills",
    "experience",
    "projects",
    "certifications",
    "achievements",
)


def _result(
    status: str,
    candidate_parse_result: dict | None = None,
    job_parse_result: dict | None = None,
    analysis_result: dict | None = None,
    errors: list[str] | None = None,
    warnings: list[str] | None = None,
    completed_stages: list[str] | None = None,
    failed_stage: str = "",
    analysis_ran: bool = False,
    candidate_profile_source: str = "parsed",
) -> dict:
    """Return the upload/paste helper result shape."""
    metadata = HELPER_METADATA.copy()
    metadata.update(
        {
            "completed_stages": completed_stages or [],
            "failed_stage": failed_stage,
            "analysis_ran": analysis_ran,
            "candidate_profile_source": candidate_profile_source,
        }
    )
    return {
        "status": status,
        "candidate_parse_result": candidate_parse_result or {},
        "job_parse_result": job_parse_result or {},
        "analysis_result": analysis_result or {},
        "errors": errors or [],
        "warnings": warnings or [],
        "metadata": metadata,
    }


def _is_empty_reviewed_profile(profile: dict) -> bool:
    """Return whether a normalized reviewed profile has no usable content."""
    return not any(bool(profile.get(key)) for key in PROFILE_KEYS)


def _normalize_reviewed_candidate_profile(reviewed_candidate_profile) -> tuple[dict, list[str]]:
    """Normalize minimally valid reviewed profile data for analysis."""
    if not isinstance(reviewed_candidate_profile, dict):
        return {}, ["reviewed_candidate_profile must be a dictionary."]

    normalized_profile = {
        "name": reviewed_candidate_profile.get("name", "") or "",
        "skills": reviewed_candidate_profile.get("skills", []) or [],
        "experience": reviewed_candidate_profile.get("experience", []) or [],
        "projects": reviewed_candidate_profile.get("projects", []) or [],
        "certifications": reviewed_candidate_profile.get("certifications", []) or [],
        "achievements": reviewed_candidate_profile.get("achievements", []) or [],
    }
    if _is_empty_reviewed_profile(normalized_profile):
        return {}, ["reviewed_candidate_profile must contain reviewed candidate content."]
    return normalized_profile, []


def _reviewed_candidate_parse_result(candidate_profile: dict) -> dict:
    """Return parser-compatible wrapper for reviewed candidate profile input."""
    return {
        "status": "success",
        "candidate_profile": candidate_profile,
        "errors": [],
        "warnings": [],
        "metadata": {
            "source": "reviewed_candidate_profile",
            "reviewed": True,
        },
    }


def run_upload_paste_analysis(cv_text, job_text, reviewed_candidate_profile=None) -> dict:
    """Run parser-gated resume analysis from extracted CV and pasted JD text."""
    completed_stages: list[str] = []
    errors: list[str] = []
    warnings: list[str] = []

    candidate_profile_source = "parsed"
    if reviewed_candidate_profile is not None:
        normalized_profile, profile_errors = _normalize_reviewed_candidate_profile(
            reviewed_candidate_profile,
        )
        candidate_profile_source = "reviewed"
        if profile_errors:
            return _result(
                "failed",
                errors=profile_errors,
                warnings=warnings,
                failed_stage="reviewed_candidate_profile",
                candidate_profile_source=candidate_profile_source,
            )
        candidate_result = _reviewed_candidate_parse_result(normalized_profile)
        completed_stages.append("reviewed_candidate_profile")
    else:
        candidate_result = parse_candidate_profile_text(cv_text)
        warnings.extend(candidate_result.get("warnings", []))
        if candidate_result.get("status") != "success":
            errors.extend(candidate_result.get("errors", []))
            return _result(
                "failed",
                candidate_parse_result=candidate_result,
                errors=errors,
                warnings=warnings,
                failed_stage="candidate_profile_parse",
                candidate_profile_source=candidate_profile_source,
            )
        completed_stages.append("candidate_profile_parse")

    job_result = parse_job_description_text(job_text)
    warnings.extend(job_result.get("warnings", []))
    if job_result.get("status") != "success":
        errors.extend(job_result.get("errors", []))
        return _result(
            "failed",
            candidate_parse_result=candidate_result,
            job_parse_result=job_result,
            errors=errors,
            warnings=warnings,
            completed_stages=completed_stages,
            failed_stage="job_description_parse",
            candidate_profile_source=candidate_profile_source,
        )
    completed_stages.append("job_description_parse")

    try:
        job_description = JobDescription(**job_result["job_description"])
    except Exception as error:
        errors.append(f"JobDescription conversion failed: {error}")
        return _result(
            "failed",
            candidate_parse_result=candidate_result,
            job_parse_result=job_result,
            errors=errors,
            warnings=warnings,
            completed_stages=completed_stages,
            failed_stage="job_description_model_conversion",
            candidate_profile_source=candidate_profile_source,
        )
    completed_stages.append("job_description_model_conversion")

    try:
        analysis_result = run_resume_analysis(
            candidate_result["candidate_profile"],
            job_description,
        )
    except Exception as error:
        errors.append(f"Resume analysis failed: {error}")
        return _result(
            "failed",
            candidate_parse_result=candidate_result,
            job_parse_result=job_result,
            errors=errors,
            warnings=warnings,
            completed_stages=completed_stages,
            failed_stage="resume_analysis",
            candidate_profile_source=candidate_profile_source,
        )
    completed_stages.append("resume_analysis")

    return _result(
        "success",
        candidate_parse_result=candidate_result,
        job_parse_result=job_result,
        analysis_result=analysis_result,
        warnings=warnings,
        completed_stages=completed_stages,
        analysis_ran=True,
        candidate_profile_source=candidate_profile_source,
    )
