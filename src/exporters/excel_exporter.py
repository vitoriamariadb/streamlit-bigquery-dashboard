import streamlit as st
import pandas as pd
import logging
from io import BytesIO
from datetime import datetime
from typing import Optional


logger: logging.Logger = logging.getLogger(__name__)


def export_dataframe_excel(
    dataframes: dict[str, pd.DataFrame],
    filename_prefix: str = "educacao_export",
) -> bytes:
    output = BytesIO()

    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        for sheet_name, df in dataframes.items():
            safe_name = sheet_name[:31]
            df.to_excel(writer, index=False, sheet_name=safe_name)

            workbook = writer.book
            worksheet = writer.sheets[safe_name]

            header_format = workbook.add_format({
                "bold": True,
                "bg_color": "#2ecc71",
                "font_color": "#ffffff",
                "border": 1,
            })
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)

            for col_num, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).str.len().max(),
                    len(str(col)),
                )
                worksheet.set_column(col_num, col_num, min(max_length + 2, 50))

    return output.getvalue()


def render_excel_download(
    dataframes: dict[str, pd.DataFrame],
    filename_prefix: str = "educacao_export",
    label: str = "Baixar Excel",
) -> None:
    has_data = any(not df.empty for df in dataframes.values())
    if not has_data:
        st.warning("Nenhum dado para exportar.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.xlsx"

    excel_data = export_dataframe_excel(dataframes, filename_prefix)

    total_rows = sum(len(df) for df in dataframes.values())
    total_sheets = len(dataframes)

    st.download_button(
        label=label,
        data=excel_data,
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        key=f"excel_download_{timestamp}",
    )

    st.caption(f"{total_sheets} abas | {total_rows:,} linhas")
    logger.info("Export Excel preparado: %s (%d abas, %d linhas)", filename, total_sheets, total_rows)


def export_single_sheet(
    df: pd.DataFrame,
    sheet_name: str = "Dados",
    filename_prefix: str = "educacao_export",
) -> bytes:
    return export_dataframe_excel({sheet_name: df}, filename_prefix)
