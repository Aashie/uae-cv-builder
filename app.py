"""
Streamlit demo UI for UAE CV Builder.

Purpose:
Provide a lightweight local demo for resume analysis and DOCX export.
"""

import json
import hashlib
import tempfile
from pathlib import Path

try:
    import streamlit as st
except ModuleNotFoundError:  # Keep helper imports testable when streamlit is unavailable.
    st = None

from models.job_description import JobDescription
from engine.candidate_profile_text_parser import parse_candidate_profile_text
from engine.job_description_text_parser import parse_job_description_text
from engine.resume_text_extractor import extract_resume_text
from engine.section_evidence_trace import build_section_evidence_trace
from engine.upload_paste_analysis_pipeline import run_upload_paste_analysis


SAMPLES_DIR = Path(__file__).resolve().parent / "samples"
SAMPLE_PROFILE_PATH = SAMPLES_DIR / "sample_profile_admin.json"
SAMPLE_JOB_PATH = SAMPLES_DIR / "sample_job_admin.json"


def _initialize_session_state() -> None:
    """Initialize upload/paste flow session state keys once."""
    defaults = {
        "uploaded_cv_name": "",
        "uploaded_cv_type": "",
        "uploaded_cv_size": 0,
        "extracted_cv_text": "",
        "extracted_cv_metadata": {},
        "cv_extraction_result": {},
        "cv_extraction_status": "",
        "cv_extraction_errors": [],
        "pasted_job_text": "",
        "parsed_candidate_profile": {},
        "candidate_parse_result": {},
        "parsed_jd": {},
        "job_parse_result": {},
        "analysis_result": {},
        "analysis_baseline": "",
        "profile_edited": False,
        "analysis_stale": False,
        "candidate_parse_source_text": "",
        "job_parse_source_text": "",
        "reviewed_candidate_profile": {},
        "candidate_review_source_signature": "",
        "candidate_review_saved": False,
        "review_name": "",
        "review_skills": "",
        "review_experience": "",
        "review_projects": "",
        "review_certifications": "",
        "review_achievements": "",
        "upload_pipeline_result": {},
        "analysis_completed": False,
        "analysis_errors": [],
        "analysis_warnings": [],
        "real_flow_docx_ready": False,
        "real_flow_docx_blockers": [],
        "real_flow_docx_error": "",
        "real_flow_evidence_trace": {},
        "real_flow_evidence_trace_error": "",
    }
    for key, default in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default


def _clear_downstream_upload_state() -> None:
    """Clear parser/analysis state that depends on uploaded CV content."""
    st.session_state["parsed_candidate_profile"] = {}
    st.session_state["candidate_parse_result"] = {}
    st.session_state["candidate_parse_source_text"] = ""
    st.session_state["parsed_jd"] = {}
    st.session_state["job_parse_result"] = {}
    st.session_state["job_parse_source_text"] = ""
    st.session_state["analysis_result"] = {}
    st.session_state["analysis_baseline"] = ""
    st.session_state["profile_edited"] = False
    st.session_state["analysis_stale"] = False
    _clear_upload_analysis_state()
    _clear_candidate_review_state()


def _clear_candidate_review_state() -> None:
    """Clear reviewed candidate profile state."""
    st.session_state["reviewed_candidate_profile"] = {}
    st.session_state["candidate_review_source_signature"] = ""
    st.session_state["candidate_review_saved"] = False
    st.session_state["review_name"] = ""
    st.session_state["review_skills"] = ""
    st.session_state["review_experience"] = ""
    st.session_state["review_projects"] = ""
    st.session_state["review_certifications"] = ""
    st.session_state["review_achievements"] = ""
    st.session_state["profile_edited"] = False


def _clear_upload_analysis_state() -> None:
    """Clear real upload/paste analysis state."""
    st.session_state["upload_pipeline_result"] = {}
    st.session_state["analysis_result"] = {}
    st.session_state["analysis_completed"] = False
    st.session_state["analysis_errors"] = []
    st.session_state["analysis_warnings"] = []
    _clear_real_flow_docx_gate_state()
    _clear_real_flow_evidence_trace_state()


def _clear_real_flow_docx_gate_state() -> None:
    """Clear real-flow DOCX gate state."""
    st.session_state["real_flow_docx_ready"] = False
    st.session_state["real_flow_docx_blockers"] = []
    st.session_state["real_flow_docx_error"] = ""


def _clear_real_flow_evidence_trace_state() -> None:
    """Clear real-flow section evidence trace state."""
    st.session_state["real_flow_evidence_trace"] = {}
    st.session_state["real_flow_evidence_trace_error"] = ""


def _clear_candidate_parse_state() -> None:
    """Clear parsed candidate profile and analysis state."""
    st.session_state["parsed_candidate_profile"] = {}
    st.session_state["candidate_parse_result"] = {}
    st.session_state["candidate_parse_source_text"] = ""
    st.session_state["analysis_result"] = {}
    st.session_state["analysis_baseline"] = ""
    st.session_state["profile_edited"] = False
    st.session_state["analysis_stale"] = False
    _clear_upload_analysis_state()
    _clear_candidate_review_state()


