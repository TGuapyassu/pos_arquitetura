#!/usr/bin/env python3
"""
Gera PDF com ficha de entrega (participante, caminhos no projeto, repositório, justificativa do banco).
Saída: docs/ficha_entrega.pdf
"""
from __future__ import annotations

import sys
from pathlib import Path

try:
    from fpdf import FPDF
except ImportError as e:
    print("Instale fpdf2: pip install '.[dev]'", file=sys.stderr)
    raise SystemExit(1) from e

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "ficha_entrega.pdf"

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
    doc_md = ROOT / "docs" / "ddd_documentacao_entrega.md"
    vuln_md = ROOT / "docs" / "relatorio_analise_vulnerabilidades.md"

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
            "Aviso: fonte TrueType não encontrada; acentos podem falhar.",
            file=sys.stderr,
        )

    pdf.add_page()

    def heading(text: str) -> None:
        pdf.set_font(family, "B", 12)
        pdf.cell(0, 8, text, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)

    def body(size: int = 10) -> None:
        pdf.set_font(family, "", size)

    # Título
    pdf.set_font(family, "B", 16)
    pdf.cell(0, 10, "Ficha de entrega — Arquitetura de Software", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    heading("Participantes")
    body()
    pdf.multi_cell(
        0,
        6,
        "Tiago de Andrade Guapyassu Machado",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.ln(3)

    heading("Link da documentação (caminho no projeto)")
    body()
    path_doc = doc_md.relative_to(ROOT)
    pdf.multi_cell(0, 6, str(path_doc), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    heading("Link do repositório")
    body()
    pdf.multi_cell(
        0,
        6,
        "https://github.com/TGuapyassu/pos_arquitetura",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.ln(3)

    heading("Link do vídeo")
    body()
    pdf.multi_cell(
        0,
        6,
        "https://www.youtube.com/watch?v=qrRx3YWXMVs",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.ln(3)

    heading("Relatório com análise de vulnerabilidades (caminho no projeto)")
    body()
    path_v = vuln_md.relative_to(ROOT)
    pdf.multi_cell(0, 6, str(path_v), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    heading("Justificativa da escolha do banco de dados")
    body()
    p1 = (
        "Este MVP modela entidades fortemente relacionadas. clientes, veículos, catálogo de "
        "serviços e peças, estoque e ordens de serviço com itens e mudanças de estado "
        "controladas. Para esse tipo de domínio, um banco relacional é adequado: garante "
        "integridade referencial (FKs), transações ACID e consultas previsíveis sobre "
        "dados estruturados, alinhadas ao uso de SQLAlchemy e Alembic para schema "
        "versionado."
    )
    p2 = (
        "O PostgreSQL foi escolhido por ser robusto, maduro e amplamente adotado em "
        "produção; oferece tipos e constraints úteis ao modelo (texto, numérico para "
        "valores monetários com precisão, timestamps), bom desempenho em cargas OLTP "
        "típicas de um sistema de oficina e ecossistema estável com drivers (psycopg2) e "
        "operação em contêiner (Docker Compose). Em conjunto com o monólito em camadas, o "
        "Postgres sustenta persistência consistente sem complexidade operacional "
        "desnecessária para o escopo do MVP, com caminho claro de evolução (índices, "
        "relatórios, replicação) se o produto crescer."
    )
    pdf.multi_cell(0, 6, p1, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.multi_cell(0, 6, p2, new_x="LMARGIN", new_y="NEXT")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(OUT)
    print(f"PDF gerado: {OUT}")


if __name__ == "__main__":
    main()
