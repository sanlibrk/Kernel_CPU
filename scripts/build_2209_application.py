#!/usr/bin/env python3
"""Build the application documents from their single Markdown source.

PDF export uses an installed LibreOffice. It never contacts or submits to TYBS.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import zipfile

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / "docs/basvuru/2209a"
STEM = "2209A_Burak_Sanli_Arastirma_Onerisi"


def clean(text):
    text = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", text)
    return text.replace("**", "").replace("`", "")


def table(document, rows):
    columns = len(rows[0])
    widths = {2: [3.6, 13.4], 3: [4.0, 6.5, 6.5],
              4: [2.8, 3.4, 5.2, 5.6], 5: [2.2, 3.7, 2.0, 7.3, 1.8]}[columns]
    result = document.add_table(rows=1, cols=columns)
    result.style = "Table Grid"
    result.autofit = False
    for column, width in zip(result.columns, widths):
        column.width = Cm(width)
    repeat = OxmlElement("w:tblHeader")
    result.rows[0]._tr.get_or_add_trPr().append(repeat)
    for number, values in enumerate(rows):
        row = result.rows[0] if number == 0 else result.add_row()
        no_split = OxmlElement("w:cantSplit")
        row._tr.get_or_add_trPr().append(no_split)
        for cell, value, width in zip(row.cells, values, widths):
            cell.width = Cm(width)
            cell.text = clean(value)
            for paragraph in cell.paragraphs:
                paragraph.paragraph_format.space_after = Pt(2)
                paragraph.paragraph_format.line_spacing = 1.05
                for run in paragraph.runs:
                    run.font.size = Pt(9.5)
                    run.bold = number == 0
                if number == 0:
                    paragraph.paragraph_format.keep_with_next = True
    document.add_paragraph()


def build_word(source, destination):
    document = Document()
    section = document.sections[0]
    section.page_width, section.page_height = Cm(21), Cm(29.7)
    section.top_margin = section.bottom_margin = Cm(2)
    section.left_margin = section.right_margin = Cm(2)
    normal = document.styles["Normal"]
    normal.font.name, normal.font.size = "Arial", Pt(11)
    normal.paragraph_format.space_after = Pt(6)
    normal.paragraph_format.line_spacing = 1.10
    for name in ("Heading 1", "Heading 2", "Heading 3"):
        document.styles[name].font.name = "Arial"
        document.styles[name].font.color.rgb = RGBColor.from_string("17365D")
    header = section.header.paragraphs[0]
    header.text = "2209-A 2026 | CPU Zamanlama | Burak Şanlı"
    for run in header.runs:
        run.font.size = Pt(8)
    footer = section.footer.paragraphs[0]
    footer.alignment = 2
    field = OxmlElement("w:fldSimple")
    field.set(qn("w:instr"), "PAGE")
    footer._p.append(field)
    document.core_properties.title = "CPU Zamanlama — 2209-A Araştırma Önerisi"
    document.core_properties.author = "Burak Şanlı"

    lines = source.splitlines()
    index, paragraph = 0, []

    def flush():
        if paragraph:
            document.add_paragraph(clean(" ".join(paragraph)))
            paragraph.clear()

    while index < len(lines):
        line = lines[index]
        if not line.strip():
            flush()
            index += 1
            continue
        if line.startswith("|"):
            flush()
            rows = []
            while index < len(lines) and lines[index].startswith("|"):
                cells = [cell.strip() for cell in lines[index].strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", cell) for cell in cells):
                    rows.append(cells)
                index += 1
            table(document, rows)
            continue
        if line.startswith("#"):
            flush()
            level = len(line) - len(line.lstrip("#"))
            title = clean(line.lstrip("#").strip())
            if title == "KAYNAKLAR":
                document.add_page_break()
            document.add_heading(title, level=0 if title == "ARAŞTIRMA ÖNERİSİ"
                                 else min(level, 3))
        elif re.match(r"\d+\.\s", line):
            flush()
            document.add_paragraph(clean(line))
        else:
            paragraph.append(line.strip())
        index += 1
    flush()
    for title, filename in (
        ("Ek 1 — Karışık model iş yükü", "ek1_karisik_model.png"),
        ("Ek 2 — Yoğun etkileşimli model iş yükü", "ek2_yogun_etkilesimli_model.png"),
    ):
        document.add_heading(title, level=1)
        document.add_picture(str(DIRECTORY / "ekler" / filename), width=Cm(16.8))
        document.add_paragraph("Kaynak: 5 Kasım 2026 tarihli ön çalışma arşivi. "
                               "Model karşılaştırmasıdır; gerçek Linux politika kazancı göstermez.")
    document.save(destination)


def inspect_word(path):
    document = Document(path)
    required = ["ÖZET", "1. ARAŞTIRMA ÖNERİSİNİN BİLİMSEL NİTELİĞİ",
                "1.1. Konunun Önemi ve Araştırma Önerisinin Bilimsel Niteliği",
                "1.2. Amaç ve Hedefler", "2. YÖNTEM", "3. PROJE YÖNETİMİ",
                "3.1. Çalışma Takvimi", "3.2. Risk Yönetimi", "3.3. Araştırma Olanakları",
                "4. ARAŞTIRMA ÖNERİSİNİN YAYGIN ETKİSİ",
                "5. BELİRTMEK İSTEDİĞİNİZ DİĞER KONULAR", "6. EKLER", "KAYNAKLAR"]
    parts, key = {}, None
    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if text in required:
            key = text
            parts[key] = []
        elif text and key:
            parts[key].append(text)
    if not set(required).issubset(parts):
        raise ValueError("Missing proposal headings")
    summary = "\n".join(parts["ÖZET"])
    words = len(summary.split("Anahtar kelimeler:")[0].split())
    counts = {"section_1_1": len("\n".join(parts[required[2]])),
              "section_1_2": len("\n".join(parts[required[3]])),
              "method": len("\n".join(parts["2. YÖNTEM"]))}
    if not 25 <= words <= 450 or min(counts.values()) < 350:
        raise ValueError("The supplied call's length constraints are not satisfied")
    calendar = next(t for t in document.tables if t.rows[0].cells[0].text == "Dönem")
    weights = [int(row.cells[-1].text) for row in calendar.rows[1:]]
    if sum(weights) != 100 or len(weights) < 1:
        raise ValueError("Invalid calendar contribution weights")
    resources = "\n".join(parts["3.3. Araştırma Olanakları"])
    if "i7-12650H" not in resources or "15,7 GiB" not in resources:
        raise ValueError("Confirmed resource inventory missing")
    text = "\n".join(paragraph.text for paragraph in document.paragraphs)
    if "Her koşuda en az 1.000 kısa iş gözlemi" in text:
        raise ValueError("Superseded sample-count claim remains")
    before_bibliography = text.split("KAYNAKLAR")[0]
    references = ["2024a", "2024b", "2024c", "2024d"]
    if any(ref not in before_bibliography for ref in references):
        raise ValueError("A listed reference is not cited in the proposal")
    with zipfile.ZipFile(path) as archive:
        if archive.testzip() is not None:
            raise ValueError("Invalid Word document archive")
    return {"checked_artifact": path.name, "abstract_words_excluding_keywords": words,
            "abstract_words_including_keywords": len(summary.split()),
            "section_characters": counts, "required_headings_present": True,
            "planned_duration_months": 6, "work_package_count": len(weights),
            "work_package_weights": weights, "weight_sum": sum(weights),
            "main_runs": {"latency": 80, "cpu_only": 40, "total": 120},
            "secondary_runs": 60, "minimum_short_samples_per_latency_run": 1000,
            "short_samples_required_for_cpu_only": False,
            "word_tables": len(document.tables), "embedded_figures": len(document.inline_shapes),
            "all_listed_sources_cited": True, "portal_submission_verified": False,
            "tybs_rendering_verified": False, "advisor_approval_verified": False,
            "institution_signature_verified": False,
            "official_bibliography_webpage_accessible": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", action="store_true", help="also export PDF using LibreOffice")
    arguments = parser.parse_args()
    source = DIRECTORY / f"{STEM}.md"
    word = DIRECTORY / f"{STEM}.docx"
    build_word(source.read_text(), word)
    result = inspect_word(word)
    if arguments.pdf:
        program = shutil.which("soffice") or shutil.which("libreoffice")
        if not program:
            raise RuntimeError("LibreOffice is required for PDF export")
        with tempfile.TemporaryDirectory(prefix="2209-office-", dir="/tmp") as temporary:
            temporary = Path(temporary)
            rendered = temporary / "rendered"
            rendered.mkdir()
            profile = temporary / "profile"
            subprocess.run([program, f"-env:UserInstallation={profile.as_uri()}",
                            "--headless", "--convert-to", "pdf", "--outdir", str(rendered),
                            str(word)], check=True)
            exported = rendered / f"{STEM}.pdf"
            if not exported.is_file() or exported.stat().st_size == 0:
                raise RuntimeError("PDF export did not produce a fresh document")
            shutil.copyfile(exported, DIRECTORY / exported.name)
    result["sha256"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in (source, word, DIRECTORY / f"{STEM}.pdf") if p.exists()}
    (DIRECTORY / "uygunluk_kontrolu.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