def _clear_job_parse_state() -> None:
    """Clear parsed job description and analysis state."""
    st.session_state["parsed_jd"] = {}
    st.session_state["job_parse_result"] = {}
    st.session_state["job_parse_source_text"] = ""
    st.session_state["analysis_result"] = {}
    st.session_state["analysis_baseline"] = ""
    st.session_state["analysis_stale"] = False
    _clear_upload_analysis_state()


def _clear_cv_upload_state() -> None:
    """Clear CV extraction state and downstream upload/paste state."""
    st.session_state["uploaded_cv_name"] = ""
    st.session_state["uploaded_cv_type"] = ""
    st.session_state["uploaded_cv_size"] = 0
    st.session_state["extracted_cv_text"] = ""
    st.session_state["extracted_cv_metadata"] = {}
    st.session_state["cv_extraction_result"] = {}
    st.session_state["cv_extraction_status"] = ""
    st.session_state["cv_extraction_errors"] = []
    _clear_downstream_upload_state()


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


def _message_items(messages) -> list[str]:
    """Return non-empty display messages from strings or simple collections."""
    if not messages:
        return []
    if isinstance(messages, str):
        return [messages] if messages.strip() else []
    if isinstance(messages, (list, tuple, set)):
        items: list[str] = []
        for message in messages:
            items.extend(_message_items(message))
        return items
    return [str(messages)]


