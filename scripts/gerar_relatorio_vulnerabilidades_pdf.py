#!/usr/bin/env python3
"""
Gera PDF a partir de docs/relatorio_analise_vulnerabilidades.md
Requer: pip install fpdf2
Usa DejaVu Sans do sistema (Linux) se existir, para suporte a UTF-8 (pt-BR).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    from fpdf import FPDF
except ImportError as e:
    print("Instale fpdf2: pip install fpdf2", file=sys.stderr)
    raise SystemExit(1) from e

ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "docs" / "relatorio_analise_vulnerabilidades.md"
OUT = ROOT / "docs" / "relatorio_analise_vulnerabilidades.pdf"

# Fontes comuns em Linux (WSL)
FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
]
FONT_BOLD = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]


def find_fonts() -> tuple[str, str]:
    reg, bold = "", ""
    for p in FONT_CANDIDATES:
        if Path(p).is_file():
            reg = p
            break
    for p in FONT_BOLD:
        if Path(p).is_file():
            bold = p
            break
    if reg and not bold:
        bold = reg
    return reg, bold


def main() -> None:
    if not MD.is_file():
        print(f"Arquivo não encontrado: {MD}", file=sys.stderr)
        raise SystemExit(2)

    text = MD.read_text(encoding="utf-8")
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    f_reg, f_bold = find_fonts()
    if f_reg:
        pdf.add_font("Body", "", f_reg)
        pdf.add_font("Body", "B", f_bold or f_reg)
        family = "Body"
    else:
        family = "Helvetica"
        print(
            "Aviso: fonte TrueType não encontrada; acentos podem falhar. Instale dejavu-fonts ou edite FONT_CANDIDATES.",
            file=sys.stderr,
        )

    def write_title(line: str) -> None:
        s = line.lstrip("#").strip()
        n = min(len(line) - len(line.lstrip("#")), 6) or 1
        h = 14 - min(n, 2)
        if f_reg:
            pdf.set_font(family, "B", h)
        else:
            pdf.set_font("Helvetica", "B", h)
        pdf.multi_cell(0, h * 0.45, s, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
        if f_reg:
            pdf.set_font(family, "", 10)
        else:
            pdf.set_font("Helvetica", "", 10)

    def is_table_separator(line: str) -> bool:
        return re.match(r"^[\s|:\-−]+$", line) and line.count("-") + line.count("−") > 3

    in_code = False
    pdf.add_page()
    if f_reg:
        pdf.set_font(family, "", 10)
    else:
        pdf.set_font("Helvetica", "", 10)

    for raw in text.splitlines():
        line = raw.rstrip()
        if line.strip().startswith("```"):
            in_code = not in_code
            pdf.ln(2)
            continue
        if in_code:
            pdf.set_font("Courier" if not f_reg else family, "", 8)
            pdf.multi_cell(0, 3.5, line or " ", new_x="LMARGIN", new_y="NEXT")
            if f_reg:
                pdf.set_font(family, "", 10)
            else:
                pdf.set_font("Helvetica", "", 10)
            continue
        if not line.strip():
            pdf.ln(2)
            continue
        if line.startswith("#"):
            write_title(line)
            if f_reg:
                pdf.set_font(family, "", 10)
            else:
                pdf.set_font("Helvetica", "", 10)
            continue
        if line.strip().startswith("|") and is_table_separator(line):
            continue
        if re.match(r"^[\-\*] ", line) or re.match(r"^[\d]+\. ", line):
            body = re.sub(r"^[\-\*] ", "• ", line)
            body = re.sub(r"^[\d]+\. ", "• ", body) if not body.startswith("•") else body
            pdf.set_font("Helvetica" if not f_reg else family, "", 10)
            pdf.multi_cell(0, 5, body, new_x="LMARGIN", new_y="NEXT")
            continue
        if line.strip().startswith("|") and " | " in line:
            pdf.set_font("Helvetica" if not f_reg else family, "", 8)
            clean = " | ".join(c.strip() for c in line.split("|") if c.strip())
            pdf.multi_cell(0, 4, clean, new_x="LMARGIN", new_y="NEXT")
            if f_reg:
                pdf.set_font(family, "", 10)
            else:
                pdf.set_font("Helvetica", "", 10)
            continue
        if f_reg:
            pdf.set_font(family, "", 10)
        else:
            pdf.set_font("Helvetica", "", 10)
        if line.strip().startswith("> "):
            pdf.multi_cell(0, 5, line[2:].strip(), new_x="LMARGIN", new_y="NEXT")
            continue
        pdf.multi_cell(0, 5, line, new_x="LMARGIN", new_y="NEXT")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(OUT)
    print(f"PDF gerado: {OUT}")


if __name__ == "__main__":
    main()
