import streamlit as st
import pandas as pd
import logging
from io import BytesIO
from datetime import datetime
from typing import Optional


logger: logging.Logger = logging.getLogger(__name__)


class PDFReportConfig:
    """Configuracao para geracao de relatorios PDF."""

    def __init__(
        self,
        title: str = "Painel Educação Básica",
        subtitle: str = "",
        author: str = "Sistema Painel Educação",
        page_size: str = "A4",
        orientation: str = "portrait",
        include_charts: bool = True,
        include_tables: bool = True,
    ):
        self.title: str = title
        self.subtitle: str = subtitle
        self.author: str = author
        self.page_size: str = page_size
        self.orientation: str = orientation
        self.include_charts: bool = include_charts
        self.include_tables: bool = include_tables


def generate_pdf_report(
    dataframes: dict[str, pd.DataFrame],
    config: Optional[PDFReportConfig] = None,
) -> bytes:
    if config is None:
        config = PDFReportConfig()

    output = BytesIO()

    try:
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

        page_size = landscape(A4) if config.orientation == "landscape" else A4
        doc = SimpleDocTemplate(output, pagesize=page_size)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph(config.title, styles["Title"]))
        if config.subtitle:
            elements.append(Paragraph(config.subtitle, styles["Heading2"]))
        elements.append(Spacer(1, 20))

        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
        elements.append(Paragraph(f"Gerado em: {timestamp}", styles["Normal"]))
        elements.append(Spacer(1, 20))

        for section_name, df in dataframes.items():
            if df.empty:
                continue

            elements.append(Paragraph(section_name, styles["Heading2"]))
            elements.append(Spacer(1, 10))

            if config.include_tables:
                table_data = [df.columns.tolist()] + df.head(50).values.tolist()
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2ecc71")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTSIZE", (0, 0), (-1, -1), 8),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ]))
                elements.append(table)
                elements.append(Spacer(1, 20))

        doc.build(elements)
        logger.info("Relatorio PDF gerado: %d secoes", len(dataframes))

    except ImportError:
        logger.warning("reportlab nao instalado, gerando PDF simplificado")
        content = _generate_simple_pdf(dataframes, config)
        output.write(content)

    return output.getvalue()


def _generate_simple_pdf(
    dataframes: dict[str, pd.DataFrame],
    config: PDFReportConfig,
) -> bytes:
    lines = [config.title, "=" * len(config.title), ""]
    if config.subtitle:
        lines.append(config.subtitle)
        lines.append("")

    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M")
    lines.append(f"Gerado em: {timestamp}")
    lines.append("")

    for name, df in dataframes.items():
        lines.append(f"## {name}")
        lines.append(f"Registros: {len(df)}")
        lines.append(df.to_string(index=False))
        lines.append("")

    return "\n".join(lines).encode("utf-8")


def render_pdf_download(
    dataframes: dict[str, pd.DataFrame],
    config: Optional[PDFReportConfig] = None,
    label: str = "Baixar PDF",
) -> None:
    has_data = any(not df.empty for df in dataframes.values())
    if not has_data:
        st.warning("Nenhum dado para exportar.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"educacao_relatorio_{timestamp}.pdf"

    pdf_data = generate_pdf_report(dataframes, config)

    st.download_button(
        label=label,
        data=pdf_data,
        file_name=filename,
        mime="application/pdf",
        key=f"pdf_download_{timestamp}",
    )
    logger.info("Export PDF preparado: %s", filename)
