"""
Resume Export Adapter

Purpose:
Transform a validated final_resume into an export-ready structure.
"""

from engine.final_resume_schema_validator import validate_final_resume


def _metadata(source_metadata: dict | None = None) -> dict:
    """Return export adapter metadata."""
    return {
        "adapter": "resume_export_adapter",
        "version": "v1",
        "source": "final_resume",
        "source_metadata": source_metadata if isinstance(source_metadata, dict) else {},
    }


def _failed_payload(errors: list[str]) -> dict:
    """Return a failed export payload."""
    return {
        "status": "failed",
        "errors": errors,
        "document_title": "",
        "sections": [],
        "metadata": _metadata(),
    }


def _experience_text(bullet) -> str:
    """Return visible experience bullet text without source metadata."""
    if isinstance(bullet, dict):
        return bullet.get("text", "")
    if isinstance(bullet, str):
        return bullet
    return ""


def build_resume_export_payload(final_resume) -> dict:
    """Build an export-ready payload from a valid final_resume."""
    validation_result = validate_final_resume(final_resume)
    if not validation_result["is_valid"]:
        return _failed_payload(validation_result["errors"])

    skills = final_resume["skills"]
    sections = [
        {
            "id": "professional_summary",
            "title": "Professional Summary",
            "type": "paragraph",
            "content": final_resume["professional_summary"],
        },
        {
            "id": "skills",
            "title": "Skills",
            "type": "grouped_list",
            "content": {
                "Technical": skills["technical"],
                "Soft Skills": skills["soft"],
                "Tools": skills["tools"],
                "Domain": skills["domain"],
            },
        },
        {
            "id": "experience",
            "title": "Experience",
            "type": "bullet_list",
            "content": [
                _experience_text(bullet)
                for bullet in final_resume["experience_bullets"]
            ],
        },
    ]

    return {
        "status": "success",
        "errors": [],
        "document_title": final_resume["job_title"],
        "sections": sections,
        "metadata": _metadata(final_resume.get("metadata", {})),
    }
