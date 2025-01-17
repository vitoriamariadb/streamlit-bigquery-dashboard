import streamlit as st
import pandas as pd
import plotly.express as px
import logging
from typing import Optional


logger: logging.Logger = logging.getLogger(__name__)


def calculate_retention_rate(
    df: pd.DataFrame,
    year_col: str = "ano",
    enrolled_col: str = "total_matriculas",
    retained_col: str = "matriculas_ano_seguinte",
) -> pd.DataFrame:
    if retained_col not in df.columns:
        df_sorted = df.sort_values(year_col)
        df_sorted[retained_col] = df_sorted[enrolled_col].shift(-1)
        df = df_sorted.dropna(subset=[retained_col])

    df = df.copy()
    df["taxa_retencao"] = (df[retained_col] / df[enrolled_col] * 100).round(1)
    df["taxa_evasao"] = (100 - df["taxa_retencao"]).round(1)
    return df


def calculate_year_over_year(
    df: pd.DataFrame,
    metric_col: str,
    year_col: str = "ano",
) -> pd.DataFrame:
    df_sorted = df.sort_values(year_col).copy()
    df_sorted["valor_anterior"] = df_sorted[metric_col].shift(1)
    df_sorted["variacao_abs"] = (df_sorted[metric_col] - df_sorted["valor_anterior"]).round(2)
    df_sorted["variacao_pct"] = (
        (df_sorted["variacao_abs"] / df_sorted["valor_anterior"]) * 100
    ).round(2)
    return df_sorted.dropna(subset=["valor_anterior"])


def render_retention_page(df: Optional[pd.DataFrame] = None) -> None:
    st.header("Retencao e Evasao")
    st.markdown(
        "Analise das taxas de retencao e evasao escolar, "
        "com detalhamento por regiao, rede e etapa de ensino."
    )

    view_mode: str = st.radio(
        "Modo de visualizacao",
        options=["Serie Temporal", "Comparativo Regional", "Detalhamento"],
        horizontal=True,
        key="retention_view",
    )

    if df is None or df.empty:
        st.warning("Nenhum dado disponivel.")
        _render_demo_retention(view_mode)
        return

    retention_df = calculate_retention_rate(df)

    if view_mode == "Serie Temporal":
        fig = px.line(
            retention_df,
            x="ano",
            y=["taxa_retencao", "taxa_evasao"],
            title="Evolucao das Taxas de Retencao e Evasao",
            template="plotly_white",
        )
        st.plotly_chart(fig, use_container_width=True)

    elif view_mode == "Comparativo Regional":
        if "regiao" in retention_df.columns:
            fig = px.bar(
                retention_df.groupby("regiao")["taxa_retencao"].mean().reset_index(),
                x="regiao",
                y="taxa_retencao",
                title="Taxa de Retencao por Regiao",
                template="plotly_white",
            )
            st.plotly_chart(fig, use_container_width=True)

    elif view_mode == "Detalhamento":
        st.dataframe(retention_df, use_container_width=True)

    logger.info("Pagina Retencao renderizada: %s", view_mode)


def _render_demo_retention(view_mode: str) -> None:
    st.info("Exibindo dados demonstrativos")
    years = list(range(2015, 2024))
    demo = pd.DataFrame({
        "ano": years,
        "taxa_retencao": [91.2, 91.5, 92.0, 92.3, 92.8, 93.1, 93.5, 93.8, 94.2],
        "taxa_evasao": [8.8, 8.5, 8.0, 7.7, 7.2, 6.9, 6.5, 6.2, 5.8],
    })

    if view_mode == "Serie Temporal":
        fig = px.line(
            demo,
            x="ano",
            y=["taxa_retencao", "taxa_evasao"],
            title="Evolucao das Taxas de Retencao e Evasao",
            template="plotly_white",
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.dataframe(demo, use_container_width=True)

