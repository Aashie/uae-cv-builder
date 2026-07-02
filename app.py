"""
Streamlit demo UI for UAE CV Builder.

Purpose:
Provide a lightweight local demo for resume analysis and DOCX export.
"""

import json
from pathlib import Path

try:
    import streamlit as st
except ModuleNotFoundError:  # Keep helper imports testable when streamlit is unavailable.
    st = None

from models.job_description import JobDescription


SAMPLES_DIR = Path(__file__).resolve().parent / "samples"
SAMPLE_PROFILE_PATH = SAMPLES_DIR / "sample_profile_admin.json"
SAMPLE_JOB_PATH = SAMPLES_DIR / "sample_job_admin.json"


def parse_skill_lines(text: str) -> list[str]:
    """Parse newline or comma-separated skills into a clean list."""
    if not isinstance(text, str):
        return []

    normalized = text.replace(",", "\n")
    return [skill.strip() for skill in normalized.splitlines() if skill.strip()]


def load_sample_profile() -> dict:
    """Load the sample administrative profile JSON."""
    if not SAMPLE_PROFILE_PATH.exists():
        raise FileNotFoundError(f"Sample profile file not found: {SAMPLE_PROFILE_PATH}")

    return json.loads(SAMPLE_PROFILE_PATH.read_text(encoding="utf-8"))


def load_sample_job_values() -> dict:
    """Load the sample administrative job JSON."""
    if not SAMPLE_JOB_PATH.exists():
        raise FileNotFoundError(f"Sample job file not found: {SAMPLE_JOB_PATH}")

    return json.loads(SAMPLE_JOB_PATH.read_text(encoding="utf-8"))


def get_sample_profile() -> dict:
    """Return the sample administrative profile from samples/."""
    return load_sample_profile()


def get_default_job_values() -> dict:
    """Return sample job values formatted for Streamlit inputs."""
    job = load_sample_job_values()
    return {
        "job_title": job.get("job_title", ""),
        "required_skills": "\n".join(job.get("required_skills", [])),
        "soft_skills": "\n".join(job.get("soft_skills", [])),
        "experience_level": job.get("experience_level", ""),
        "education": job.get("education", ""),
    }


def build_job_description(values: dict) -> JobDescription:
    """Build a JobDescription model from UI values."""
    return JobDescription(
        job_title=values["job_title"],
        required_skills=parse_skill_lines(values["required_skills"]),
        soft_skills=parse_skill_lines(values["soft_skills"]),
        experience_level=values["experience_level"],
        education=values["education"],
    )


def run_pipeline(profile: dict, job_description: JobDescription) -> dict:
    """Run the deterministic resume analysis pipeline."""
    from engine.resume_analysis_orchestrator import run_resume_analysis

    return run_resume_analysis(profile, job_description)


def _render_analysis_result(result: dict) -> None:
    """Render key analysis outputs."""
    st.subheader("Analysis Result")
    st.write("Status:", result.get("status", ""))
    st.write("Match score:", result.get("match_score", 0))
    st.write("Matched skills:", result.get("matched_skills", []))
    st.write("Missing skills:", result.get("missing_skills", []))
    st.write("Final resume validation:", result.get("final_resume_validation", {}))

    if result.get("errors"):
        st.warning("Pipeline completed with messages.")
        st.write(result["errors"])


def _render_docx_download(final_resume: dict, validation: dict) -> None:
    """Build export payload, write DOCX, and render a download button."""
    if not validation.get("is_valid"):
        st.error("Final resume validation failed. DOCX export was not generated.")
        st.write(validation.get("errors", []))
        return

    from engine.docx_exporter import export_resume_to_docx
    from engine.resume_export_adapter import build_resume_export_payload

    export_payload = build_resume_export_payload(final_resume)
    st.write("Export payload status:", export_payload.get("status", ""))
    if export_payload.get("status") != "success":
        st.error("Export payload generation failed.")
        st.write(export_payload.get("errors", []))
        return

    exports_dir = Path("exports")
    output_path = exports_dir / "uae_cv_builder_demo.docx"
    export_result = export_resume_to_docx(export_payload, str(output_path))
    if export_result.get("status") != "success":
        st.error("DOCX export failed.")
        st.write(export_result.get("errors", []))
        return

    with open(output_path, "rb") as docx_file:
        st.download_button(
            "Download DOCX Resume",
            data=docx_file,
            file_name="uae_cv_builder_demo.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )


def main() -> None:
    """Render the Streamlit demo UI."""
    if st is None:
        raise ModuleNotFoundError("streamlit is required to run the demo UI")

    st.set_page_config(page_title="UAE CV Builder Demo")
    st.title("UAE CV Builder Demo")
    st.write("Evidence-based resume analysis and DOCX generation for UAE job applications.")

    use_sample = st.checkbox("Use sample Administrative Assistant profile", value=True)
    sample_profile = get_sample_profile()
    profile_text = st.text_area(
        "Candidate profile JSON",
        value=json.dumps(sample_profile if use_sample else {}, indent=2),
        height=320,
    )

    defaults = get_default_job_values()
    job_title = st.text_input("Job title", value=defaults["job_title"])
    required_skills = st.text_area(
        "Required skills (one per line or comma-separated)",
        value=defaults["required_skills"],
    )
    soft_skills = st.text_area(
        "Soft skills (one per line or comma-separated)",
        value=defaults["soft_skills"],
    )
    experience_level = st.text_input("Experience level", value=defaults["experience_level"])
    education = st.text_input("Education", value=defaults["education"])

    if st.button("Run Analysis"):
        try:
            profile = json.loads(profile_text)
        except json.JSONDecodeError as error:
            st.error(f"Candidate profile JSON is invalid: {error}")
            return

        job_description = build_job_description(
            {
                "job_title": job_title,
                "required_skills": required_skills,
                "soft_skills": soft_skills,
                "experience_level": experience_level,
                "education": education,
            }
        )
        result = run_pipeline(profile, job_description)
        _render_analysis_result(result)

        final_resume = result.get("final_resume", {})
        if final_resume:
            _render_docx_download(
                final_resume,
                result.get("final_resume_validation", {}),
            )


if __name__ == "__main__":
    main()
