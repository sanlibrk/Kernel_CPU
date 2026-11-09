#!/usr/bin/env python3
"""Fill the research-proposal form derived from the supplied Word examples.

The reusable template contains only the examples' cover, labels and blank tables.
It does not publish another student's proposal. PDF export needs LibreOffice.
"""
import argparse
from copy import deepcopy
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
from docx.shared import Cm, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
DIRECTORY = ROOT / 'docs/basvuru/2209a'
STEM = '2209A_Burak_Sanli_Arastirma_Onerisi'
TEMPLATE = DIRECTORY / 'sablon/2209A_Arastirma_Onerisi_Formati.docx'
REQUIRED = ['A. GENEL BİLGİLER', 'ÖZET',
 '1. ARAŞTIRMA ÖNERİSİNİN BİLİMSEL NİTELİĞİ',
 '1.1. Konunun Önemi ve Araştırma Önerisinin Bilimsel Niteliği',
 '1.2. Amaç ve Hedefler', '2. YÖNTEM', '3. PROJE YÖNETİMİ',
 '3.1. Çalışma Takvimi', '3.2. Risk Yönetimi', '3.3. Araştırma Olanakları',
 '4. ARAŞTIRMA ÖNERİSİNİN YAYGIN ETKİSİ', '5. BÜTÇE TALEP ÇİZELGESİ',
 '6. BELİRTMEK İSTEDİĞİNİZ DİĞER KONULAR', '7. EKLER', 'KAYNAKLAR']


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clean(text):
    return re.sub(r'\[([^]]+)\]\([^)]+\)', r'\1', text).replace('**', '').replace('`', '')


def parse_source(source):
    sections, key = {}, None
    for line in source.splitlines():
        title = line.lstrip('#').strip() if line.startswith('#') else ''
        if title in REQUIRED:
            if title in sections:
                raise ValueError(f'Duplicate proposal heading: {title}')
            key = title
            sections[key] = []
        elif key:
            sections[key].append(line)
    if list(sections) != REQUIRED:
        raise ValueError('Proposal headings do not match the supplied form')
    metadata = {}
    for row in table_rows(sections[REQUIRED[0]]):
        if len(row) == 2:
            metadata[row[0]] = clean(row[1])
    for field in ('Proje başlığı', 'Proje yürütücüsü', 'Akademik danışman', 'Üniversite / bölüm'):
        if not metadata.get(field):
            raise ValueError(f'Missing general information: {field}')
    return metadata, sections


def table_rows(lines):
    rows = []
    for line in lines:
        if not line.strip().startswith('|'):
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if not all(re.fullmatch(r':?-+:?', c) for c in cells):
            rows.append(cells)
    return rows


def format_paragraph(p, *, size=9, bold=False, italic=False, after=3):
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.line_spacing = 1.05
    p.paragraph_format.widow_control = True
    p.paragraph_format.keep_with_next = False
    p.paragraph_format.keep_together = False
    p.paragraph_format.page_break_before = False
    for r in p.runs:
        r.font.name, r.font.size = 'Arial', Pt(size)
        r.bold, r.italic = bold, italic
        r.font.color.rgb = RGBColor(0, 0, 0)


def paragraph(container, text='', *, bold=False, italic=False, size=9):
    p = container.add_paragraph(clean(text))
    format_paragraph(p, size=size, bold=bold, italic=italic)
    return p


def fill_grid(table, rows, *, widths=None):
    columns = len(rows[0])
    if len(table.columns) != columns:
        raise ValueError('Wrong number of columns in the form table')
    table.autofit = False
    if widths:
        for c, w in zip(table.columns, widths):
            c.width = Cm(w)
    while len(table.rows) > len(rows):
        tr = table.rows[-1]._tr
        tr.getparent().remove(tr)
    while len(table.rows) < len(rows):
        table.add_row()
    for i, (row, values) in enumerate(zip(table.rows, rows)):
        if len(values) != columns:
            raise ValueError('Irregular Markdown table')
        trpr = row._tr.get_or_add_trPr()
        for height in list(trpr.findall(qn('w:trHeight'))):
            trpr.remove(height)
        if trpr.find(qn('w:cantSplit')) is None:
            trpr.append(OxmlElement('w:cantSplit'))
        if i == 0 and trpr.find(qn('w:tblHeader')) is None:
            trpr.append(OxmlElement('w:tblHeader'))
        for j, (cell, value) in enumerate(zip(row.cells, values)):
            if widths:
                cell.width = Cm(widths[j])
            cell.text = clean(value)
            for p in cell.paragraphs:
                format_paragraph(p, bold=i == 0, after=2)
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    # Original sample tables are black/grey grids. No replacement theme.
    return table


