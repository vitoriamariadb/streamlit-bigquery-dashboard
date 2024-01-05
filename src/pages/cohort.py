import streamlit as st
import pandas as pd
import numpy as np
import logging
from typing import Optional


logger: logging.Logger = logging.getLogger(__name__)


def build_cohort_matrix(
    df: pd.DataFrame,
    cohort_col: str = "ano_ingresso",
    period_col: str = "ano",
    value_col: str = "total_matriculas",
) -> pd.DataFrame:
    if cohort_col not in df.columns or period_col not in df.columns:
        return pd.DataFrame()

    cohort_data = df.groupby([cohort_col, period_col])[value_col].sum().reset_index()
    cohort_data["periodo_idx"] = cohort_data[period_col] - cohort_data[cohort_col]

    cohort_pivot = cohort_data.pivot_table(
        index=cohort_col,
        columns="periodo_idx",
        values=value_col,
        aggfunc="sum",
    )

    cohort_sizes = cohort_pivot.iloc[:, 0]
    retention_matrix = cohort_pivot.divide(cohort_sizes, axis=0) * 100

    return retention_matrix.round(1)


def render_cohort_page(df: Optional[pd.DataFrame] = None) -> None:
    st.header("Analise de Coorte")
    st.markdown(
        "Acompanhamento de grupos de alunos ao longo do tempo, "
        "permitindo identificar padroes de retencao e evasao."
    )

    col1, col2 = st.columns(2)
    with col1:
        metric: str = st.selectbox(
            "Metrica",
            options=["Matriculas", "Aprovacao", "Abandono"],
            key="cohort_metric",
        )
    with col2:
        cohort_type: str = st.selectbox(
            "Tipo de Coorte",
            options=["Ano de Ingresso", "Etapa de Ensino", "Rede"],
            key="cohort_type",
        )

    if df is None or df.empty:
        st.warning("Nenhum dado disponivel.")
        _render_demo_cohort()
        return

    metric_map = {
        "Matriculas": "total_matriculas",
        "Aprovacao": "taxa_aprovacao",
        "Abandono": "taxa_abandono",
    }
    value_col = metric_map.get(metric, "total_matriculas")

    matrix = build_cohort_matrix(df, value_col=value_col)
    if not matrix.empty:
        st.dataframe(
            matrix.style.background_gradient(cmap="RdYlGn", axis=1),
            use_container_width=True,
        )

    logger.info("Pagina Coorte renderizada: %s / %s", metric, cohort_type)


def _render_demo_cohort() -> None:
    st.info("Exibindo dados demonstrativos")
    years = list(range(2018, 2024))
    data = {}
    for i, year in enumerate(years):
        row = [100.0]
        for j in range(1, len(years) - i):
            row.append(round(100 * (0.92 ** j), 1))
        while len(row) < len(years):
            row.append(np.nan)
        data[year] = row

    demo = pd.DataFrame(data, index=range(len(years))).T
    demo.columns = [f"Ano +{i}" for i in range(len(years))]
    st.dataframe(
        demo.style.background_gradient(cmap="RdYlGn", axis=1),
        use_container_width=True,
    )
