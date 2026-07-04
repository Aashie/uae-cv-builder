"""
Streamlit demo UI for UAE CV Builder.

Purpose:
Provide a lightweight local demo for resume analysis and DOCX export.
"""

import json
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


def _clear_candidate_parse_state() -> None:
    """Clear parsed candidate profile and analysis state."""
    st.session_state["parsed_candidate_profile"] = {}
    st.session_state["candidate_parse_result"] = {}
    st.session_state["candidate_parse_source_text"] = ""
    st.session_state["analysis_result"] = {}
    st.session_state["analysis_baseline"] = ""
    st.session_state["profile_edited"] = False
    st.session_state["analysis_stale"] = False
    _clear_candidate_review_state()


def _clear_job_parse_state() -> None:
    """Clear parsed job description and analysis state."""
    st.session_state["parsed_jd"] = {}
    st.session_state["job_parse_result"] = {}
    st.session_state["job_parse_source_text"] = ""
    st.session_state["analysis_result"] = {}
    st.session_state["analysis_baseline"] = ""
    st.session_state["analysis_stale"] = False


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
        st.write(st.session_state["cv_extraction_errors"])


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
    if not cv_text:
        st.session_state["parsed_candidate_profile"] = {}
        return

    if (
        st.session_state["candidate_parse_result"]
        and st.session_state["candidate_parse_source_text"] == cv_text
    ):
        return

    parse_result = parse_candidate_profile_text(cv_text)
    st.session_state["candidate_parse_result"] = parse_result
    if parse_result.get("status") == "success":
        st.session_state["parsed_candidate_profile"] = parse_result.get(
            "candidate_profile",
            {},
        )
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
        return

    parse_result = parse_job_description_text(job_text)
    st.session_state["job_parse_result"] = parse_result
    if parse_result.get("status") == "success":
        st.session_state["parsed_jd"] = parse_result.get("job_description", {})
    else:
        st.session_state["parsed_jd"] = {}
    st.session_state["job_parse_source_text"] = job_text


def _render_parser_messages(parse_result: dict) -> None:
    """Render parser warnings and errors."""
    if parse_result.get("warnings"):
        st.warning(parse_result["warnings"])
    if parse_result.get("errors"):
        st.write(parse_result["errors"])


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
    _render_parser_messages(parse_result)


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
    _render_parser_messages(parse_result)


def _render_parsed_preview_before_analysis() -> None:
    """Render upload/paste parser previews before analysis is enabled."""
    _parse_candidate_profile_if_needed()
    _parse_job_description_if_needed()

    st.markdown("### Parsed Preview Before Analysis")
    st.caption(
        "Review what the system extracted. Full analysis will be enabled after "
        "the review/edit step."
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
    return {key: reviewed.get(key, []) for key in parsed_profile}


def _save_reviewed_candidate_profile() -> None:
    """Persist the reviewed candidate profile for future analysis integration."""
    st.session_state["reviewed_candidate_profile"] = _build_reviewed_candidate_profile()
    st.session_state["candidate_review_saved"] = True
    st.session_state["profile_edited"] = True
    st.session_state["analysis_result"] = {}
    st.session_state["analysis_baseline"] = ""
    st.session_state["analysis_stale"] = True


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
        st.info("Analysis is still disabled until the next integration sprint.")
        with st.expander("Reviewed candidate profile", expanded=False):
            st.json(st.session_state["reviewed_candidate_profile"])


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
            '<div class="card-subtitle">Upload your existing CV. The system will eventually extract only information present in your document.</div>',
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

    st.button("Analyze My CV", type="primary", disabled=True)
    st.info(
        "Full analysis will be enabled after parsed profile review/edit is complete. "
        "Use Advanced Demo Mode below to run the current structured demo."
    )

    result = None
    with st.expander("Advanced Demo Mode: structured profile analysis", expanded=False):
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