def _render_message_list(title: str, messages, level: str = "info") -> None:
    """Render user-facing messages line by line."""
    items = _message_items(messages)
    if not items:
        return
    if level == "warning":
        st.warning(title)
    elif level == "error":
        st.error(title)
    else:
        st.info(title)
    for item in items:
        st.write(f"- {item}")


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
            _render_message_list("Pipeline errors:", result["errors"], level="error")
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
        _render_message_list("Final resume validation errors:", validation.get("errors", []), level="error")
        return

    from engine.docx_exporter import export_resume_to_docx
    from engine.resume_export_adapter import build_resume_export_payload

    export_payload = build_resume_export_payload(final_resume)
    st.write("Export payload status:", export_payload.get("status", ""))
    if export_payload.get("status") != "success":
        _render_message_list("Export payload generation failed:", export_payload.get("errors", []), level="error")
        return

    exports_dir = Path("exports")
    output_path = exports_dir / "uae_cv_builder_demo.docx"
    export_result = export_resume_to_docx(export_payload, str(output_path))
    if export_result.get("status") != "success":
        _render_message_list("DOCX export failed:", export_result.get("errors", []), level="error")
        return

    with open(output_path, "rb") as docx_file:
        st.download_button(
            "Download DOCX Resume",
            data=docx_file,
            file_name="uae_cv_builder_demo.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )


def _extract_uploaded_cv_text(uploaded_cv) -> dict:
    """Extract text from an uploaded CV through a temporary local file."""
    suffix = Path(uploaded_cv.name).suffix
    temp_path = ""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(uploaded_cv.getvalue())
            temp_path = temp_file.name
        return extract_resume_text(temp_path)
    finally:
        if temp_path:
            Path(temp_path).unlink(missing_ok=True)


def _store_cv_extraction_result(uploaded_cv, extraction_result: dict) -> None:
    """Store upload metadata and extraction result in session state."""
    previous_text = st.session_state["extracted_cv_text"]
    st.session_state["uploaded_cv_name"] = uploaded_cv.name
    st.session_state["uploaded_cv_type"] = uploaded_cv.type or "Unknown"
    st.session_state["uploaded_cv_size"] = uploaded_cv.size
    st.session_state["cv_extraction_result"] = extraction_result
    st.session_state["cv_extraction_status"] = extraction_result.get("status", "")
    st.session_state["cv_extraction_errors"] = extraction_result.get("errors", [])

    if extraction_result.get("status") == "success":
        st.session_state["extracted_cv_text"] = extraction_result.get("text", "")
        st.session_state["extracted_cv_metadata"] = extraction_result.get("metadata", {})
    else:
        st.session_state["extracted_cv_text"] = ""
        st.session_state["extracted_cv_metadata"] = {}

    if st.session_state["extracted_cv_text"] != previous_text:
        _clear_candidate_parse_state()


def _process_uploaded_cv_if_needed(uploaded_cv) -> None:
    """Extract a new uploaded CV and update upload-flow state."""
    previous_name = st.session_state["uploaded_cv_name"]
    previous_size = st.session_state["uploaded_cv_size"]
    upload_changed = (
        uploaded_cv.name != previous_name
        or uploaded_cv.size != previous_size
    )

    if upload_changed:
        _clear_candidate_parse_state()

    if upload_changed or not st.session_state["cv_extraction_result"]:
        extraction_result = _extract_uploaded_cv_text(uploaded_cv)
        _store_cv_extraction_result(uploaded_cv, extraction_result)


def _render_cv_extraction_state() -> None:
    """Render safe extracted-text status and preview from session state."""
    status = st.session_state["cv_extraction_status"]
    if not status:
        return

    if status == "success":
        metadata = st.session_state["extracted_cv_metadata"]
        text = st.session_state["extracted_cv_text"]
        st.success("CV text extracted successfully.")
        if metadata.get("detected_extension"):
            st.write("Detected extension:", metadata["detected_extension"])
        st.write("Character count:", f"{len(text):,}")
        with st.expander("Extracted text preview", expanded=False):
            st.text_area(
                "Extracted CV text",
                value=text,
                height=260,
                disabled=True,
            )
    else:
        st.error("CV text extraction failed.")
        _render_message_list("CV text extraction errors:", st.session_state["cv_extraction_errors"], level="error")


def _render_uploaded_cv_extraction(uploaded_cv) -> None:
    """Render safe extracted-text status and preview for an uploaded CV."""
    _process_uploaded_cv_if_needed(uploaded_cv)

    st.write("File name:", uploaded_cv.name)
    st.write("File type:", uploaded_cv.type or "Unknown")
    st.write("File size:", f"{uploaded_cv.size:,} bytes")

    _render_cv_extraction_state()


def _parse_candidate_profile_if_needed() -> None:
    """Parse extracted CV text for preview when source text changes."""
    cv_text = st.session_state["extracted_cv_text"]
    expected_keys = {
        "name",
        "skills",
        "experience",
        "projects",
        "certifications",
        "achievements",
    }
    if not cv_text:
        st.session_state["parsed_candidate_profile"] = {}
        return

    if (
        st.session_state["candidate_parse_result"]
        and st.session_state["candidate_parse_source_text"] == cv_text
    ):
        cached_profile = st.session_state["candidate_parse_result"].get(
            "candidate_profile",
            {},
        )
        if (
            st.session_state["candidate_parse_result"].get("status") == "success"
            and not st.session_state["parsed_candidate_profile"]
            and isinstance(cached_profile, dict)
            and cached_profile
            and expected_keys.issubset(cached_profile)
        ):
            st.session_state["parsed_candidate_profile"] = cached_profile
        return

    parse_result = parse_candidate_profile_text(cv_text)
    st.session_state["candidate_parse_result"] = parse_result
    if parse_result.get("status") == "success":
        candidate_profile = parse_result.get(
            "candidate_profile",
            {},
        )
        if (
            isinstance(candidate_profile, dict)
            and candidate_profile
            and expected_keys.issubset(candidate_profile)
        ):
            st.session_state["parsed_candidate_profile"] = candidate_profile
        else:
            st.session_state["parsed_candidate_profile"] = {}
    else:
        st.session_state["parsed_candidate_profile"] = {}
    st.session_state["candidate_parse_source_text"] = cv_text


def _parse_job_description_if_needed() -> None:
    """Parse pasted JD text for preview when source text changes."""
    job_text = st.session_state["pasted_job_text"]
    if not job_text.strip():
        _clear_job_parse_state()
        return

    if (
        st.session_state["job_parse_result"]
        and st.session_state["job_parse_source_text"] == job_text
    ):
        cached_jd = st.session_state["job_parse_result"].get("job_description", {})
        if (
            st.session_state["job_parse_result"].get("status") == "success"
            and not st.session_state["parsed_jd"]
            and isinstance(cached_jd, dict)
            and cached_jd
        ):
            st.session_state["parsed_jd"] = cached_jd
        return

    parse_result = parse_job_description_text(job_text)
    st.session_state["job_parse_result"] = parse_result
    if parse_result.get("status") == "success":
        job_description = parse_result.get("job_description", {})
        if isinstance(job_description, dict) and job_description:
            st.session_state["parsed_jd"] = job_description
        else:
            st.session_state["parsed_jd"] = {}
    else:
        st.session_state["parsed_jd"] = {}
    st.session_state["job_parse_source_text"] = job_text


def _render_parser_messages(parse_result: dict, label: str = "Parser") -> None:
    """Render parser warnings and errors."""
    if parse_result.get("warnings"):
        _render_message_list(f"{label} warnings:", parse_result["warnings"], level="warning")
    if parse_result.get("errors"):
        _render_message_list(f"{label} errors:", parse_result["errors"], level="error")


def _render_candidate_profile_preview() -> None:
    """Render parsed candidate profile preview."""
    parse_result = st.session_state["candidate_parse_result"]
    if not st.session_state["extracted_cv_text"]:
        st.info("Upload a DOCX or PDF CV to preview parsed candidate profile.")
        return
    if not parse_result:
        return

    if parse_result.get("status") == "success":
        profile = st.session_state["parsed_candidate_profile"]
        st.success("Candidate profile parsed successfully.")
        if profile.get("name"):
            st.write("Candidate name:", profile["name"])
        preview_cols = st.columns(3)
        preview_cols[0].metric("Skills", len(profile.get("skills", [])))
        preview_cols[1].metric("Experience entries", len(profile.get("experience", [])))
        preview_cols[2].metric("Certifications", len(profile.get("certifications", [])))
        with st.expander("Parsed candidate profile", expanded=False):
            st.json(profile)
    else:
        st.error("Candidate profile parsing failed.")
    _render_parser_messages(parse_result, label="Candidate parser")


def _render_job_description_preview() -> None:
    """Render parsed job description preview."""
    parse_result = st.session_state["job_parse_result"]
    if not st.session_state["pasted_job_text"].strip():
        st.info("Paste a job description to preview parsed job requirements.")
        return
    if not parse_result:
        return

    if parse_result.get("status") == "success":
        parsed_jd = st.session_state["parsed_jd"]
        st.success("Job description parsed successfully.")
        if parsed_jd.get("job_title"):
            st.write("Job title:", parsed_jd["job_title"])
        preview_cols = st.columns(2)
        preview_cols[0].metric("Required skills", len(parsed_jd.get("required_skills", [])))
        preview_cols[1].metric("Requirements/keywords", len(parsed_jd.get("keywords", [])))
        with st.expander("Parsed job description", expanded=False):
            st.json(parsed_jd)
    else:
        st.error("Job description parsing failed.")
    _render_parser_messages(parse_result, label="Job parser")


def _render_parsed_preview_before_analysis() -> None:
    """Render upload/paste parser previews before analysis is enabled."""
    _parse_candidate_profile_if_needed()
    _parse_job_description_if_needed()

    st.markdown("### Parsed Preview Before Analysis")
    st.caption(
        "Review what the system extracted. Save the reviewed profile and paste "
        "a valid job description to run analysis."
    )
    preview_cols = st.columns(2)
    with preview_cols[0]:
        st.markdown('<div class="card-title">Candidate Profile Preview</div>', unsafe_allow_html=True)
        _render_candidate_profile_preview()
    with preview_cols[1]:
        st.markdown('<div class="card-title">Job Description Preview</div>', unsafe_allow_html=True)
        _render_job_description_preview()


def _candidate_profile_signature(profile: dict) -> str:
    """Return a deterministic signature for a parsed candidate profile."""
    return json.dumps(profile or {}, sort_keys=True)


def _normalize_review_line(text: str) -> str:
    """Normalize obvious whitespace in reviewed profile text."""
    return " ".join(str(text).split())


def _review_lines(text: str) -> list[str]:
    """Return non-empty normalized review lines."""
    return [
        _normalize_review_line(line)
        for line in str(text).splitlines()
        if _normalize_review_line(line)
    ]


def _item_text(item) -> str:
    """Return display text for a profile list item."""
    if isinstance(item, dict):
        return _normalize_review_line(item.get("text", ""))
    return _normalize_review_line(item)


def _profile_list_to_lines(items: list) -> str:
    """Convert profile list values to editable line text."""
    return "\n".join(_item_text(item) for item in items if _item_text(item))


def _experience_to_lines(entries: list[dict]) -> str:
    """Convert experience entries to editable line text."""
    return "\n".join(
        _normalize_review_line(entry.get("text", ""))
        for entry in entries
        if isinstance(entry, dict) and _normalize_review_line(entry.get("text", ""))
    )


def _copy_profile(profile: dict) -> dict:
    """Return a JSON-safe copy of a candidate profile."""
    return json.loads(json.dumps(profile or {}))


def _initialize_review_state_from_profile(profile: dict, signature: str) -> None:
    """Initialize review widget state from a newly parsed candidate profile."""
    profile_copy = _copy_profile(profile)
    st.session_state["reviewed_candidate_profile"] = profile_copy
    st.session_state["candidate_review_source_signature"] = signature
    st.session_state["candidate_review_saved"] = False
    st.session_state["profile_edited"] = False
    st.session_state["review_name"] = profile_copy.get("name", "")
    st.session_state["review_skills"] = _profile_list_to_lines(
        profile_copy.get("skills", [])
    )
    st.session_state["review_experience"] = _experience_to_lines(
        profile_copy.get("experience", [])
    )
    st.session_state["review_projects"] = _profile_list_to_lines(
        profile_copy.get("projects", [])
    )
    st.session_state["review_certifications"] = _profile_list_to_lines(
        profile_copy.get("certifications", [])
    )
    st.session_state["review_achievements"] = _profile_list_to_lines(
        profile_copy.get("achievements", [])
    )


def _ensure_candidate_review_state(profile: dict) -> None:
    """Initialize review state only when parsed candidate profile changes."""
    signature = _candidate_profile_signature(profile)
    if signature != st.session_state["candidate_review_source_signature"]:
        _initialize_review_state_from_profile(profile, signature)


def _build_reviewed_experience(lines: list[str], original_entries: list) -> list[dict]:
    """Build reviewed experience entries while preserving IDs by line order."""
    reviewed_experience: list[dict] = []
    for index, line in enumerate(lines):
        original_id = ""
        if index < len(original_entries) and isinstance(original_entries[index], dict):
            original_id = _normalize_review_line(original_entries[index].get("id", ""))
        reviewed_experience.append(
            {
                "id": original_id or f"exp-{index + 1}",
                "text": line,
                "skills": [],
            }
        )
    return reviewed_experience


def _build_reviewed_candidate_profile() -> dict:
    """Build a reviewed candidate profile from review form fields."""
    profile_keys = (
        "name",
        "skills",
        "experience",
        "projects",
        "certifications",
        "achievements",
    )
    parsed_profile = st.session_state["parsed_candidate_profile"]
    original_profile = (
        st.session_state["reviewed_candidate_profile"]
        or parsed_profile
    )
    reviewed = {
        "name": _normalize_review_line(st.session_state["review_name"]),
        "skills": _review_lines(st.session_state["review_skills"]),
        "experience": _build_reviewed_experience(
            _review_lines(st.session_state["review_experience"]),
            original_profile.get("experience", []),
        ),
        "projects": _review_lines(st.session_state["review_projects"]),
        "certifications": _review_lines(st.session_state["review_certifications"]),
        "achievements": _review_lines(st.session_state["review_achievements"]),
    }
    return {key: reviewed.get(key, [] if key != "name" else "") for key in profile_keys}


def _save_reviewed_candidate_profile() -> None:
    """Persist the reviewed candidate profile for future analysis integration."""
    had_analysis = bool(
        st.session_state["analysis_result"]
        or st.session_state["upload_pipeline_result"]
    )
    reviewed_profile = _build_reviewed_candidate_profile()
    has_reviewed_content = any(bool(reviewed_profile.get(key)) for key in reviewed_profile)
    if not has_reviewed_content:
        st.session_state["reviewed_candidate_profile"] = {}
        st.session_state["candidate_review_saved"] = False
        st.session_state["profile_edited"] = False
        st.error("Reviewed candidate profile could not be saved because it is empty.")
        return
    st.session_state["reviewed_candidate_profile"] = reviewed_profile
    st.session_state["candidate_review_saved"] = True
    st.session_state["profile_edited"] = True
    _clear_upload_analysis_state()
    st.session_state["analysis_baseline"] = ""
    st.session_state["analysis_stale"] = had_analysis


def _render_candidate_review_section() -> None:
    """Render simple human review/edit UI for parsed candidate profile."""
    st.markdown("### Review Parsed Candidate Profile")
    st.caption(
        "Edit only what is true and supported by your CV or your own knowledge. "
        "These edits become candidate-provided evidence."
    )

    parse_result = st.session_state["candidate_parse_result"]
    parsed_profile = st.session_state["parsed_candidate_profile"]
    if not (
        parse_result
        and parse_result.get("status") == "success"
        and parsed_profile
    ):
        st.info("Upload and parse a CV before reviewing the candidate profile.")
        return

    _ensure_candidate_review_state(parsed_profile)

    with st.form(key="review_form"):
        st.text_input("Name", key="review_name")
        st.text_area(
            "Skills",
            help="One skill per line.",
            height=140,
            key="review_skills",
        )
        st.text_area(
            "Experience",
            help="One experience line or bullet per line.",
            height=180,
            key="review_experience",
        )
        st.text_area(
            "Projects",
            help="One project per line.",
            height=120,
            key="review_projects",
        )
        st.text_area(
            "Certifications",
            help="One certification per line.",
            height=120,
            key="review_certifications",
        )
        st.text_area(
            "Achievements",
            help="One achievement per line.",
            height=120,
            key="review_achievements",
        )
        saved = st.form_submit_button("Save Reviewed Profile")

    if saved:
        _save_reviewed_candidate_profile()

    if st.session_state["candidate_review_saved"]:
        st.success("Reviewed candidate profile saved.")
        st.info("Reviewed profile is saved. Analysis becomes available once a valid job description is parsed.")
        with st.expander("Reviewed candidate profile", expanded=False):
            st.json(st.session_state["reviewed_candidate_profile"])


def _upload_analysis_readiness() -> tuple[bool, list[str]]:
    """Return whether the real upload/paste analysis flow is ready."""
    missing: list[str] = []
    if not st.session_state["extracted_cv_text"]:
        missing.append("Upload a DOCX or PDF CV.")
    if not st.session_state["candidate_review_saved"]:
        missing.append("Save the reviewed candidate profile.")
    if not isinstance(st.session_state["reviewed_candidate_profile"], dict) or not st.session_state["reviewed_candidate_profile"]:
        missing.append("Reviewed candidate profile is missing.")
    if not st.session_state["pasted_job_text"].strip():
        missing.append("Paste a full job description.")
    if not st.session_state["job_parse_result"]:
        missing.append("Preview the parsed job description.")
    elif st.session_state["job_parse_result"].get("status") != "success":
        missing.append("Fix job description parsing errors.")
    if not st.session_state["parsed_jd"]:
        missing.append("Parsed job description is missing.")
    return not missing, missing


def _normalize_for_baseline(payload):
    """Normalize profile-like payloads for deterministic baseline hashing."""
    if isinstance(payload, str):
        return payload.strip()
    if isinstance(payload, list):
        normalized_items = [
            _normalize_for_baseline(item)
            for item in payload
        ]
        normalized_items = [
            item for item in normalized_items
            if not (isinstance(item, str) and not item)
        ]
        if all(not isinstance(item, (dict, list)) for item in normalized_items):
            return sorted(normalized_items, key=lambda item: json.dumps(item, default=str))
        return sorted(
            normalized_items,
            key=lambda item: json.dumps(item, sort_keys=True, default=str),
        )
    if isinstance(payload, dict):
        return {
            key: _normalize_for_baseline(value)
            for key, value in payload.items()
        }
    return payload


def _stable_json_signature(payload) -> str:
    """Return a SHA-256 signature for a JSON-serializable payload."""
    serialized = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(serialized).hexdigest()


def _current_upload_analysis_baseline() -> str:
    """Return the current real-flow input baseline signature."""
    baseline_payload = {
        "extracted_cv_text": st.session_state["extracted_cv_text"],
        "reviewed_candidate_profile": _normalize_for_baseline(
            st.session_state["reviewed_candidate_profile"],
        ),
        "pasted_job_text": st.session_state["pasted_job_text"],
    }
    return _stable_json_signature(baseline_payload)


def _is_real_flow_analysis_stale() -> bool:
    """Return whether current real-flow inputs differ from analyzed baseline."""
    return (
        st.session_state["analysis_completed"] is True
        and bool(st.session_state["analysis_baseline"])
        and _current_upload_analysis_baseline() != st.session_state["analysis_baseline"]
    )


def _run_real_upload_analysis() -> None:
    """Run the real upload/paste analysis flow using the reviewed profile."""
    _clear_real_flow_evidence_trace_state()
    helper_result = run_upload_paste_analysis(
        st.session_state["extracted_cv_text"],
        st.session_state["pasted_job_text"],
        reviewed_candidate_profile=st.session_state["reviewed_candidate_profile"],
    )
    st.session_state["upload_pipeline_result"] = helper_result
    st.session_state["analysis_result"] = helper_result.get("analysis_result", {})
    st.session_state["analysis_errors"] = helper_result.get("errors", [])
    st.session_state["analysis_warnings"] = helper_result.get("warnings", [])
    st.session_state["analysis_completed"] = (
        helper_result.get("status") == "success"
        and bool(helper_result.get("analysis_result"))
    )
    if st.session_state["analysis_completed"]:
        st.session_state["analysis_baseline"] = _current_upload_analysis_baseline()
        st.session_state["analysis_stale"] = False
    else:
        st.session_state["analysis_completed"] = False
    _clear_real_flow_docx_gate_state()
    if (
        st.session_state["analysis_completed"]
        and st.session_state["analysis_result"]
        and st.session_state["analysis_result"].get("status") not in {"failed", "partial"}
        and st.session_state["analysis_result"].get("final_resume")
    ):
        try:
            st.session_state["real_flow_evidence_trace"] = build_section_evidence_trace(
                st.session_state["analysis_result"]["final_resume"],
                st.session_state["reviewed_candidate_profile"],
                st.session_state["parsed_jd"],
            )
        except Exception as error:
            st.session_state["real_flow_evidence_trace"] = {}
            st.session_state["real_flow_evidence_trace_error"] = str(error)


def _render_readiness_messages(missing_items: list[str]) -> None:
    """Render short readiness guidance."""
    if not missing_items:
        st.success("Ready to analyze the reviewed profile against the pasted job description.")
        return
    st.info("Complete these steps before analysis:")
    for item in missing_items:
        st.write(f"- {item}")


def _render_analysis_internal_messages(analysis_result: dict) -> None:
    """Render internal analysis status and failure-safety details honestly."""
    if analysis_result.get("status"):
        st.write("Internal analysis status:", analysis_result["status"])
    if analysis_result.get("failed_stage"):
        st.write("Failed stage:", analysis_result["failed_stage"])
    if analysis_result.get("errors"):
        _render_message_list("Analysis errors:", analysis_result["errors"], level="error")
    if analysis_result.get("completed_stages"):
        with st.expander("Completed analysis stages", expanded=False):
            st.write(analysis_result["completed_stages"])
    validation = analysis_result.get("final_resume_validation")
    if validation:
        validation_label = "Valid" if validation.get("is_valid") else "Needs review"
        st.write("Final resume validation:", validation_label)
        if validation.get("errors"):
            _render_message_list("Final resume validation errors:", validation["errors"], level="error")


def _real_flow_docx_gate(analysis_result: dict) -> tuple[bool, list[str]]:
    """Return whether real-flow DOCX download may be generated."""
    blockers: list[str] = []
    helper_result = st.session_state["upload_pipeline_result"]
    stale = st.session_state["analysis_stale"] or _is_real_flow_analysis_stale()

    if not analysis_result:
        blockers.append("Run analysis before downloading.")
    if stale:
        blockers.append("Analysis is stale. Re-run analysis before downloading.")
    if not st.session_state["analysis_completed"]:
        blockers.append("Analysis did not complete successfully.")
    if helper_result.get("status") != "success":
        blockers.append("Upload/paste analysis did not complete successfully.")
    if analysis_result and analysis_result.get("status") in {"failed", "partial"}:
        blockers.append("Analysis did not complete successfully enough for evidence trace.")

    final_resume = analysis_result.get("final_resume") if analysis_result else {}
    validation = analysis_result.get("final_resume_validation") if analysis_result else {}
    if not final_resume:
        blockers.append("Final resume is missing.")
    if not validation:
        blockers.append("Final resume validation is missing.")
    elif validation.get("is_valid") is not True:
        blockers.append("Final resume validation failed.")
    if validation and validation.get("errors"):
        blockers.extend(str(error) for error in validation["errors"])
    if final_resume:
        evidence_trace = st.session_state["real_flow_evidence_trace"]
        if not evidence_trace:
            blockers.append("Section-level evidence trace is missing.")
        elif evidence_trace.get("status") == "failed":
            blockers.append("Section-level evidence trace failed.")

    return not blockers, blockers


def _build_real_flow_docx_bytes(final_resume: dict) -> bytes | None:
    """Build DOCX bytes for a validated real-flow final resume."""
    from engine.docx_exporter import export_resume_to_docx
    from engine.resume_export_adapter import build_resume_export_payload

    export_payload = build_resume_export_payload(final_resume)
    if export_payload.get("status") != "success":
        st.session_state["real_flow_docx_error"] = "; ".join(
            str(error) for error in export_payload.get("errors", [])
        )
        return None

    temp_path = ""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_file:
            temp_path = temp_file.name
        export_result = export_resume_to_docx(export_payload, temp_path)
        if export_result.get("status") != "success":
            st.session_state["real_flow_docx_error"] = "; ".join(
                str(error) for error in export_result.get("errors", [])
            )
            return None
        return Path(temp_path).read_bytes()
    finally:
        if temp_path:
            Path(temp_path).unlink(missing_ok=True)


def _render_real_flow_download_gate(analysis_result: dict) -> None:
    """Render real-flow DOCX download safety check and button when safe."""
    st.markdown("#### Download Safety Check")
    can_download, blockers = _real_flow_docx_gate(analysis_result)
    st.session_state["real_flow_docx_ready"] = can_download
    st.session_state["real_flow_docx_blockers"] = blockers

    if blockers:
        _render_message_list("Reviewed resume DOCX download is blocked.", blockers, level="warning")
        return

    try:
        docx_bytes = _build_real_flow_docx_bytes(analysis_result["final_resume"])
    except Exception as error:
        st.session_state["real_flow_docx_ready"] = False
        st.session_state["real_flow_docx_error"] = str(error)
        st.error("DOCX export is currently blocked because export generation failed.")
        st.write(st.session_state["real_flow_docx_error"])
        return

    if not docx_bytes:
        st.session_state["real_flow_docx_ready"] = False
        st.error("DOCX export is currently blocked because export generation failed.")
        if st.session_state["real_flow_docx_error"]:
            st.write(st.session_state["real_flow_docx_error"])
        return

    st.success("Download safety checks passed.")
    st.download_button(
        "Download Reviewed Resume DOCX",
        data=docx_bytes,
        file_name="reviewed_resume.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


def _format_section_title(section_name: str) -> str:
    """Return a readable evidence trace section title."""
    titles = {
        "job_title": "Job title",
        "professional_summary": "Professional summary",
        "skills": "Skills",
        "experience_bullets": "Experience bullets",
        "metadata_note": "Metadata note",
    }
    return titles.get(section_name, section_name.replace("_", " ").title())


def _render_section_trace(section_trace: dict) -> None:
    """Render one section-level evidence trace."""
    warnings = section_trace.get("warnings", [])
    if warnings:
        _render_message_list("Trace warnings:", warnings, level="warning")
    st.write("Supported:", section_trace.get("supported"))
    st.write("Support level:", section_trace.get("support_level", ""))
    st.write("Evidence sources:", section_trace.get("evidence_sources", []))
    st.write("Evidence items:", section_trace.get("evidence_items", []))
    if section_trace.get("section") == "skills":
        st.write("Supported resume skills:", section_trace.get("supported_resume_skills", []))
        st.write("Unsupported resume skills:", section_trace.get("unsupported_resume_skills", []))
        st.write("Candidate profile skills:", section_trace.get("candidate_profile_skills", []))


def _render_real_flow_evidence_trace(analysis_result: dict) -> None:
    """Render the real-flow section-level evidence trace."""
    st.markdown("#### Evidence Trace")
    st.warning("Section-level evidence trace, not per-claim proof.")

    if analysis_result.get("status") in {"failed", "partial"}:
        st.info("Evidence trace is not shown because analysis did not complete successfully.")
        return

    if st.session_state["real_flow_evidence_trace_error"]:
        st.error("Evidence trace could not be generated.")
        st.write(st.session_state["real_flow_evidence_trace_error"])

    evidence_trace = st.session_state["real_flow_evidence_trace"]
    if not evidence_trace:
        st.info("Evidence trace will appear after a successful analysis with a final resume.")
        return

    if evidence_trace.get("status") == "failed":
        st.error("Section-level evidence trace failed.")
        if evidence_trace.get("errors"):
            _render_message_list("Evidence trace errors:", evidence_trace["errors"], level="error")
        return

    section_traces = evidence_trace.get("section_traces", {})
    for section_name in (
        "job_title",
        "professional_summary",
        "skills",
        "experience_bullets",
        "metadata_note",
    ):
        section_trace = section_traces.get(section_name, {})
        if not section_trace:
            continue
        with st.expander(_format_section_title(section_name), expanded=False):
            _render_section_trace(section_trace)


def _render_real_flow_analysis_results() -> None:
    """Render real upload/paste analysis results without DOCX download."""
    st.markdown("### Analysis Results")
    helper_result = st.session_state["upload_pipeline_result"]
    analysis_result = st.session_state["analysis_result"]

    if not helper_result and not analysis_result:
        st.info("Run analysis after reviewing your profile and job description.")
        return

    if helper_result and helper_result.get("status") == "failed":
        _render_message_list("Upload/paste analysis failed.", helper_result.get("errors", []), level="error")
        return

    if st.session_state["analysis_warnings"]:
        _render_message_list("Analysis warnings:", st.session_state["analysis_warnings"], level="warning")

    if analysis_result:
        if st.session_state["analysis_stale"] or _is_real_flow_analysis_stale():
            st.warning(
                "This analysis is stale because the CV, reviewed profile, or job "
                "description changed. Re-run analysis before downloading."
            )
        _render_analysis_internal_messages(analysis_result)
        if analysis_result.get("matched_skills") or analysis_result.get("missing_skills"):
            skill_cols = st.columns(2)
            with skill_cols[0]:
                _render_tags(
                    "Matched skills",
                    analysis_result.get("matched_skills", []),
                    "green",
                    "No matched skills returned.",
                )
            with skill_cols[1]:
                _render_tags(
                    "Missing skills",
                    analysis_result.get("missing_skills", []),
                    "red",
                    "No missing skills returned.",
                )
        if analysis_result.get("skill_gaps"):
            with st.expander("Skill gap summary", expanded=False):
                st.json(analysis_result["skill_gaps"])
        if analysis_result.get("recommendations"):
            with st.expander("Recommendations", expanded=False):
                st.json(analysis_result["recommendations"])
        if analysis_result.get("final_resume"):
            _render_resume_preview(analysis_result["final_resume"])
        _render_real_flow_evidence_trace(analysis_result)
        _render_real_flow_download_gate(analysis_result)


def main() -> None:
    """Render the Streamlit demo UI."""
    if st is None:
        raise ModuleNotFoundError("streamlit is required to run the demo UI")

    st.set_page_config(
        page_title="UAE CV Builder Demo",
        page_icon="\U0001F4C4",
        layout="wide",
    )
    _initialize_session_state()
    _inject_css()

    st.markdown("# UAE CV Builder")
    st.markdown(
        '<div class="subtitle">Evidence-based resume analysis and DOCX generation for UAE job applications.</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="accent-line"></div>', unsafe_allow_html=True)
    st.markdown(_badge("No-invention resume pipeline", "gray"), unsafe_allow_html=True)

    st.markdown("## Start with your CV and job description")
    primary_cols = st.columns(2)
    with primary_cols[0]:
        st.markdown('<div class="card-title">Upload your CV</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="card-subtitle">Upload your existing CV. The system extracts text and uses only reviewed candidate information for analysis.</div>',
            unsafe_allow_html=True,
        )
        uploaded_cv = st.file_uploader("Upload your CV", type=["pdf", "docx"])
        if uploaded_cv is not None:
            _render_uploaded_cv_extraction(uploaded_cv)
        else:
            _clear_cv_upload_state()

    with primary_cols[1]:
        st.markdown('<div class="card-title">Paste full job description</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="card-subtitle">Paste the full job post. You do not need to separate skills manually.</div>',
            unsafe_allow_html=True,
        )
        st.text_area(
            "Full job description",
            placeholder=(
                "Paste the full job description here, including responsibilities, "
                "requirements, qualifications, and skills."
            ),
            height=220,
            key="pasted_job_text",
        )

    _render_parsed_preview_before_analysis()
    _render_candidate_review_section()

    ready_to_analyze, missing_readiness_items = _upload_analysis_readiness()
    _render_readiness_messages(missing_readiness_items)
    if st.button("Analyze My CV", type="primary", disabled=not ready_to_analyze):
        _run_real_upload_analysis()
    st.info(
        "Real upload-based analysis is available after you save the reviewed profile "
        "and paste a valid job description. DOCX download appears only after safety "
        "and stale-validation checks pass."
    )
    _render_real_flow_analysis_results()

    result = None
    with st.expander("Developer Sample Mode: structured profile analysis", expanded=False):
        st.info(
            "Developer Sample Mode uses built-in sample data for testing the interface. "
            "It does not analyze your uploaded CV and does not affect the real Upload "
            "CV + Paste JD analysis above."
        )
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
            st.markdown('<div class="card-subtitle">Structured fields for the current working demo</div>', unsafe_allow_html=True)
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

    if result:
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
