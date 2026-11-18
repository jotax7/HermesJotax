#!/usr/bin/env python3
"""Markdown -> styled multi-page PDF (WeasyPrint). No pandoc, no LaTeX.

Usage:
    python md2pdf.py informe.md informe.pdf

Deps (install into a venv, not into the Hermes interpreter):
    python3 -m venv ~/.hermes/venvs/pdf && \
      ~/.hermes/venvs/pdf/bin/pip install weasyprint markdown pymupdf

Why this instead of the reportlab JSON-spec path: when the source is already a
markdown document (a report, a proposal, notes the user will forward), piping it
through a JSON spec loses the structure. CSS `@page` gives real page numbers, a
running footer and repeating table headers for free.

The stylesheet below is the corporate/serious default: A4, sans-serif, hairline
tables, blue-accented code blocks, footer with document label + page counter.
Edit CSS in place rather than sprinkling inline styles in the markdown.
"""
import sys
from pathlib import Path

import markdown
from weasyprint import HTML

CSS = """
@page {
  size: A4;
  margin: 20mm 18mm 22mm 18mm;
  @bottom-center {
    content: "Documento confidencial";
    font-family: Helvetica, Arial, sans-serif;
    font-size: 7.5pt;
    color: #8a949e;
  }
  @bottom-right {
    content: counter(page) " / " counter(pages);
    font-family: Helvetica, Arial, sans-serif;
    font-size: 7.5pt;
    color: #8a949e;
  }
}
body { font-family: Helvetica, Arial, sans-serif; font-size: 9.6pt; line-height: 1.5; color: #1c2530; }
h1 { font-size: 19pt; line-height: 1.2; margin: 0 0 2mm 0; color: #0d1b2a; letter-spacing: -0.3pt; }
h1 + p { color: #5a6672; font-size: 9pt; }
h2 { font-size: 12.5pt; margin: 8mm 0 2.5mm 0; padding-bottom: 1.2mm;
     border-bottom: 0.7pt solid #d7dde4; color: #12314d; page-break-after: avoid; }
h3 { font-size: 10.5pt; margin: 5mm 0 2mm 0; color: #1f4a72; page-break-after: avoid; }
p { margin: 0 0 2.6mm 0; }
ul, ol { margin: 0 0 3mm 0; padding-left: 5mm; }
li { margin-bottom: 1.2mm; }
table { border-collapse: collapse; width: 100%; margin: 3mm 0 4mm 0; font-size: 8.3pt; page-break-inside: avoid; }
th { background: #eef2f6; text-align: left; padding: 2mm 2.2mm; border: 0.5pt solid #cfd8e0;
     font-size: 8.2pt; color: #12314d; }
td { padding: 1.9mm 2.2mm; border: 0.5pt solid #dde3e9; vertical-align: top; }
tr:nth-child(even) td { background: #fafbfc; }
code { font-family: "DejaVu Sans Mono", monospace; font-size: 8.2pt; background: #f2f5f8;
       padding: 0.3mm 1mm; border-radius: 1mm; }
pre { background: #f6f8fa; border-left: 2pt solid #1f6feb; padding: 1.8mm 3mm; font-size: 7.8pt;
      line-height: 1.35; white-space: pre-wrap; page-break-inside: avoid; margin: 3mm 0 4mm 0; }
pre code { background: none; padding: 0; font-size: 7.8pt; }
strong { color: #0d1b2a; }
hr { border: none; border-top: 0.5pt solid #dde3e9; margin: 6mm 0; }
blockquote { border-left: 2pt solid #b8c4d0; margin: 3mm 0; padding: 0.5mm 3mm; color: #4a5663; }
"""


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 1
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    html = markdown.markdown(
        src.read_text(encoding="utf-8"),
        extensions=["tables", "fenced_code", "sane_lists", "attr_list"],
    )
    doc = f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{html}</body></html>"
    HTML(string=doc).write_pdf(str(out))
    print(f"PDF: {out} - {out.stat().st_size / 1024:.0f} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
