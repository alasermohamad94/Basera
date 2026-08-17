#!/usr/bin/env python3
"""Convert Basera graduation study Markdown to formatted Arabic RTL Word document."""

from __future__ import annotations

import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.shared import OxmlElement as OE


def shade_cell(cell, fill: str = "D9E2F3") -> None:
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    shd = OE("w:shd")
    shd.set(qn("w:fill"), fill)
    shd.set(qn("w:val"), "clear")
    tc_pr.append(shd)


def set_paragraph_rtl(paragraph) -> None:
    p_pr = paragraph._p.get_or_add_pPr()
    bidi = OxmlElement("w:bidi")
    p_pr.append(bidi)
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT


def set_run_rtl(run) -> None:
    r_pr = run._r.get_or_add_rPr()
    rtl = OxmlElement("w:rtl")
    r_pr.append(rtl)


def add_formatted_text(paragraph, text: str, *, bold_default: bool = False, font_name: str = "Arial") -> None:
    """Parse **bold** and `code` inline markers."""
    pattern = re.compile(r"(\*\*[^*]+\*\*|`[^`]+`)")
    pos = 0
    for match in pattern.finditer(text):
        if match.start() > pos:
            run = paragraph.add_run(text[pos : match.start()])
            run.bold = bold_default
            run.font.name = font_name
            run.font.size = Pt(12)
            set_run_rtl(run)
        chunk = match.group(0)
        if chunk.startswith("**"):
            run = paragraph.add_run(chunk[2:-2])
            run.bold = True
        else:
            run = paragraph.add_run(chunk[1:-1])
            run.font.name = "Consolas"
            run.font.size = Pt(10)
        run.font.name = font_name if not chunk.startswith("`") else "Consolas"
        if not chunk.startswith("`"):
            run.font.size = Pt(12)
        set_run_rtl(run)
        pos = match.end()
    if pos < len(text):
        run = paragraph.add_run(text[pos:])
        run.bold = bold_default
        run.font.name = font_name
        run.font.size = Pt(12)
        set_run_rtl(run)


def is_table_row(line: str) -> bool:
    s = line.strip()
    return s.startswith("|") and s.endswith("|") and "|" in s[1:-1]


def is_separator_row(line: str) -> bool:
    s = line.strip().strip("|").strip()
    if not s:
        return False
    return all(re.match(r"^:?-+:?$", cell.strip()) for cell in s.split("|"))


def parse_table_rows(lines: list[str]) -> tuple[list[list[str]], int]:
    rows: list[list[str]] = []
    i = 0
    while i < len(lines) and is_table_row(lines[i]):
        if not is_separator_row(lines[i]):
            cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
            rows.append(cells)
        i += 1
    return rows, i


def add_table(doc: Document, rows: list[list[str]]) -> None:
    if not rows:
        return
    cols = max(len(r) for r in rows)
    table = doc.add_table(rows=len(rows), cols=cols)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for ri, row in enumerate(rows):
        for ci in range(cols):
            cell_text = row[ci] if ci < len(row) else ""
            cell = table.rows[ri].cells[ci]
            cell.text = ""
            p = cell.paragraphs[0]
            set_paragraph_rtl(p)
            add_formatted_text(p, cell_text)
            for run in p.runs:
                run.font.size = Pt(11)
                if ri == 0:
                    run.bold = True
            if ri == 0:
                shade_cell(cell)
    doc.add_paragraph()


def add_heading(doc: Document, text: str, level: int, *, is_first_title: bool = False) -> None:
    clean = text.lstrip("#").strip()
    sizes = {1: 24, 2: 18, 3: 16, 4: 14, 5: 13}

    if level == 2 and re.match(r"^#{2}\s+\d", text):
        doc.add_page_break()

    p = doc.add_paragraph()
    set_paragraph_rtl(p)
    if is_first_title:
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    else:
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p.paragraph_format.space_before = Pt(14 if level <= 2 else 8)
    p.paragraph_format.space_after = Pt(8)
    run = p.add_run(clean)
    run.bold = True
    run.font.name = "Arial"
    run.font.size = Pt(sizes.get(level, 12))
    if is_first_title:
        run.font.size = Pt(26)
    set_run_rtl(run)


