"""
Evidence Extractor

Purpose:
Convert profile data into Evidence objects for use in the Evidence Engine.
"""

from models.evidence import Evidence

_TEXT_FIELDS = ("text", "description", "summary", "title", "name", "role")

_SECTIONS = (
    ("experience", "EXP", "experience"),
    ("projects", "PRJ", "project"),
    ("certifications", "CERT", "certification"),
    ("achievements", "ACH", "achievement"),
)


def _extract_text(item: dict) -> str:
    """Return the first non-empty text field from a profile item."""
    for field in _TEXT_FIELDS:
        value = item.get(field)
        if value:
            return str(value).strip()
    return ""


def _make_source_id(item: dict, index: int) -> str:
    """Return the item's id field when present, otherwise its list index."""
    item_id = item.get("id")
    if item_id is not None and str(item_id).strip():
        return str(item_id)
    return str(index)


def extract_evidence(profile_data: dict) -> list[Evidence]:
    """Extract Evidence objects from experience, projects, certifications, and achievements."""
    evidence_list: list[Evidence] = []

    for section_key, id_prefix, source_type in _SECTIONS:
        items = profile_data.get(section_key, [])
        if not isinstance(items, list):
            continue

        counter = 0
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                continue

            text = _extract_text(item)
            if not text:
                continue

            counter += 1
            evidence_list.append(
                Evidence(
                    id=f"{id_prefix}{counter:03d}",
                    source_type=source_type,
                    source_id=_make_source_id(item, index),
                    category=source_type,
                    text=text,
                    skills=list(item.get("skills") or []),
                )
            )

    return evidence_list
