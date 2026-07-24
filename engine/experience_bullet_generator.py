"""
Experience Bullet Generator

Purpose:
Generate deterministic, evidence-safe experience bullets from Evidence objects.
"""

import re


NO_EXPERIENCE_EVIDENCE_ERROR = "No experience evidence found. Cannot generate bullets."
MAX_BULLETS = 5
MIN_BULLET_CHARACTERS = 25
MIN_BULLET_WORDS = 5
ABBREVIATION_SUFFIXES = (
    "U.S.",
    "U.A.E.",
    "U.K.",
    "e.g.",
    "i.e.",
)


def _empty_ai_output() -> dict:
    """Return the empty AI Generation Contract schema for Sprint 18."""
    return {
        "summary": "",
        "experience_bullets": [],
        "skills": {
            "technical": [],
            "soft": [],
            "domain": [],
        },
    }


def _failed_output(provider: str) -> dict:
    """Return failed wrapper output when no usable experience evidence exists."""
    return {
        "status": "failed",
        "errors": [NO_EXPERIENCE_EVIDENCE_ERROR],
        "provider": provider,
        "mode": "deterministic",
        "ai_output": _empty_ai_output(),
    }


def _success_output(provider: str, bullets: list[dict]) -> dict:
    """Return successful wrapper output with generated bullets."""
    ai_output = _empty_ai_output()
    ai_output["experience_bullets"] = bullets

    return {
        "status": "success",
        "errors": [],
        "provider": provider,
        "mode": "deterministic",
        "ai_output": ai_output,
    }


def _is_usable_experience_evidence(evidence) -> bool:
    """Return whether an Evidence item can be used for bullet generation."""
    evidence_id = getattr(evidence, "id", "")
    evidence_text = getattr(evidence, "text", "")
    evidence_category = getattr(evidence, "category", "")

    return (
        bool(str(evidence_id).strip())
        and bool(str(evidence_text).strip())
        and str(evidence_category).strip().casefold() == "experience"
    )


def _select_experience_evidence(evidence_items: list) -> list:
    """Return the first five usable experience Evidence items in list order."""
    selected_evidence = []
    for evidence in evidence_items:
        if _is_usable_experience_evidence(evidence):
            selected_evidence.append(evidence)
        if len(selected_evidence) == MAX_BULLETS:
            break
    return selected_evidence


def _has_minimum_content(candidate: str) -> bool:
    """Return whether a direct evidence substring is usable as a bullet."""
    stripped_candidate = candidate.strip()
    return (
        len(stripped_candidate) >= MIN_BULLET_CHARACTERS
        and len(stripped_candidate.split()) >= MIN_BULLET_WORDS
    )


def _line_candidates(text: str) -> list[str]:
    """Return line candidates from the original evidence text."""
    if "\n" not in text and "\r" not in text:
        return []
    return re.split(r"\r?\n+", text)


def _is_sentence_boundary(text: str, index: int) -> bool:
    """Return whether punctuation at index is a safe sentence boundary."""
    if text[index] not in ".!?":
        return False
    if index + 1 >= len(text) or not text[index + 1].isspace():
        return False
    prefix = text[: index + 1]
    return not any(prefix.endswith(abbreviation) for abbreviation in ABBREVIATION_SUFFIXES)


def _sentence_candidates(text: str) -> list[str]:
    """Return sentence candidates as direct slices from evidence text."""
    candidates = []
    start = 0
    for index, _character in enumerate(text):
        if not _is_sentence_boundary(text, index):
            continue
        candidates.append(text[start : index + 1])
        start = index + 1
        while start < len(text) and text[start].isspace():
            start += 1
    if start < len(text):
        candidates.append(text[start:])
    return candidates


def _first_usable_candidate(candidates: list[str]) -> str:
    """Return the first candidate that satisfies bullet minimums."""
    for candidate in candidates:
        stripped_candidate = candidate.strip()
        if stripped_candidate and _has_minimum_content(stripped_candidate):
            return stripped_candidate
    return ""


def _select_bullet_text(raw_text: str) -> str:
    """Select a safe direct-substring bullet from evidence text."""
    line_candidate = _first_usable_candidate(_line_candidates(raw_text))
    if line_candidate:
        return line_candidate

    sentence_candidate = _first_usable_candidate(_sentence_candidates(raw_text))
    if sentence_candidate:
        return sentence_candidate

    return raw_text.strip()


def _build_bullet(evidence) -> dict:
    """Build one deterministic bullet from Evidence text and id."""
    raw_text = str(evidence.text)
    return {
        "text": _select_bullet_text(raw_text),
        "source_evidence_id": str(evidence.id),
    }


def _build_deterministic_bullets(evidence_items: list) -> list[dict]:
    """Build deterministic bullets from selected experience Evidence items."""
    return [_build_bullet(evidence) for evidence in evidence_items]


def _generate_with_gemini(evidence_items: list) -> list[dict]:
    """Sprint 18 Gemini path using deterministic bullet generation only."""
    selected_evidence = _select_experience_evidence(evidence_items)
    return _build_deterministic_bullets(selected_evidence)


def generate_experience_bullets(
    evidence_items: list,
    provider: str = "gemini",
) -> dict:
    """Generate deterministic experience bullets from Evidence objects."""
    if provider != "gemini":
        raise ValueError(f"Unsupported provider: {provider}")

    if not evidence_items:
        return _failed_output(provider)

    bullets = _generate_with_gemini(evidence_items)
    if not bullets:
        return _failed_output(provider)

    return _success_output(provider, bullets)
