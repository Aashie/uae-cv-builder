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


def _inject_css() -> None:
    """Inject lightweight Streamlit presentation CSS."""
    st.markdown(
        """
        <style>
        .stApp { background: #F8F9FA; color: #1A1A2E; }
        h1, h2, h3 { color: #1A1A2E; font-weight: 700; }
        .subtitle { color: #6B7280; font-size: 1.05rem; margin-bottom: 0.6rem; }
        .accent-line { width: 80px; height: 4px; background: #0A6E7C; border-radius: 999px; margin: 0.7rem 0 1rem; }
        .card { background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 8px; padding: 16px; margin-bottom: 16px; }
        .card-title { font-weight: 700; color: #1A1A2E; font-size: 1.05rem; margin-bottom: 0.15rem; }
        .card-subtitle { color: #6B7280; font-size: 0.92rem; margin-bottom: 0.8rem; }
        .badge { display: inline-block; padding: 0.28rem 0.6rem; border-radius: 999px; font-size: 0.82rem; font-weight: 700; margin: 0.15rem 0.25rem 0.15rem 0; }
        .badge-green { background: #E6F4EA; color: #137333; }
        .badge-red { background: #FCE8E6; color: #A50E0E; }
        .badge-gray { background: #F3F4F6; color: #6B7280; }
        .badge-orange { background: #FFF7ED; color: #C65D3B; }
        .score-display { color: #0A6E7C; font-size: 2.2rem; font-weight: 800; line-height: 1; }
        .section-label { color: #6B7280; font-size: 0.86rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.02em; }
        .stButton > button, .stDownloadButton > button { background: #0A6E7C !important; color: #FFFFFF !important; border-radius: 6px !important; border: 1px solid #0A6E7C !important; font-weight: 700 !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _badge(label: str, style: str = "gray") -> str:
    """Return a small HTML badge."""
    return f'<span class="badge badge-{style}">{label}</span>'


def _status_style(status: str) -> str:
    """Return badge style for a pipeline status."""
    if status == "success":
        return "green"
    if status == "failed":
        return "red"
    if status == "partial":
        return "orange"
    return "gray"


def _render_tags(title: str, values: list[str], style: str, empty_message: str) -> None:
    """Render skill values as pill tags."""
    st.markdown(f'<div class="section-label">{title}</div>', unsafe_allow_html=True)
    if values:
        tags = "".join(_badge(str(value), style) for value in values)
        st.markdown(tags, unsafe_allow_html=True)
    else:
        st.caption(empty_message)


def _render_analysis_result(result: dict) -> None:
    """Render key analysis outputs."""
    status = result.get("status", "")
    validation = result.get("final_resume_validation", {})
    validation_label = "Valid" if validation.get("is_valid") else "Needs review"
    validation_style = "green" if validation.get("is_valid") else "red"

    st.markdown("### Results Dashboard")
    metric_cols = st.columns(5)
    metric_cols[0].markdown(_badge(status.title() or "Unknown", _status_style(status)), unsafe_allow_html=True)
    metric_cols[0].caption("Pipeline status")
    metric_cols[1].markdown(f'<div class="score-display">{result.get("match_score", 0)}</div>', unsafe_allow_html=True)
    metric_cols[1].caption("Match score")
    metric_cols[2].metric("Matched", len(result.get("matched_skills", [])))
    metric_cols[3].metric("Missing", len(result.get("missing_skills", [])))
    metric_cols[4].markdown(_badge(validation_label, validation_style), unsafe_allow_html=True)
    metric_cols[4].caption("Final resume validation")

    st.markdown('<div class="card">', unsafe_allow_html=True)
    skill_cols = st.columns(2)
    with skill_cols[0]:
        _render_tags(
            "Matched skills",
            result.get("matched_skills", []),
            "green",
            "No matched skills returned.",
        )
    with skill_cols[1]:
        _render_tags(
            "Missing skills",
            result.get("missing_skills", []),
            "red",
            "No missing skills returned.",
        )
    st.markdown("</div>", unsafe_allow_html=True)

    if result.get("errors"):
        with st.expander("Pipeline messages", expanded=status in {"partial", "failed"}):
            st.write(result["errors"])
            if result.get("failed_stage"):
                st.write("Failed stage:", result["failed_stage"])
            if result.get("completed_stages"):
                st.write("Completed stages:", result["completed_stages"])


def _render_resume_preview(final_resume: dict) -> None:
    """Render a clean final resume preview."""
    if not final_resume:
        return

    st.markdown("### Resume Preview")
    summary_tab, skills_tab, experience_tab = st.tabs(
        ["Professional Summary", "Skills", "Experience Highlights"]
    )

    with summary_tab:
        summary = final_resume.get("professional_summary", "")
        st.write(summary if summary else "No content available for this section.")

    with skills_tab:
        skills = final_resume.get("skills", {})
        visible_groups = {
            "Technical": skills.get("technical", []),
            "Soft Skills": skills.get("soft", []),
            "Tools": skills.get("tools", []),
            "Domain": skills.get("domain", []),
        }
        if any(visible_groups.values()):
            for label, items in visible_groups.items():
                _render_tags(label, items, "gray", "")
        else:
            st.write("No content available for this section.")

    with experience_tab:
        bullets = final_resume.get("experience_bullets", [])
        if bullets:
            for bullet in bullets:
                text = bullet.get("text", "") if isinstance(bullet, dict) else str(bullet)
                if text:
                    st.markdown(f"- {text}")
        else:
            st.write("No content available for this section.")


def _render_docx_download(final_resume: dict, validation: dict) -> None:
    """Build export payload, write DOCX, and render a download button."""
    st.markdown("### DOCX Export")
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

    st.set_page_config(
        page_title="UAE CV Builder Demo",
        page_icon="\U0001F4C4",
        layout="wide",
    )
    _inject_css()

    st.markdown("# UAE CV Builder")
    st.markdown(
        '<div class="subtitle">Evidence-based resume analysis and DOCX generation for UAE job applications.</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="accent-line"></div>', unsafe_allow_html=True)
    st.markdown(_badge("No-invention resume pipeline", "gray"), unsafe_allow_html=True)

    defaults = get_default_job_values()
    input_cols = st.columns(2)

    with input_cols[0]:
        st.markdown('<div class="card-title">Candidate Profile</div>', unsafe_allow_html=True)
        st.markdown('<div class="card-subtitle">Paste your profile JSON here</div>', unsafe_allow_html=True)
        use_sample = st.checkbox("Use sample Administrative Assistant profile", value=True)
        sample_profile = get_sample_profile()
        profile_text = st.text_area(
            "Candidate profile JSON",
            value=json.dumps(sample_profile if use_sample else {}, indent=2),
            height=360,
        )

    with input_cols[1]:
        st.markdown('<div class="card-title">Job Description</div>', unsafe_allow_html=True)
        st.markdown('<div class="card-subtitle">Describe the role and required skills</div>', unsafe_allow_html=True)
        job_title = st.text_input("Job Title", value=defaults["job_title"])
        required_skills = st.text_area(
            "Required Skills",
            value=defaults["required_skills"],
            help="Use one skill per line or comma-separated skills.",
        )
        soft_skills = st.text_area(
            "Soft Skills",
            value=defaults["soft_skills"],
            help="Use one skill per line or comma-separated skills.",
        )
        experience_level = st.text_input("Experience Level", value=defaults["experience_level"])
        education = st.text_input("Education", value=defaults["education"])

    st.markdown("")
    run_clicked = st.button("▶ Run Analysis", type="primary")

    if run_clicked:
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
        with st.spinner("Running evidence-based analysis..."):
            result = run_pipeline(profile, job_description)
        _render_analysis_result(result)

        final_resume = result.get("final_resume", {})
        if final_resume:
            _render_resume_preview(final_resume)
            _render_docx_download(
                final_resume,
                result.get("final_resume_validation", {}),
            )


if __name__ == "__main__":
    main()