def render_markdown(document, container, lines):
    pending = []
    def flush():
        if pending:
            paragraph(container, ' '.join(pending))
            pending.clear()
    i = 0
    while i < len(lines):
        line = lines[i]
        if not line.strip():
            flush()
        elif line.startswith('```'):
            flush(); i += 1; code = []
            while i < len(lines) and not lines[i].startswith('```'):
                code.append(lines[i]); i += 1
            if i == len(lines):
                raise ValueError('Unclosed pseudocode block')
            p = container.add_paragraph('\n'.join(code))
            format_paragraph(p)
            p.paragraph_format.line_spacing = 1.0
            p.paragraph_format.keep_together = True
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            shade = OxmlElement('w:shd'); shade.set(qn('w:fill'), 'F2F2F2')
            p._p.get_or_add_pPr().append(shade)
        elif line.strip().startswith('|'):
            flush(); group = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                group.append(lines[i]); i += 1
            rows = table_rows(group); cols = len(rows[0])
            widths = {2:[4.4,11.2],3:[3.0,5.2,7.4],4:[3.4,5.2,3.5,3.5],
                      5:[2.0,3.2,3.0,3.4,4.0]}.get(cols, [15.6/cols]*cols)
            try:
                table = container.add_table(rows=1, cols=cols)
            except TypeError:
                table = container.add_table(rows=1, cols=cols, width=Cm(15.6))
            # Copy the form's general grid appearance for nested technical tables.
            props = deepcopy(document.tables[0]._tbl.tblPr)
            table._tbl.replace(table._tbl.tblPr, props)
            fill_grid(table, rows, widths=widths)
            i -= 1
        elif line.startswith('!['):
            flush()
            match = re.fullmatch(r'!\[([^]]+)\]\(([^)]+)\)', line.strip())
            if not match:
                raise ValueError('Invalid figure markup')
            path = (DIRECTORY / match[2]).resolve()
            if not path.is_relative_to(DIRECTORY):
                raise ValueError('Figure outside proposal directory')
            p = container.add_paragraph()
            p.add_run().add_picture(str(path), width=Cm(15.0))
            p.paragraph_format.keep_with_next = True
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            caption = paragraph(container, match[1], italic=True)
            caption.alignment = WD_ALIGN_PARAGRAPH.CENTER
        elif line.startswith('#'):
            flush()
            p = paragraph(container, line.lstrip('#').strip(), bold=True)
            p.paragraph_format.space_before = Pt(5)
            p.paragraph_format.keep_with_next = True
        elif re.match(r'\d+\.\s', line) or line.startswith('- '):
            flush(); paragraph(container, line)
        else:
            pending.append(line.strip())
        i += 1
    flush()


def fill_content_cell(document, table, lines):
    cell = table.cell(0, 0)
    cell.text = ''
    # A multi-page text field must allow the outer row to split.
    trpr = table.rows[0]._tr.get_or_add_trPr()
    for prop in list(trpr):
        if prop.tag in (qn('w:cantSplit'), qn('w:trHeight'), qn('w:tblHeader')):
            trpr.remove(prop)
    render_markdown(document, cell, lines)
    if len(cell.paragraphs) > 1 and not cell.paragraphs[0].text:
        p = cell.paragraphs[0]._p; p.getparent().remove(p)


