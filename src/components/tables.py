import streamlit as st
import pandas as pd
import logging
from typing import Optional


logger: logging.Logger = logging.getLogger(__name__)

DEFAULT_PAGE_SIZE: int = 25
MAX_PAGE_SIZE: int = 100


class TableConfig:
    """Configuracao para renderizacao de tabelas."""

    def __init__(
        self,
        page_size: int = DEFAULT_PAGE_SIZE,
        sortable: bool = True,
        filterable: bool = True,
        resizable: bool = True,
        selection_mode: Optional[str] = None,
    ):
        self.page_size: int = min(page_size, MAX_PAGE_SIZE)
        self.sortable: bool = sortable
        self.filterable: bool = filterable
        self.resizable: bool = resizable
        self.selection_mode: Optional[str] = selection_mode


def format_numeric_columns(df: pd.DataFrame, decimal_places: int = 2) -> pd.DataFrame:
    formatted = df.copy()
    for col in formatted.select_dtypes(include=["float64", "float32"]).columns:
        formatted[col] = formatted[col].round(decimal_places)
    return formatted


def render_data_table(
    df: pd.DataFrame,
    config: Optional[TableConfig] = None,
    title: Optional[str] = None,
    key: Optional[str] = None,
) -> Optional[pd.DataFrame]:
    if df is None or df.empty:
        st.info("Nenhum dado para exibir na tabela.")
        return None

    if config is None:
        config = TableConfig()

    if title:
        st.subheader(title)

    st.caption(f"{len(df):,} registros encontrados")

    formatted_df = format_numeric_columns(df)

    if config.filterable:
        search_term = st.text_input(
            "Buscar na tabela",
            key=f"table_search_{key or 'default'}",
        )
        if search_term:
            mask = formatted_df.astype(str).apply(
                lambda row: row.str.contains(search_term, case=False).any(),
                axis=1,
            )
            formatted_df = formatted_df[mask]
            st.caption(f"{len(formatted_df):,} registros filtrados")

    total_pages = max(1, (len(formatted_df) - 1) // config.page_size + 1)

    if total_pages > 1:
        page = st.number_input(
            "Pagina",
            min_value=1,
            max_value=total_pages,
            value=1,
            key=f"table_page_{key or 'default'}",
        )
    else:
        page = 1

    start_idx = (page - 1) * config.page_size
    end_idx = start_idx + config.page_size
    page_df = formatted_df.iloc[start_idx:end_idx]

    st.dataframe(
        page_df,
        use_container_width=True,
        hide_index=True,
    )

    if total_pages > 1:
        st.caption(f"Pagina {page} de {total_pages}")

    logger.debug(
        "Tabela renderizada: %d linhas (pagina %d/%d)",
        len(page_df), page, total_pages,
    )
    return page_df


def render_pivot_table(
    df: pd.DataFrame,
    index: str,
    columns: str,
    values: str,
    aggfunc: str = "mean",
    title: Optional[str] = None,
) -> Optional[pd.DataFrame]:
    if df is None or df.empty:
        return None

    try:
        pivot = pd.pivot_table(
            df,
            index=index,
            columns=columns,
            values=values,
            aggfunc=aggfunc,
        ).round(2)

        if title:
            st.subheader(title)

        st.dataframe(pivot, use_container_width=True)
        logger.info("Tabela pivot renderizada: %s", title or "sem titulo")
        return pivot
    except Exception as e:
        logger.error("Erro ao criar tabela pivot: %s", e)
        st.error("Erro ao criar tabela pivot.")
        return None
