"""Render staged DOCX documents locally for internal page-by-page layout review.

The packaged LibreOffice renderer is unavailable on this Windows host. This
fallback uses an isolated Aspose evaluation installation to render PDFs, then
the bundled PDFium library to produce PNGs. Evaluation banners occur only in
the QA intermediates; the final DOCX files are never saved through Aspose.
"""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import re
import sys
import unicodedata
from copy import deepcopy, copy
from zipfile import ZipFile
import xml.etree.ElementTree as ET

from docx import Document
from pypdf import PdfReader
import pypdfium2 as pdfium

BUILD = Path(__file__).resolve().parent
ROOT = BUILD.parent
sys.path.insert(0, str(BUILD / "render_dependencies"))
import aspose.words as aw


def tokens(text: str) -> list[str]:
    """Normalize text into tokens for detecting rendering truncation.

    Args:
        text: Source or PDF text.
    Returns:
        Lowercase alphanumeric tokens after Unicode normalization.
    """
    normalized = unicodedata.normalize("NFKC", text).lower()
    return re.findall(r"\w+", normalized)


def source_text(path: Path) -> str:
    """Extract body and table text from a source DOCX without changing it.

    Args:
        path: Source document path.
    Returns:
        Source text joined by spaces.
    """
    doc = Document(path)
    pieces = [paragraph.text for paragraph in doc.paragraphs]
    for table in doc.tables:
        pieces.extend(cell.text for row in table.rows for cell in row.cells)
    return " ".join(pieces)


def render_piece(path: Path, directory: Path, start_page: int = 1) -> dict[str, object]:
    """Render one DOCX, rasterize every page, and compare textual coverage.

    Args:
        path: Staged Word document or an explicitly paginated chapter.
        directory: Internal QA output directory.
        start_page: First PNG number for assembling chapter previews.
    Returns:
        Rendering manifest entry including page count and coverage.
    Raises:
        ValueError: If the evaluation renderer truncates substantial content.
        OSError: If files cannot be read or written.
    """
    directory.mkdir(parents=True, exist_ok=True)
    pdf_path = directory / f"{path.stem}.pdf"
    aw.Document(str(path)).save(str(pdf_path))
    reader = PdfReader(pdf_path)
    text = " ".join(page.extract_text() or "" for page in reader.pages)
    expected, actual = Counter(tokens(source_text(path))), Counter(tokens(text))
    missing = expected - actual
    coverage = 1 - sum(missing.values()) / sum(expected.values())
    if "document was truncated" in text.lower() or coverage < 0.985:
        raise ValueError(f"Renderer text coverage insufficient for {path.name}: {coverage:.3%}; {missing}")
    pdf = pdfium.PdfDocument(pdf_path)
    for index in range(len(pdf)):
        page = pdf[index]
        bitmap = page.render(scale=1.8)
        bitmap.to_pil().save(directory / f"page-{index + start_page}.png")
        bitmap.close()
        page.close()
    count = len(pdf)
    pdf.close()
    return {"file": path.name, "pages": count, "text_coverage": coverage,
            "minor_token_differences": dict(missing), "qa_directory": str(directory),
            "renderer": "Aspose evaluation QA only; final DOCX unchanged"}


def chapter_copies(path: Path, directory: Path) -> list[Path]:
    """Copy the explicitly paginated chapters into independent QA documents.

    Args:
        path: Final DOCX whose domain/table chapters start on new pages.
        directory: Internal chapter-copy output directory.
    Returns:
        Ordered paths to unchanged chapter content with original styles.
    Raises:
        ValueError: If the OOXML body or section definition is absent.
    """
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    tag = "{" + ns["w"] + "}"
    with ZipFile(path) as archive:
        xml = ET.fromstring(archive.read("word/document.xml"))
        body = xml.find("w:body", ns)
        if body is None:
            raise ValueError("Missing document body")
        section = body.find("w:sectPr", ns)
        groups: list[list[ET.Element]] = [[]]
        for child in body:
            if child.tag == tag + "sectPr":
                continue
            breaks = child.findall('.//w:br[@w:type="page"]', ns)
            if breaks:
                groups.append([])
            else:
                groups[-1].append(deepcopy(child))
        paths = []
        for index, group in enumerate(groups, 1):
            copied = deepcopy(xml)
            copied_body = copied.find("w:body", ns)
            copied_body.clear()
            copied_body.extend(group)
            copied_body.append(deepcopy(section))
            target = directory / f"chapter-{index}.docx"
            write_chapter(archive, copied, target)
            paths.append(target)
    return paths


def write_chapter(archive: ZipFile, xml: ET.Element, target: Path) -> None:
    """Write a QA-only chapter while preserving package styles and relationships.

    Args:
        archive: Open original OOXML package.
        xml: Chapter document XML.
        target: QA DOCX path.
    Returns:
        None. Writes a temporary chapter copy without changing the original.
    """
    with ZipFile(target, "w") as destination:
        for info in archive.infolist():
            data = ET.tostring(xml, encoding="utf-8", xml_declaration=True) if info.filename == "word/document.xml" else archive.read(info.filename)
            destination.writestr(copy(info), data)


def render_one(path: Path) -> dict[str, object]:
    """Render the full document or each explicitly paginated table/domain chapter.

    Args:
        path: Final staged DOCX path.
    Returns:
        Manifest with all reviewed pages and text coverage.
    Raises:
        ValueError or OSError: If rendering, chapter copying or coverage fails.
    """
    number = path.name.split(".")[0]
    directory = BUILD / "qa" / number
    directory.mkdir(parents=True, exist_ok=True)
    if number not in ("3", "7"):
        return render_piece(path, directory)
    page = 1
    pieces = []
    for chapter in chapter_copies(path, directory):
        result = render_piece(chapter, directory, page)
        page += int(result["pages"])
        pieces.append(result)
    return {"file": path.name, "pages": page - 1, "chapters": pieces,
            "qa_directory": str(directory), "mode": "Explicit page-break chapters rendered separately; native Word pagination not independently checked"}


def main() -> None:
    """Render all staged documents and save a QA manifest.

    Returns:
        None. Writes internal PDFs, page PNGs and render_manifest.json.
    Raises:
        ValueError or OSError: If rendering or coverage verification fails.
    """
    report = []
    for path in sorted((ROOT / "KeraNova_Submission").glob("*.docx")):
        entry = render_one(path)
        report.append(entry)
        print(json.dumps(entry), flush=True)
    (BUILD / "render_manifest.json").write_text(json.dumps(report, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
