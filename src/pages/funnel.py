import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import logging
from typing import Optional


logger: logging.Logger = logging.getLogger(__name__)

FUNNEL_STAGES: list[dict] = [
    {"nome": "Matriculas Iniciais", "coluna": "matriculas_iniciais"},
    {"nome": "Frequencia Regular", "coluna": "frequencia_regular"},
    {"nome": "Aprovados", "coluna": "aprovados"},
    {"nome": "Progresso Etapa", "coluna": "progresso_etapa"},
    {"nome": "Conclusao", "coluna": "conclusao"},
]


def calculate_funnel_rates(values: list[float]) -> list[dict]:
    rates = []
    for i, val in enumerate(values):
        rate_from_start = (val / values[0] * 100) if values[0] > 0 else 0
        rate_from_prev = (val / values[i - 1] * 100) if i > 0 and values[i - 1] > 0 else 100
        rates.append({
            "valor": val,
            "taxa_inicio": round(rate_from_start, 1),
            "taxa_anterior": round(rate_from_prev, 1),
        })
    return rates


def create_funnel_chart(
    stages: list[str],
    values: list[float],
    title: str = "Funil Educacional",
) -> go.Figure:
    fig = go.Figure(
        go.Funnel(
            y=stages,
            x=values,
            textposition="inside",
            textinfo="value+percent initial",
            marker=dict(
                color=["#2ecc71", "#3498db", "#f39c12", "#e67e22", "#e74c3c"],
            ),
        )
    )
    fig.update_layout(
        title=title,
        template="plotly_white",
        height=500,
    )
    return fig


def render_funnel_page(df: Optional[pd.DataFrame] = None) -> None:
    st.header("Funil Educacional")
    st.markdown(
        "Visualizacao do fluxo de alunos desde a matricula "
        "ate a conclusao da etapa de ensino."
    )

    col1, col2 = st.columns(2)
    with col1:
        etapa: str = st.selectbox(
            "Etapa de Ensino",
            options=[
                "Ensino Fundamental - Anos Iniciais",
                "Ensino Fundamental - Anos Finais",
                "Ensino Medio",
            ],
            key="funnel_etapa",
        )
    with col2:
        ano: int = st.selectbox(
            "Ano",
            options=list(range(2023, 2014, -1)),
            key="funnel_ano",
        )

    if df is None or df.empty:
        st.warning("Nenhum dado disponivel.")
        _render_demo_funnel()
        return

    stages = [s["nome"] for s in FUNNEL_STAGES]
    values = []
    for stage in FUNNEL_STAGES:
        if stage["coluna"] in df.columns:
            values.append(float(df[stage["coluna"]].sum()))

    if values:
        fig = create_funnel_chart(stages[:len(values)], values)
        st.plotly_chart(fig, use_container_width=True)

        rates = calculate_funnel_rates(values)
        rate_df = pd.DataFrame(rates, index=stages[:len(values)])
        st.dataframe(rate_df, use_container_width=True)

    logger.info("Pagina Funil renderizada: %s / %d", etapa, ano)


def _render_demo_funnel() -> None:
    st.info("Exibindo dados demonstrativos")
    stages = [s["nome"] for s in FUNNEL_STAGES]
    values = [100000, 92000, 85000, 78000, 72000]
    fig = create_funnel_chart(stages, values)
    st.plotly_chart(fig, use_container_width=True)

    rates = calculate_funnel_rates(values)
    rate_df = pd.DataFrame(rates, index=stages)
    st.dataframe(rate_df, use_container_width=True)
