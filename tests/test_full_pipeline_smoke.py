"""
Full Pipeline Smoke Test

Purpose:
Exercise the real resume analysis orchestrator with realistic UAE-style data.
"""

from engine.resume_analysis_orchestrator import run_resume_analysis
from models.job_description import JobDescription


def test_full_pipeline_smoke_administrative_assistant() -> None:
    """Run the full deterministic pipeline without monkeypatching."""
    candidate_profile = {
        "skills": [
            "Documentation",
            "Microsoft Excel",
            "Communication",
            "Scheduling",
            "Reporting",
            "Leadership",
        ],
        "experience": [
            {
                "id": "exp-1",
                "text": (
                    "Prepared office documentation, maintained Microsoft Excel "
                    "reporting trackers, coordinated scheduling, supported "
                    "communication with internal teams, and provided leadership "
                    "for daily administrative follow-ups."
                ),
                "skills": [
                    "Documentation",
                    "Microsoft Excel",
                    "Communication",
                    "Scheduling",
                    "Reporting",
                    "Leadership",
                ],
            }
        ],
        "projects": [],
        "certifications": [],
        "achievements": [],
    }
    job_description = JobDescription(
        job_title="Administrative Assistant",
        required_skills=[
            "Documentation",
            "Microsoft Excel",
            "Communication",
            "Scheduling",
            "Reporting",
            "Leadership",
            "Records Management",
            "Office Coordination",
        ],
        soft_skills=["Communication", "Leadership"],
        experience_level="Mid",
        education="Bachelor's",
    )

    result = run_resume_analysis(candidate_profile, job_description)

    assert result["status"] in {"success", "partial"}
    assert isinstance(result["errors"], list)
    assert result["failed_stage"] == ""
    assert isinstance(result["completed_stages"], list)

    expected_top_level_fields = {
        "match_score",
        "matched_skills",
        "missing_skills",
        "skill_gaps",
        "recommendations",
        "career_insights",
        "resume_draft",
        "skills_section_output",
        "resume_output",
        "final_resume",
    }
    assert expected_top_level_fields.issubset(result)

    assert isinstance(result["match_score"], (int, float))
    assert isinstance(result["matched_skills"], list)
    assert isinstance(result["missing_skills"], list)
    assert isinstance(result["skill_gaps"], dict)
    assert isinstance(result["recommendations"], dict)
    assert isinstance(result["career_insights"], dict)
    assert isinstance(result["resume_draft"], dict)
    assert isinstance(result["skills_section_output"], dict)
    assert isinstance(result["resume_output"], dict)
    assert isinstance(result["final_resume"], dict)

    for stage in {
        "evidence_extraction",
        "matcher",
        "resume_draft_builder",
        "skills_section_generator",
        "resume_output_assembler",
    }:
        assert stage in result["completed_stages"]

    assert set(result["final_resume"]["skills"]) == {
        "technical",
        "soft",
        "tools",
        "domain",
        "matched_skills",
        "strongest_skills",
    }

    allowed_skill_universe = {
        "documentation",
        "microsoft excel",
        "communication",
        "scheduling",
        "reporting",
        "leadership",
        "records management",
        "office coordination",
    }
    assert {
        skill.lower() for skill in result["matched_skills"]
    }.issubset(allowed_skill_universe)
