import streamlit as st
import pandas as pd
import logging
from datetime import datetime
from io import StringIO


logger: logging.Logger = logging.getLogger(__name__)


def export_dataframe_csv(
    df: pd.DataFrame,
    filename_prefix: str = "educacao_export",
    delimiter: str = ";",
) -> str:
    buffer = StringIO()
    df.to_csv(buffer, index=False, sep=delimiter, encoding="utf-8")
    return buffer.getvalue()


def render_csv_download(
    df: pd.DataFrame,
    filename_prefix: str = "educacao_export",
    label: str = "Baixar CSV",
) -> None:
    if df is None or df.empty:
        st.warning("Nenhum dado para exportar.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{filename_prefix}_{timestamp}.csv"
    csv_data = export_dataframe_csv(df)

    st.download_button(
        label=label,
        data=csv_data,
        file_name=filename,
        mime="text/csv",
        key=f"csv_download_{timestamp}",
    )

    logger.info(
        "Export CSV preparado: %s (%d linhas)",
        filename,
        len(df),
    )