def split_long_field(table):
    """Keep one continuous frame but permit breaks between text/figure blocks.

    A single huge Word row containing nested tables may be pushed to a new page
    by LibreOffice. Separate borderless internal rows avoid nearly empty pages.
    """
    first = table.cell(0, 0)
    blocks = [e for e in list(first._tc) if e.tag != qn('w:tcPr')]
    for element in blocks:
        first._tc.remove(element)
    for i, element in enumerate(blocks):
        cell = first if i == 0 else table.add_row().cells[0]
        for p in list(cell._tc):
            if p.tag != qn('w:tcPr'):
                cell._tc.remove(p)
        cell._tc.append(element)
        if element.tag == qn('w:tbl'):
            end = cell.add_paragraph()
            end.paragraph_format.space_after = Pt(0)
            end.paragraph_format.line_spacing = Pt(1)
        trpr = cell._tc.getparent().get_or_add_trPr()
        for prop in list(trpr):
            if prop.tag in (qn('w:cantSplit'), qn('w:trHeight'), qn('w:tblHeader')):
                trpr.remove(prop)
        if element.tag == qn('w:p') and 'MODEL_ADIMI' in ''.join(element.itertext()):
            trpr.append(OxmlElement('w:cantSplit'))
    borders = table._tbl.tblPr.find(qn('w:tblBorders'))
    if borders is not None:
        inside = borders.find(qn('w:insideH'))
        if inside is None:
            inside = OxmlElement('w:insideH');borders.append(inside)
        inside.set(qn('w:val'), 'nil')


def insert_after_heading(document, anchor, lines):
    # Render into a temporary table cell and move the blocks into the body.
    tmp = document.add_table(rows=1, cols=1)
    cell = tmp.cell(0,0)
    render_markdown(document, cell, lines)
    cursor = anchor._p
    for element in list(cell._tc):
        if element.tag == qn('w:tcPr'):
            continue
        if (element.tag == qn('w:p') and not ''.join(element.itertext()).strip()
            and not element.xpath('.//*[local-name()="drawing"]')):
            continue
        cursor.addnext(element); cursor = element
    tmp._tbl.getparent().remove(tmp._tbl)