def add_codeblock(doc: Document, lines: list[str], language: str = "") -> None:
    label = "مخطط (Mermaid) — يُعرض في Markdown/VS Code:" if language == "mermaid" else "كود:"
    if language == "mermaid":
        p = doc.add_paragraph()
        set_paragraph_rtl(p)
        run = p.add_run(label)
        run.bold = True
        run.italic = True
        run.font.name = "Arial"
        run.font.size = Pt(11)
        run.font.color.rgb = RGBColor(0x55, 0x55, 0x55)
        set_run_rtl(run)

    for line in lines:
        p = doc.add_paragraph()
        set_paragraph_rtl(p)
        p.paragraph_format.left_indent = Cm(0.5)
        run = p.add_run(line)
        run.font.name = "Consolas"
        run.font.size = Pt(9)
        run.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
        if language == "mermaid":
            set_run_rtl(run)
    doc.add_paragraph()


def configure_document(doc: Document) -> None:
    section = doc.sections[0]
    section.page_height = Cm(29.7)
    section.page_width = Cm(21.0)
    section.top_margin = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)

    # Default RTL for Normal style
    styles = doc.styles["Normal"]
    styles.font.name = "Arial"
    styles.font.size = Pt(12)
    pf = styles.paragraph_format
    pf.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    pf.line_spacing = 1.35


def convert_md_to_docx(md_path: Path, docx_path: Path) -> None:
    text = md_path.read_text(encoding="utf-8")
    lines = text.splitlines()
    doc = Document()
    configure_document(doc)

    i = 0
    in_code = False
    code_lang = ""
    code_lines: list[str] = []
    first_h1 = True

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Fenced code block
        if stripped.startswith("```"):
            if not in_code:
                in_code = True
                code_lang = stripped[3:].strip().lower()
                code_lines = []
            else:
                add_codeblock(doc, code_lines, code_lang)
                in_code = False
                code_lang = ""
                code_lines = []
            i += 1
            continue

        if in_code:
            code_lines.append(line)
            i += 1
            continue

        # Headings
        m = re.match(r"^(#{1,5})\s+(.+)$", line)
        if m:
            lvl = len(m.group(1))
            add_heading(doc, line, lvl, is_first_title=(first_h1 and lvl == 1))
            if first_h1 and lvl == 1:
                first_h1 = False
            i += 1
            continue

        # Horizontal rule
        if stripped in ("---", "***", "___"):
            p = doc.add_paragraph()
            set_paragraph_rtl(p)
            run = p.add_run("─" * 40)
            run.font.color.rgb = RGBColor(0xAA, 0xAA, 0xAA)
            i += 1
            continue

        # Blockquote
        if stripped.startswith(">"):
            p = doc.add_paragraph()
            set_paragraph_rtl(p)
            add_formatted_text(p, stripped.lstrip(">").strip(), bold_default=False)
            for run in p.runs:
                run.italic = True
            i += 1
            continue

        # Table
        if is_table_row(line):
            rows, consumed = parse_table_rows(lines[i:])
            add_table(doc, rows)
            i += consumed
            continue

        # Ordered list
        m = re.match(r"^(\d+)\.\s+(.+)$", stripped)
        if m:
            p = doc.add_paragraph()
            set_paragraph_rtl(p)
            add_formatted_text(p, f"{m.group(1)}. {m.group(2)}")
            p.paragraph_format.left_indent = Cm(0.75)
            i += 1
            continue

        # Unordered list
        if stripped.startswith("- ") or stripped.startswith("* "):
            p = doc.add_paragraph()
            set_paragraph_rtl(p)
            add_formatted_text(p, "• " + stripped[2:])
            p.paragraph_format.left_indent = Cm(0.75)
            i += 1
            continue

        # Empty line
        if not stripped:
            i += 1
            continue

        # Regular paragraph
        p = doc.add_paragraph()
        set_paragraph_rtl(p)
        add_formatted_text(p, stripped)
        i += 1

    doc.save(str(docx_path))
    size_kb = docx_path.stat().st_size // 1024
    print(f"Saved OK ({size_kb} KB)")


def main() -> int:
    base = Path(__file__).resolve().parent.parent
    md_path = base / "دراسة مشروع التخرج.md"
    docx_path = base / "دراسة مشروع التخرج.docx"

    if len(sys.argv) >= 2:
        md_path = Path(sys.argv[1])
    if len(sys.argv) >= 3:
        docx_path = Path(sys.argv[2])

    if not md_path.exists():
        print(f"Missing: {md_path}", file=sys.stderr)
        return 1

    convert_md_to_docx(md_path, docx_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
