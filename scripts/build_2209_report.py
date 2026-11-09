#!/usr/bin/env python3
"""Fill the supplied result-report Word template from the current-stage report.

The source template is kept byte-for-byte. Its VML cover, general-information
table, numbered body labels and signature table are edited in a loaded copy.
PDF export requires LibreOffice. No portal submission or approval is performed.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
from zipfile import ZipFile

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt
from docx.text.paragraph import Paragraph

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "docs/basvuru/2209a"
STEM = "2209A_Burak_Sanli_Proje_Raporu"
TEMPLATE = DIRECTORY / "sablon/2209-a_sonuc_raporu_formati.docx"
BODY_LABELS = ["Giriş", "Proje konusu hakkında kısa bilgi",
               "Rapor dönemlerinde yapılan çalışmalar", "Sonuç",
               "Çıktılar (Yayınlar,sunumlar v.b.)",
               "Proje ile ilgili harcama kalemleri hakkında ayrıntılı bilgi"]
V = "urn:schemas-microsoft-com:vml"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clean(text):
    return re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", text).replace("**", "").replace("`", "")


def read_source(source):
    """The metadata table and six exact template anchors are authoritative."""
    metadata, parts, key = {}, {}, None
    for line in source.splitlines():
        if line.startswith("# ") and line[2:] in BODY_LABELS:
            key = line[2:]
            if key in parts:
                raise ValueError(f"Duplicate report section: {key}")
            parts[key] = []
        elif key:
            # Signature completion is an explicit, separate administrative note.
            if line == "## İmza alanları":
                break
            parts[key].append(line)
        elif line.startswith("|"):
            cells = [c.strip() for c in line.strip("|").split("|")]
            if len(cells) == 2 and cells[0] not in ("Alan", "---"):
                metadata[cells[0]] = cells[1]
    if list(parts) != BODY_LABELS or any(not "".join(p).strip() for p in parts.values()):
        raise ValueError("The report must fill every supplied template section in order")
    required = ["Projenin konusu", "Proje yürütücüsü", "Danışman",
                "Proje başlangıç ve bitiş tarihleri", "Rapor kapsam tarihi"]
    if not all(metadata.get(k) for k in required):
        raise ValueError("Missing template field values in Markdown metadata")
    return metadata, parts


def format_text(paragraph, text, *, size=11, bold=False):
    paragraph.text = text
    paragraph.paragraph_format.space_after = Pt(6)
    paragraph.paragraph_format.line_spacing = 1.10
    for run in paragraph.runs:
        run.font.name, run.font.size, run.bold = "Arial", Pt(size), bold


def fill_cover(document, metadata):
    """Keep the original framed VML shape; fill and reflow its text box."""
    boxes = document._element.xpath("//*[local-name()='txbxContent']")
    if len(boxes) != 1:
        raise ValueError("Expected the uploaded template's single cover text box")
    box = boxes[0]
    # Original empty paragraphs push the advisor label below the frame. Replace
    # the internal text layout, preserving the actual shape, border and anchor.
    for child in list(box):
        box.remove(child)
    cover = [
        ("2209/A", 16, False, 110, 24, "center"),
        ("ÜNİVERSİTE ÖĞRENCİLERİ ARAŞTIRMA PROJELERİ DESTEK PROGRAMI",
         15, False, 0, 26, "center"),
        ("SONUÇ RAPORU", 16, True, 0, 16, "center"),
        (f"Mevcut çalışma aşaması · {metadata['Rapor kapsam tarihi']}",
         10, False, 0, 48, "center"),
        ("PROJE BAŞLIĞI:", 11, True, 0, 8, "left"),
        (metadata["Projenin konusu"], 13, True, 0, 28, "left"),
        ("PROJE YÜRÜTÜCÜSÜNÜN ADI:", 11, True, 0, 6, "left"),
        (metadata["Proje yürütücüsü"], 12, False, 0, 22, "left"),
        ("DANIŞMANININ ADI:", 11, True, 0, 6, "left"),
        (metadata["Danışman"], 12, False, 0, 24, "left"),
        (metadata["Üniversite / bölüm"], 10, False, 0, 8, "center"),
        ("Rapor, gerçekleşen çalışmaları ve planlanan faaliyetleri ayrı açıklar.",
         9, False, 0, 0, "center"),
    ]
    for text, size, bold, before, after, alignment in cover:
        element = OxmlElement("w:p")
        box.append(element)
        paragraph = Paragraph(element, document._body)
        format_text(paragraph, text, size=size, bold=bold)
        paragraph.alignment = (WD_ALIGN_PARAGRAPH.CENTER if alignment == "center"
                               else WD_ALIGN_PARAGRAPH.LEFT)
        pf = paragraph.paragraph_format
        pf.left_indent = pf.right_indent = Cm(0.6)
        pf.space_before, pf.space_after = Pt(before), Pt(after)
        pf.line_spacing = 1.05
    # Remove the unrelated stray text outside the cover, without clearing the
    # paragraph that also holds the VML object, page break and general heading.
    for run in document.paragraphs[0].runs:
        if run.text == "ÜNÜ":
            run._r.getparent().remove(run._r)


def format_template_table(table):
    for row in table.rows:
        no_split = OxmlElement("w:cantSplit")
        row._tr.get_or_add_trPr().append(no_split)
        for cell in row.cells:
            for paragraph in cell.paragraphs:
                paragraph.paragraph_format.space_after = Pt(4)
                paragraph.paragraph_format.line_spacing = 1.05
                for run in paragraph.runs:
                    run.font.name, run.font.size = "Arial", Pt(10)


def append_table(document, rows):
    count = len(rows[0])
    widths = {3: [3.6, 6.2, 6.2], 4: [4.0, 6.0, 3.0, 3.0],
              5: [1.4, 2.4, 5.0, 3.6, 3.6]}.get(count, [16 / count] * count)
    table = document.add_table(rows=1, cols=count)
    # The uploaded Turkish template has no English 'Table Grid' style.
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        border = OxmlElement(f"w:{edge}")
        border.set(qn("w:val"), "single")
        border.set(qn("w:sz"), "4")
        border.set(qn("w:color"), "666666")
        borders.append(border)
    table._tbl.tblPr.append(borders)
    table.autofit = False
    for column, width in zip(table.columns, widths):
        column.width = Cm(width)
    for index, values in enumerate(rows):
        if len(values) != count:
            raise ValueError("Inconsistent Markdown table")
        row = table.rows[0] if index == 0 else table.add_row()
        no_split = OxmlElement("w:cantSplit")
        row._tr.get_or_add_trPr().append(no_split)
        for cell, value, width in zip(row.cells, values, widths):
            cell.width = Cm(width)
            format_text(cell.paragraphs[0], clean(value), size=9, bold=index == 0)
            cell.paragraphs[0].paragraph_format.space_after = Pt(3)
            cell.paragraphs[0].paragraph_format.line_spacing = 1.05
        if index == 0:
            repeat = OxmlElement("w:tblHeader")
            row._tr.get_or_add_trPr().append(repeat)
    return table._tbl


def insert_markdown(document, anchor, lines):
    """Insert rendered content after an existing template paragraph."""
    cursor = anchor._p
    pending = []

    def move(element):
        nonlocal cursor
        cursor.addnext(element)
        cursor = element

    def paragraph(text, heading=False):
        p = document.add_paragraph()
        format_text(p, clean(text), size=11 if not heading else 11.5, bold=heading)
        if heading:
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.keep_with_next = True
        move(p._p)

    def flush():
        if pending:
            paragraph(" ".join(pending))
            pending.clear()

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            flush()
        elif line.startswith("|"):
            flush()
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            move(append_table(document, rows))
            continue
        elif line.startswith("!["):
            flush()
            match = re.fullmatch(r"!\[([^]]*)\]\(([^)]+)\)", line)
            if not match:
                raise ValueError("Invalid image markup")
            path = (DIRECTORY / match[2]).resolve()
            if not path.is_relative_to(DIRECTORY):
                raise ValueError("Figure path outside the report directory")
            p = document.add_paragraph()
            p.add_run().add_picture(str(path), width=Cm(15.8))
            p.paragraph_format.keep_with_next = True
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            move(p._p)
        elif line.startswith("## "):
            flush()
            paragraph(line[3:], heading=True)
        else:
            pending.append(line)
        i += 1
    flush()


def build_word(metadata, parts, destination):
    document = Document(TEMPLATE)
    original_tables = list(document.tables)
    original_paragraphs = list(document.paragraphs)
    anchors = {}
    for paragraph in original_paragraphs:
        label = paragraph.text.strip().rstrip(":").strip()
        if label in BODY_LABELS:
            anchors[label] = paragraph
    if set(anchors) != set(BODY_LABELS):
        raise ValueError("The supplied template anchors have changed")

    normal = document.styles["Normal"]
    normal.font.name, normal.font.size = "Arial", Pt(11)
    normal.paragraph_format.line_spacing = 1.10
    normal.paragraph_format.space_after = Pt(6)
    fill_cover(document, metadata)
    information, signatures = original_tables
    values = [metadata["Projenin konusu"], metadata["Proje yürütücüsü"],
              metadata["Danışman"], metadata["Proje başlangıç ve bitiş tarihleri"]]
    for row, value in zip(information.rows, values):
        row.cells[1].text = value
    format_template_table(information)

    # Keep the original section labels and their automatic numbering. The
    # 'Proje konusu...' sentence is the template's subprompt under Giriş.
    for label, paragraph in anchors.items():
        pf = paragraph.paragraph_format
        pf.keep_with_next = True
        pf.space_before, pf.space_after = Pt(12), Pt(6)
        if label == "Proje konusu hakkında kısa bilgi":
            pf.left_indent = Cm(0)
        for run in paragraph.runs:
            run.font.name, run.font.size, run.bold = "Arial", Pt(11.5), True
        insert_markdown(document, paragraph, parts[label])

    signatures.cell(1, 0).text = metadata["Proje yürütücüsü"]
    signatures.cell(1, 1).text = metadata["Danışman"]
    # Third row is an intentionally blank signature space, not a typed sign-off.
    for cell in signatures.rows[2].cells:
        cell.text = "\n\n"
    format_template_table(signatures)
    before = document.add_paragraph()
    format_text(before, "İmza alanları — Henüz imzalanmamıştır.", size=10)
    before.paragraph_format.keep_with_next = True
    signatures._tbl.addprevious(before._p)
    for row in signatures.rows[:-1]:
        for cell in row.cells:
            for p in cell.paragraphs:
                p.paragraph_format.keep_with_next = True

    # Only remove empty filler paragraphs; preserve the date and all anchors.
    for paragraph in original_paragraphs[1:]:
        if not paragraph.text.strip():
            paragraph._p.getparent().remove(paragraph._p)
        elif paragraph.text.strip() == "Tarih :":
            format_text(paragraph, "Tarih : ____________________  (İmza tarihi)", size=10)

    props = document.core_properties
    props.title = "CPU Zamanlama — 2209-A Biçiminde Proje Raporu"
    props.subject = f"Mevcut çalışma aşaması — {metadata['Rapor kapsam tarihi']}"
    props.author = metadata["Proje yürütücüsü"]
    props.keywords = "CPU zamanlama; mevcut durum; sonuç raporu şablonu"
    props.comments = "Kullanıcı tarafından sağlanan Word şablonu doldurulmuştur."
    props.modified = datetime(2026, 11, 9, tzinfo=timezone.utc)
    document.save(destination)


def inspect_word(path, metadata):
    original, report = Document(TEMPLATE), Document(path)
    body = [p.text.strip().rstrip(":").strip() for p in report.paragraphs]
    indices = [body.index(label) for label in BODY_LABELS]
    if indices != sorted(indices):
        raise ValueError("Template headings missing or out of order")
    numbered = [p for p in report.paragraphs if p._p.pPr is not None
                and p._p.pPr.find(qn("w:numPr")) is not None]
    if len(numbered) != 5:
        raise ValueError("The template's five numbered sections were not preserved")
    for a, b in zip(original.sections, report.sections):
        if (a.page_width, a.page_height, a.top_margin, a.bottom_margin,
            a.left_margin, a.right_margin) != (b.page_width, b.page_height,
            b.top_margin, b.bottom_margin, b.left_margin, b.right_margin):
            raise ValueError("Template page geometry changed")
    information, signatures = report.tables[0], report.tables[-1]
    if [r.cells[0].text for r in information.rows] != [r.cells[0].text for r in original.tables[0].rows]:
        raise ValueError("Original general-information table labels changed")
    if [c.text for c in signatures.rows[0].cells] != [c.text for c in original.tables[1].rows[0].cells]:
        raise ValueError("Original signature table labels changed")
    if any(c.text.strip() for c in signatures.rows[2].cells):
        raise ValueError("Signature spaces must be blank")
    if "henüz kesinleşmedi" not in information.cell(3, 1).text:
        raise ValueError("Unknown official project dates have been substituted")
    cover = "\n".join(report._element.xpath("//*[local-name()='txbxContent']//*[local-name()='t']/text()"))
    for key in ("Projenin konusu", "Proje yürütücüsü", "Danışman", "Rapor kapsam tarihi"):
        if metadata[key] not in cover:
            raise ValueError(f"Cover field not filled: {key}")
    with ZipFile(path) as archive:
        if archive.testzip() is not None:
            raise ValueError("Invalid Word archive")
    query = f"//*[local-name()='shape' and namespace-uri()='{V}']"
    old_shapes = original._element.xpath(query)
    new_shapes = report._element.xpath(query)
    if len(old_shapes) != 1 or len(new_shapes) != 1 or dict(old_shapes[0].attrib) != dict(new_shapes[0].attrib):
        raise ValueError("Original framed VML cover was not preserved")
    if len(report.inline_shapes) != 2:
        raise ValueError("Missing model figures")
    text = "\n".join(body)
    if "bildirilen toplam gider 0 TL" not in text or "henüz tamamlanmamıştır" not in text:
        raise ValueError("Missing actual-stage or actual-expenditure statement")
    return {
        "checked_artifact": path.name,
        "template": str(TEMPLATE.relative_to(ROOT)),
        "template_sha256": digest(TEMPLATE),
        "required_body_labels_in_order": BODY_LABELS,
        "numbered_template_sections": len(numbered),
        "original_information_and_signature_labels_preserved": True,
        "original_framed_vml_cover_preserved_and_filled": True,
        "template_page_geometry_preserved": True,
        "body_tables_including_original_two": len(report.tables),
        "embedded_model_figures": len(report.inline_shapes),
        "report_scope_date": "2026-11-09",
        "official_project_start_date": None,
        "official_project_end_date": None,
        "signatures_and_signature_date_completed": False,
        "reported_actual_expenditure_try": 0,
        "expenditure_basis": "Yürütücünün harcama olmadığına ilişkin beyanı",
        "project_completed": False,
        "portal_submission_verified": False,
        "advisor_approval_verified": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", action="store_true", help="also export PDF using LibreOffice")
    arguments = parser.parse_args()
    source = DIRECTORY / f"{STEM}.md"
    metadata, parts = read_source(source.read_text())
    word = DIRECTORY / f"{STEM}.docx"
    template_hash = digest(TEMPLATE)
    build_word(metadata, parts, word)
    result = inspect_word(word, metadata)
    result["pdf_regenerated_in_this_build"] = arguments.pdf
    if arguments.pdf:
        program = shutil.which("soffice") or shutil.which("libreoffice")
        if not program:
            raise RuntimeError("LibreOffice is required for PDF export")
        with tempfile.TemporaryDirectory(prefix="2209-report-", dir="/tmp") as directory:
            directory = Path(directory)
            rendered = directory / "rendered"
            rendered.mkdir()
            profile = directory / "profile"
            subprocess.run([program, f"-env:UserInstallation={profile.as_uri()}",
                            "--headless", "--convert-to", "pdf", "--outdir", str(rendered),
                            str(word)], check=True)
            exported = rendered / f"{STEM}.pdf"
            if not exported.is_file() or not exported.stat().st_size:
                raise RuntimeError("No fresh PDF was produced")
            shutil.copyfile(exported, DIRECTORY / exported.name)
    if digest(TEMPLATE) != template_hash:
        raise ValueError("The uploaded source template was modified")
    inputs = [source, word, DIRECTORY / f"{STEM}.pdf", TEMPLATE,
              DIRECTORY / "ekler/ek1_karisik_model.png",
              DIRECTORY / "ekler/ek2_yogun_etkilesimli_model.png"]
    result["sha256"] = {str(p.relative_to(DIRECTORY)): digest(p) for p in inputs if p.exists()}
    (DIRECTORY / "rapor_kontrolu.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
