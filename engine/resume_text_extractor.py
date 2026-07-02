"""
Resume Text Extractor

Purpose:
Extract deterministic readable text from DOCX resumes without interpreting,
enriching, or inventing candidate claims.
"""

from pathlib import Path

from docx import Document
from docx.document import Document as DocumentObject
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table
from docx.text.paragraph import Paragraph


EXTRACTOR_METADATA = {
    "extractor": "resume_text_extractor",
    "version": "v1",
    "source": "uploaded_docx",
}


def _result(status: str, text: str = "", errors: list[str] | None = None) -> dict:
    """Return the resume text extractor result shape."""
    return {
        "status": status,
        "text": text,
        "errors": errors or [],
        "warnings": [],
        "metadata": EXTRACTOR_METADATA.copy(),
    }


def _normalize_text(text: str) -> str:
    """Normalize Word spacing while preserving extracted wording."""
    return " ".join(str(text).replace("\xa0", " ").split())


def _iter_document_blocks(document: DocumentObject):
    """Yield top-level paragraphs and tables in document order."""
    for child in document.element.body.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, document)
        elif isinstance(child, CT_Tbl):
            yield Table(child, document)


def _extract_table_text(table: Table) -> list[str]:
    """Extract normalized text from table cells in row order."""
    lines: list[str] = []
    for row in table.rows:
        for cell in row.cells:
            text = _normalize_text(cell.text)
            if text:
                lines.append(text)
    return lines


def _extract_document_text(document: DocumentObject) -> str:
    """Extract normalized document text from paragraphs and tables."""
    lines: list[str] = []
    for block in _iter_document_blocks(document):
        if isinstance(block, Paragraph):
            text = _normalize_text(block.text)
            if text:
                lines.append(text)
        elif isinstance(block, Table):
            lines.extend(_extract_table_text(block))
    return "\n".join(lines)


def _validate_file_path(file_path: str) -> list[str]:
    """Validate the DOCX file path without repairing it."""
    if not isinstance(file_path, str):
        return ["file_path must be a string."]

    if not file_path:
        return ["file_path must be a non-empty string."]

    path = Path(file_path)
    if path.suffix.lower() != ".docx":
        return ["file_path must point to a .docx file."]
    if not path.exists():
        return ["file_path file does not exist."]
    if not path.is_file():
        return ["file_path must point to a file."]

    return []


def extract_text_from_docx(file_path: str) -> dict:
    """Extract readable text from DOCX paragraphs and tables."""
    validation_errors = _validate_file_path(file_path)
    if validation_errors:
        return _result("failed", errors=validation_errors)

    try:
        document = Document(file_path)
        text = _extract_document_text(document)
    except Exception as error:
        return _result("failed", errors=[f"DOCX text extraction failed: {error}"])

    if not text:
        return _result("failed", errors=["DOCX contains no extractable text."])

    return _result("success", text=text)