def build_word(source, destination):
    metadata, parts = parse_source(source)
    document = Document(TEMPLATE)
    original = list(document.paragraphs)
    normal = document.styles['Normal']
    normal.font.name, normal.font.size = 'Arial', Pt(9)
    normal.paragraph_format.line_spacing = 1.05
    normal.paragraph_format.space_after = Pt(3)
    for p in original[23:]:
        format_paragraph(p, bold=bool(p.text.strip() in REQUIRED))
        if p.text.strip().startswith(('Araştırma önerisinde','Özgün değer yazılırken','Önerilen çalışmanın','Başarı ölçütü olarak','Türkçe özetin')):
            format_paragraph(p, italic=True)
        if p.text.strip() and (p.text.strip() in REQUIRED or p.text.strip().startswith(('3.1 ','3.2 '))):
            p.paragraph_format.keep_with_next = True
    # The picture, top cover geometry and program wording are kept from the sample.
    cover_anchor = next(p for p in original if p.text.strip() == 'ARAŞTIRMA ÖNERİSİ FORMU')
    cover_lines = [(metadata['Proje başlığı'],14,True),
                   (metadata['Proje yürütücüsü'],10,False),
                   ('Danışman: '+metadata['Akademik danışman'],10,False),
                   (metadata['Üniversite / bölüm'],10,False)]
    cursor = cover_anchor._p
    for text,size,bold in cover_lines:
        p = document.add_paragraph(text);format_paragraph(p,size=size,bold=bold,after=8)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cursor.addnext(p._p);cursor=p._p
    for p in original[:23]:
        if p.text.strip() == '2026 Yılı':
            p.paragraph_format.space_before = Pt(25)
        if p.text.strip() == '2026 Yılı Çağrısı':
            p.text = ''  # Keep the original cover-ending section boundary.
    for section in document.sections[1:]:
        for p in section.header.paragraphs:
            if p.text.strip():
                p.text='2209/A ÜNİVERSİTE ÖĞRENCİLERİ ARAŞTIRMA PROJELERİ DESTEKLEME PROGRAMI\nARAŞTIRMA ÖNERİSİ FORMU — 2026'
                format_paragraph(p,size=8,bold=True,after=2)
                p.alignment=WD_ALIGN_PARAGRAPH.CENTER
        for p in section.footer.paragraphs:
            p.text=''
        footer=section.footer.paragraphs[0]
        footer.alignment=WD_ALIGN_PARAGRAPH.RIGHT
        field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');footer._p.append(field)
    general=document.tables[0]
    for row,value in zip(general.rows[1:], [metadata['Proje yürütücüsü'],metadata['Proje başlığı'],metadata['Akademik danışman'],metadata['Üniversite / bölüm']]):
        row.cells[1].text=value
    for row in general.rows:
        for cell in row.cells:
            for p in cell.paragraphs:format_paragraph(p)
    for index,key in [(1,'ÖZET'),(2,REQUIRED[3]),(3,REQUIRED[4]),(4,'2. YÖNTEM')]:
        fill_content_cell(document, document.tables[index], parts[key])
        if index == 4:
            split_long_field(document.tables[index])
    for index,key in [(5,'3.1. Çalışma Takvimi'),(6,'3.2. Risk Yönetimi'),
                      (7,'3.3. Araştırma Olanakları'),(8,REQUIRED[10]),(9,REQUIRED[11])]:
        rows=table_rows(parts[key])
        widths={5:[0.9,4.0,2.0,2.2,6.9],6:[1.0,5.1,9.9],7:[6.0,10.0],8:[5.8,10.2],9:[4.0,3.0,9.0]}[index]
        fill_grid(document.tables[index],rows,widths=widths)
    names={'3.1 Çalışma Takvimi':'3.1. Çalışma Takvimi','3.2 Risk Yönetimi':'3.2. Risk Yönetimi'}
    for p in original:
        if p.text.strip() in names:
            p.text=names[p.text.strip()];format_paragraph(p,bold=True)
        if p.text.strip() in (REQUIRED[12],REQUIRED[13],REQUIRED[14]):
            insert_after_heading(document,p,parts[p.text.strip()])
    # The two body sections in the edited example have identical geometry.
    # Merge that redundant break; keep the cover/body section boundary.
    boundaries=[p for p in document.paragraphs if p._p.pPr is not None
                and p._p.pPr.sectPr is not None]
    for p in boundaries[1:]:
        p._p.pPr.remove(p._p.pPr.sectPr)
    for section in document.sections[1:]:
        section.footer.is_linked_to_previous=False
        # The example also contains a page-number content control outside the
        # ordinary paragraph list. Rebuild this footer to avoid duplicate PAGEs.
        for element in list(section.footer._element):
            section.footer._element.remove(element)
        p=section.footer.add_paragraph()
        p.alignment=WD_ALIGN_PARAGRAPH.RIGHT
        field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE')
        field.set(qn('w:dirty'),'true')
        run=OxmlElement('w:r');value=OxmlElement('w:t');value.text='1'
        run.append(value);field.append(run);p._p.append(field)
    # No content, identities or old URLs from the other projects are retained.
    for p in list(document.paragraphs)[23:]:
        if not p.text.strip() and not p._p.xpath('.//*[local-name()="drawing"]'):
            if p._p.pPr is None or p._p.pPr.sectPr is None:
                p._p.getparent().remove(p._p)
    props=document.core_properties
    props.title=metadata['Proje başlığı'];props.author=metadata['Proje yürütücüsü']
    props.subject='TÜBİTAK 2209-A araştırma önerisi, 2026'
    props.comments='Paylaşılan Word örneklerinin kapak ve tablo düzeninde hazırlanmıştır.'
    props.last_modified_by=metadata['Proje yürütücüsü']
    document.save(destination)


def all_text(document):
    return '\n'.join(''.join(p.xpath('.//*[local-name()="t"]/text()'))
                     for p in document._element.xpath('//*[local-name()="p"]'))


