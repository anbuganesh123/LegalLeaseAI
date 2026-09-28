from __future__ import annotations

import os
import re
from pathlib import Path

from fpdf import FPDF

from ..utils.text import markdown_to_runs, sanitize_text, terms_to_list

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LOGO = PROJECT_ROOT / "assets" / "logo.png"


def _find_font() -> tuple[str | None, str | None, str | None]:
    regular_candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        r"C:\\Windows\\Fonts\\arial.ttf",
        r"C:\\Windows\\Fonts\\segoeui.ttf",
    ]
    bold_candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        r"C:\\Windows\\Fonts\\arialbd.ttf",
        r"C:\\Windows\\Fonts\\segoeuib.ttf",
    ]
    italic_candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Italic.ttf",
        r"C:\\Windows\\Fonts\\ariali.ttf",
        r"C:\\Windows\\Fonts\\segoeuii.ttf",
    ]
    regular = next((p for p in regular_candidates if os.path.exists(p)), None)
    bold = next((p for p in bold_candidates if os.path.exists(p)), None)
    italic = next((p for p in italic_candidates if os.path.exists(p)), None)
    return regular, bold, italic


class LegalEasePDF(FPDF):
    def __init__(self, doc_type: str, logo_path: str | Path | None = None) -> None:
        super().__init__(orientation="P", unit="mm", format="A4")
        self.doc_type = sanitize_text(doc_type)
        self.logo_path = Path(logo_path) if logo_path else DEFAULT_LOGO
        self.set_auto_page_break(auto=True, margin=18)
        regular, bold, italic = _find_font()
        self.font_family = "Helvetica"
        self.italic_available = False
        if regular:
            self.add_font("LegalEaseSans", "", regular)
            self.add_font("LegalEaseSans", "B", bold or regular)
            if italic:
                self.add_font("LegalEaseSans", "I", italic)
                self.italic_available = True
            self.font_family = "LegalEaseSans"

    def header(self) -> None:
        if self.logo_path.exists():
            try:
                self.image(str(self.logo_path), x=78, y=8, w=54)
                self.ln(17)
                return
            except Exception:
                pass
        self.set_font(self.font_family, "B", 12)
        self.cell(0, 8, "LegalEase", align="C", new_x="LMARGIN", new_y="NEXT")

    def footer(self) -> None:
        self.set_y(-13)
        self.set_font(self.font_family, "", 7)
        self.cell(0, 4, f"LegalEase - {self.doc_type} | Page {self.page_no()}", align="C")


def _write_inline(pdf: LegalEasePDF, text: str, height: float = 5.5, base_size: float = 10.5, default_bold: bool = False) -> None:
    for chunk, bold, italic, _is_code in markdown_to_runs(text):
        style = "B" if (default_bold or bold) else ""
        if italic and not style and getattr(pdf, "italic_available", False):
            style = "I"
        pdf.set_font(pdf.font_family, style, base_size)
        pdf.write(height, chunk)
    pdf.ln(height)


def _write_line(pdf: LegalEasePDF, line: str) -> None:
    safe = sanitize_text(line)
    if not safe:
        pdf.ln(2)
        return
    if safe.startswith("### "):
        pdf.ln(1)
        _write_inline(pdf, safe[4:], height=6, base_size=11, default_bold=True)
    elif safe.startswith("## "):
        pdf.ln(2)
        _write_inline(pdf, safe[3:], height=7, base_size=13, default_bold=True)
    elif safe.startswith("# "):
        _write_inline(pdf, safe[2:], height=8, base_size=16, default_bold=True)
    elif re.match(r"^[-*] ", safe):
        pdf.set_x(pdf.l_margin + 2)
        _write_inline(pdf, "- " + safe[2:], height=5.4, base_size=10.5)
    elif re.match(r"^\d+[.)] ", safe):
        pdf.set_x(pdf.l_margin + 1)
        _write_inline(pdf, safe, height=5.5, base_size=10.5)
    else:
        _write_inline(pdf, safe, height=5.5, base_size=10.5)


def format_pdf(text: str, doc_type: str, terms: str = "", logo_path: str | Path | None = None) -> bytes:
    pdf = LegalEasePDF(doc_type, logo_path=logo_path)
    pdf.set_margins(18, 25, 18)
    pdf.add_page()
    pdf.set_title(sanitize_text(doc_type))
    pdf.set_creator("LegalEase")

    content = sanitize_text(text)
    has_title = any(line.strip().startswith("# ") for line in content.splitlines())
    if not has_title:
        _write_inline(pdf, sanitize_text(doc_type), height=8, base_size=16, default_bold=True)
        pdf.ln(3)

    for line in content.splitlines():
        _write_line(pdf, line)

    cleaned_terms = terms_to_list(terms)
    if cleaned_terms:
        pdf.ln(4)
        _write_inline(pdf, "Terms Summary", height=7, base_size=13, default_bold=True)
        for idx, term in enumerate(cleaned_terms, 1):
            _write_inline(pdf, f"{idx}. {term}", height=5.4, base_size=10)

    output = pdf.output()
    if isinstance(output, str):
        return output.encode("latin-1")
    return bytes(output)
