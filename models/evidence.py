"""
Evidence Model

Purpose:
Defines the structure of a single evidence item extracted from a candidate
profile or source document for use in the Evidence Engine.
"""

from dataclasses import asdict, dataclass


@dataclass
class Evidence:
    """A single verifiable evidence item linked to a profile source."""

    id: str
    source_type: str
    source_id: str
    category: str
    text: str
    skills: list[str]
    confidence: float = 1.0

    def to_dict(self) -> dict:
        """Return a plain dictionary representation of this evidence item."""
        return asdict(self)