def inspect_word(path):
    document=Document(path);source=(DIRECTORY/f'{STEM}.md').read_text()
    metadata,parts=parse_source(source)
    text=all_text(document)
    positions=[text.find(label) for label in REQUIRED]
    if any(p<0 for p in positions) or positions!=sorted(positions):
        raise ValueError('Required form headings missing or out of order in Word')
    abstract=' '.join(parts['ÖZET']).split('Anahtar kelimeler:')[0]
    words=len(abstract.split())
    counts={k:len('\n'.join(parts[h])) for k,h in [('section_1_1',REQUIRED[3]),('section_1_2',REQUIRED[4]),('method','2. YÖNTEM')]}
    if not 25<=words<=450 or min(counts.values())<350:
        raise ValueError('Abstract/section length constraints not met')
    # Named form tables are top-level; technical tables are nested in text boxes.
    if len(document.tables)<10:
        raise ValueError('Expected all ten original form tables')
    wp=document.tables[5]
    weights=[int(re.search(r'%\s*(\d+)',r.cells[-1].text)[1]) for r in wp.rows[1:]]
    if sum(weights)!=100 or len(weights)!=5:
        raise ValueError('Work-package weights are inconsistent')
    budget=document.tables[9]
    if any(clean(r.cells[1].text).strip() not in ('0','0 TL') for r in budget.rows[1:]):
        raise ValueError('Unconfirmed expense introduced')
    source_records=json.loads((DIRECTORY/'kaynak_kaydi.json').read_text())
    body=text.split('KAYNAKLAR')[0]
    for record in source_records:
        if record['citation'] not in body:
            raise ValueError('Missing in-text citation: '+record['citation'])
    if metadata['Proje başlığı']!='Gecikme Odaklı CPU Zamanlama':
        raise ValueError('Project title is not the latest user choice')
    for forbidden in ('Capsicum','Elvan','Sertan','Kübra','Abdulbaki','Umut Arda','mikroplastik','NiCl₂'):
        if forbidden.casefold() in text.casefold():
            raise ValueError('Another project\'s content remains: '+forbidden)
    with ZipFile(path) as archive:
        if archive.testzip() is not None:raise ValueError('Invalid Word archive')
    if len(document.inline_shapes)!=3:
        raise ValueError('Expected flow diagram and two model figures')
    return {'checked_artifact':path.name,'project_title':metadata['Proje başlığı'],
      'format_basis':'Paylaşılan araştırma önerisi Word örneklerinden türetilmiş form',
      'template_sha256':digest(TEMPLATE),'body_font':'Arial','body_font_pt':9,
      'abstract_words_excluding_keywords':words,'section_characters':counts,
      'required_headings_present':True,'original_form_table_count':10,
      'total_top_level_tables':len(document.tables),
      'work_package_table_columns':len(wp.columns),'risk_table_columns':len(document.tables[6].columns),
      'planned_duration_months':6,'work_package_count':len(weights),'work_package_weights':weights,'weight_sum':sum(weights),
      'main_runs':{'latency':80,'cpu_only':40,'total':120},'secondary_runs':60,
      'planned_pilot_model_runs':21,'planned_pilot_kernel_runs_max':56,
      'minimum_short_samples_per_latency_run':1000,'short_samples_required_for_cpu_only':False,
      'embedded_figures':len(document.inline_shapes),'source_count':len(source_records),
      'all_listed_sources_cited':True,'budget_requested_try':0,
      'portal_submission_verified':False,'tybs_rendering_verified':False,
      'advisor_approval_verified':False,'institution_signature_verified':False}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pdf',action='store_true')
    args=parser.parse_args(); source=DIRECTORY/f'{STEM}.md';word=DIRECTORY/f'{STEM}.docx'
    build_word(source.read_text(),word);result=inspect_word(word)
    result['pdf_regenerated_in_this_build']=args.pdf
    if args.pdf:
        program=shutil.which('soffice') or shutil.which('libreoffice')
        if not program:raise RuntimeError('LibreOffice is required for PDF export')
        with tempfile.TemporaryDirectory(prefix='2209-form-',dir='/tmp') as folder:
            folder=Path(folder);rendered=folder/'rendered';rendered.mkdir()
            subprocess.run([program,f'-env:UserInstallation={(folder/"profile").as_uri()}',
                            '--headless','--convert-to','pdf','--outdir',str(rendered),str(word)],check=True)
            pdf=rendered/f'{STEM}.pdf'
            if not pdf.is_file() or not pdf.stat().st_size:raise RuntimeError('No fresh PDF')
            shutil.copyfile(pdf,DIRECTORY/pdf.name)
    inputs=[source,word,DIRECTORY/f'{STEM}.pdf',TEMPLATE,DIRECTORY/'kaynak_kaydi.json']
    inputs.extend(sorted((DIRECTORY/'ekler').glob('*.png')))
    inputs.extend(sorted((DIRECTORY/'ekler').glob('*.svg')))
    result['sha256']={str(p.relative_to(DIRECTORY)):digest(p) for p in inputs if p.exists()}
    (DIRECTORY/'uygunluk_kontrolu.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
