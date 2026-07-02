"""
Test Resume Text Extractor

Purpose:
Unit tests for deterministic DOCX resume text extraction.
"""

from pathlib import Path

from docx import Document

from engine.resume_text_extractor import extract_text_from_docx


def write_docx(path: Path, paragraphs: list[str] | None = None) -> None:
    """Create a small DOCX fixture."""
    document = Document()
    for paragraph in paragraphs or []:
        document.add_paragraph(paragraph)
    document.save(path)


def test_extracts_docx_paragraph_text(tmp_path) -> None:
    docx_path = tmp_path / "resume.docx"
    write_docx(
        docx_path,
        [
            "Sample Candidate",
            "Administrative Assistant",
            "Maintained Excel trackers and prepared reports.",
        ],
    )

    result = extract_text_from_docx(str(docx_path))

    assert result["status"] == "success"
    assert result["text"] == (
        "Sample Candidate\n"
        "Administrative Assistant\n"
        "Maintained Excel trackers and prepared reports."
    )
    assert result["errors"] == []
    assert result["warnings"] == []


def test_extracts_docx_table_text(tmp_path) -> None:
    docx_path = tmp_path / "resume.docx"
    document = Document()
    document.add_paragraph("Sample Candidate")
    table = document.add_table(rows=2, cols=2)
    table.cell(0, 0).text = "Skills"
    table.cell(0, 1).text = "Microsoft Excel"
    table.cell(1, 0).text = "Experience"
    table.cell(1, 1).text = "Coordinated office documentation"
    document.save(docx_path)

    result = extract_text_from_docx(str(docx_path))

    assert result["status"] == "success"
    assert result["text"].splitlines() == [
        "Sample Candidate",
        "Skills",
        "Microsoft Excel",
        "Experience",
        "Coordinated office documentation",
    ]


def test_return_shape_contains_status_text_errors_warnings_metadata(tmp_path) -> None:
    docx_path = tmp_path / "resume.docx"
    write_docx(docx_path, ["Sample Candidate"])

    result = extract_text_from_docx(str(docx_path))

    assert set(result) == {"status", "text", "errors", "warnings", "metadata"}
    assert set(result["metadata"]) == {"extractor", "version", "source"}


def test_omits_empty_paragraphs_and_cells(tmp_path) -> None:
    docx_path = tmp_path / "resume.docx"
    document = Document()
    document.add_paragraph("Sample Candidate")
    document.add_paragraph("")
    table = document.add_table(rows=1, cols=2)
    table.cell(0, 0).text = ""
    table.cell(0, 1).text = "Reporting"
    document.save(docx_path)

    result = extract_text_from_docx(str(docx_path))

    assert result["text"].splitlines() == ["Sample Candidate", "Reporting"]


def test_normalizes_internal_whitespace(tmp_path) -> None:
    docx_path = tmp_path / "resume.docx"
    write_docx(docx_path, ["  Managed\t schedules   and\u00a0reports  "])

    result = extract_text_from_docx(str(docx_path))

    assert result["text"] == "Managed schedules and reports"


def test_non_string_file_path_returns_failed() -> None:
    result = extract_text_from_docx(Path("resume.docx"))

    assert result["status"] == "failed"
    assert result["text"] == ""
    assert result["errors"] == ["file_path must be a string."]
    assert result["warnings"] == []


def test_empty_file_path_returns_failed() -> None:
    result = extract_text_from_docx("")

    assert result["status"] == "failed"
    assert result["errors"] == ["file_path must be a non-empty string."]


def test_non_docx_extension_returns_failed(tmp_path) -> None:
    text_path = tmp_path / "resume.txt"
    text_path.write_text("Sample Candidate", encoding="utf-8")

    result = extract_text_from_docx(str(text_path))

    assert result["status"] == "failed"
    assert result["errors"] == ["file_path must point to a .docx file."]


def test_missing_docx_file_returns_failed(tmp_path) -> None:
    result = extract_text_from_docx(str(tmp_path / "missing.docx"))

    assert result["status"] == "failed"
    assert result["errors"] == ["file_path file does not exist."]


def test_directory_path_returns_failed(tmp_path) -> None:
    directory_path = tmp_path / "resume.docx"
    directory_path.mkdir()

    result = extract_text_from_docx(str(directory_path))

    assert result["status"] == "failed"
    assert result["errors"] == ["file_path must point to a file."]


def test_empty_docx_returns_failed(tmp_path) -> None:
    docx_path = tmp_path / "empty.docx"
    write_docx(docx_path)

    result = extract_text_from_docx(str(docx_path))

    assert result["status"] == "failed"
    assert result["errors"] == ["DOCX contains no extractable text."]


def test_corrupt_docx_returns_failed_with_clear_error(tmp_path) -> None:
    docx_path = tmp_path / "corrupt.docx"
    docx_path.write_text("not a real docx", encoding="utf-8")

    result = extract_text_from_docx(str(docx_path))

    assert result["status"] == "failed"
    assert result["errors"][0].startswith("DOCX text extraction failed:")
