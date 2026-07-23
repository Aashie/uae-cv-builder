"""Deterministic section-level evidence trace helpers."""

from engine.matcher import skill_is_supported_by_candidate


def _as_list(value):
    """Return value as a list without splitting strings."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def _shorten(value, max_length=160):
    """Return a short UI-safe display string."""
    text = str(value).strip()
    if len(text) <= max_length:
        return text
    return f"{text[: max_length - 3].rstrip()}..."


def _normalize_text(value):
    """Normalize text for exact conservative matching."""
    return " ".join(str(value).strip().lower().split())


def _unique_preserve_order(items):
    """Return unique non-empty strings while preserving first-seen order."""
    unique = []
    seen = set()
    for item in items:
        if item is None:
            continue
        text = str(item).strip()
        if not text:
            continue
        normalized = _normalize_text(text)
        if normalized in seen:
            continue
        seen.add(normalized)
        unique.append(text)
    return unique


def _normalize_profile(candidate_profile):
    """Return safe profile defaults without mutating the input."""
    if not isinstance(candidate_profile, dict):
        candidate_profile = {}
    return {
        "name": str(candidate_profile.get("name", "") or ""),
        "skills": list(_as_list(candidate_profile.get("skills", []))),
        "experience": list(_as_list(candidate_profile.get("experience", []))),
        "projects": list(_as_list(candidate_profile.get("projects", []))),
        "certifications": list(_as_list(candidate_profile.get("certifications", []))),
        "achievements": list(_as_list(candidate_profile.get("achievements", []))),
    }


def _normalize_job_description(job_description):
    """Return safe job description defaults without mutating the input."""
    if not isinstance(job_description, dict):
        job_description = {}
    return {
        "job_title": str(job_description.get("job_title", "") or ""),
        "required_skills": list(_as_list(job_description.get("required_skills", []))),
        "preferred_skills": list(_as_list(job_description.get("preferred_skills", []))),
        "responsibilities": list(_as_list(job_description.get("responsibilities", []))),
    }


def _flatten_resume_skills(final_resume_skills):
    """Flatten final resume skills from list or category dict form."""
    if isinstance(final_resume_skills, dict):
        flattened = []
        for key in sorted(final_resume_skills):
            flattened.extend(_flatten_resume_skills(final_resume_skills[key]))
        return _unique_preserve_order(flattened)
    flattened = []
    for item in _as_list(final_resume_skills):
        if isinstance(item, dict):
            flattened.extend(_flatten_resume_skills(item))
        elif isinstance(item, (list, tuple)):
            flattened.extend(_flatten_resume_skills(item))
        else:
            flattened.append(item)
    return _unique_preserve_order(flattened)


def _profile_fields_with_content(profile):
    fields = []
    for field in ("skills", "experience", "projects", "certifications", "achievements"):
        if _as_list(profile.get(field)):
            fields.append(field)
    return fields


def _entry_text(entry):
    if isinstance(entry, dict):
        return entry.get("text") or entry.get("title") or entry.get("name") or ""
    return entry


def _entry_skills(entry):
    if not isinstance(entry, dict):
        return []
    return _as_list(entry.get("skills", []))


def _candidate_skill_evidence(profile):
    skills = []
    sources = []
    if _as_list(profile.get("skills")):
        skills.extend(_as_list(profile.get("skills")))
        sources.append("reviewed_candidate_profile.skills")
    for entry in _as_list(profile.get("experience")):
        entry_skills = _entry_skills(entry)
        if entry_skills:
            skills.extend(entry_skills)
            if "reviewed_candidate_profile.experience.skills" not in sources:
                sources.append("reviewed_candidate_profile.experience.skills")
    return _unique_preserve_order(skills), sources


def _profile_snippets(profile, fields, limit=8):
    snippets = []
    for field in fields:
        for item in _as_list(profile.get(field)):
            text = _entry_text(item)
            if str(text).strip():
                snippets.append(_shorten(text))
            if len(snippets) >= limit:
                return snippets
    return snippets


def _base_trace(section, supported, support_level, evidence_sources=None, evidence_items=None, warnings=None):
    return {
        "section": section,
        "supported": supported,
        "support_level": support_level,
        "evidence_sources": evidence_sources or [],
        "evidence_items": evidence_items or [],
        "warnings": warnings or [],
    }


def _job_title_trace(job_description):
    job_title = str(job_description.get("job_title", "") or "").strip()
    if job_title:
        return _base_trace(
            "job_title",
            True,
            "derived_from_job_description",
            ["parsed_job_description.job_title"],
            [_shorten(job_title)],
        )
    return _base_trace(
        "job_title",
        False,
        "missing_evidence",
        warnings=["Job title source is missing from parsed job description."],
    )


def _professional_summary_trace(profile):
    fields = _profile_fields_with_content(profile)
    warnings = [
        "Section-level trace only; individual summary claims are not verified in this sprint."
    ]
    if not fields:
        return _base_trace(
            "professional_summary",
            False,
            "missing_evidence",
            warnings=warnings + ["No reviewed profile evidence exists for summary support."],
        )
    return _base_trace(
        "professional_summary",
        True,
        "section_level",
        [f"reviewed_candidate_profile.{field}" for field in fields],
        _profile_snippets(profile, fields),
        warnings,
    )


def _skills_trace(final_resume, profile):
    resume_skills = _flatten_resume_skills(final_resume.get("skills", []))
    candidate_skills = _unique_preserve_order(profile.get("skills", []))
    candidate_support_skills, evidence_sources = _candidate_skill_evidence(profile)
    supported_resume_skills = [
        skill
        for skill in resume_skills
        if any(
            skill_is_supported_by_candidate(skill, candidate_skill)
            for candidate_skill in candidate_support_skills
        )
    ]
    unsupported_resume_skills = [
        skill
        for skill in resume_skills
        if skill not in supported_resume_skills
    ]

    supported = bool(supported_resume_skills) or (not resume_skills and bool(candidate_skills))
    if supported_resume_skills:
        support_level = "direct"
    elif not resume_skills and candidate_skills:
        support_level = "section_level"
    else:
        support_level = "missing_evidence"
    warnings = []
    if unsupported_resume_skills:
        warnings.append(
            "Unsupported resume skills found in the final resume: "
            + ", ".join(unsupported_resume_skills)
        )

    trace = _base_trace(
        "skills",
        supported,
        support_level,
        evidence_sources,
        [_shorten(skill) for skill in candidate_support_skills[:8]],
        warnings,
    )
    trace["supported_resume_skills"] = supported_resume_skills
    trace["unsupported_resume_skills"] = unsupported_resume_skills
    trace["candidate_profile_skills"] = candidate_skills
    trace["candidate_support_skills"] = candidate_support_skills
    return trace


def _experience_bullets_trace(profile):
    experience_entries = _as_list(profile.get("experience", []))
    warnings = [
        "Section-level trace only; individual experience bullets are not verified in this sprint."
    ]
    evidence_items = [
        _shorten(_entry_text(entry))
        for entry in experience_entries
        if str(_entry_text(entry)).strip()
    ][:8]
    if experience_entries:
        return _base_trace(
            "experience_bullets",
            True,
            "section_level",
            ["reviewed_candidate_profile.experience"],
            evidence_items,
            warnings,
        )
    return _base_trace(
        "experience_bullets",
        False,
        "missing_evidence",
        warnings=warnings + ["No reviewed experience evidence exists."],
    )


def _metadata_note_trace():
    return _base_trace(
        "metadata_note",
        True,
        "not_applicable",
        warnings=[
            "This MVP trace shows section-level evidence only. Per-claim evidence trace is planned for a later sprint."
        ],
    )


def build_section_evidence_trace(final_resume, candidate_profile, job_description=None) -> dict:
    """Build a deterministic section-level evidence trace for real-flow analysis."""
    result = {
        "status": "success",
        "trace_level": "section",
        "per_claim_trace": False,
        "section_traces": {},
        "errors": [],
        "warnings": [],
        "metadata": {
            "source": "reviewed_candidate_profile_and_job_description",
            "candidate_profile_source": "reviewed_candidate_profile",
            "job_description_source": "parsed_job_description",
            "trace_level": "section",
            "per_claim_trace": False,
        },
    }

    if not isinstance(final_resume, dict) or not final_resume:
        result["status"] = "failed"
        result["errors"].append("final_resume is required for section evidence trace.")
        return result
    if not isinstance(candidate_profile, dict) or not candidate_profile:
        result["status"] = "failed"
        result["errors"].append("reviewed_candidate_profile is required for section evidence trace.")
        return result

    profile = _normalize_profile(candidate_profile)
    normalized_job = _normalize_job_description(job_description)
    result["section_traces"] = {
        "job_title": _job_title_trace(normalized_job),
        "professional_summary": _professional_summary_trace(profile),
        "skills": _skills_trace(final_resume, profile),
        "experience_bullets": _experience_bullets_trace(profile),
        "metadata_note": _metadata_note_trace(),
    }
    return result
