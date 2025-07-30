import streamlit as st
import pandas as pd
import logging
from typing import Optional


logger: logging.Logger = logging.getLogger(__name__)

TREND_METRICS: list[dict] = [
    {"nome": "Taxa de Aprovacao", "coluna": "taxa_aprovacao", "cor": "#2ecc71"},
    {"nome": "Taxa de Reprovacao", "coluna": "taxa_reprovacao", "cor": "#e74c3c"},
    {"nome": "Taxa de Abandono", "coluna": "taxa_abandono", "cor": "#f39c12"},
    {"nome": "IDEB", "coluna": "ideb", "cor": "#3498db"},
    {"nome": "Matriculas", "coluna": "total_matriculas", "cor": "#9b59b6"},
]


def calculate_trend(series: pd.Series) -> dict:
    if len(series) < 2:
        return {"direcao": "estavel", "variacao": 0.0}
    diff = series.iloc[-1] - series.iloc[0]
    pct = (diff / series.iloc[0] * 100) if series.iloc[0] != 0 else 0
    direcao = "crescente" if diff > 0 else "decrescente" if diff < 0 else "estavel"
    return {"direcao": direcao, "variacao": round(pct, 2)}


def render_trends_page(df: Optional[pd.DataFrame] = None) -> None:
    st.header("Tendencias")
    st.markdown("Evolucao temporal dos indicadores educacionais.")

    selected_metrics: list[str] = st.multiselect(
        "Selecione os indicadores",
        options=[m["nome"] for m in TREND_METRICS],
        default=[TREND_METRICS[0]["nome"]],
        key="trend_metrics",
    )

    granularity: str = st.selectbox(
        "Granularidade",
        options=["Anual", "Semestral", "Mensal"],
        index=0,
        key="trend_granularity",
    )

    if df is None or df.empty:
        st.warning("Nenhum dado disponivel. Conecte-se ao BigQuery.")
        _render_demo_trends(selected_metrics)
        return

    for metric in TREND_METRICS:
        if metric["nome"] in selected_metrics and metric["coluna"] in df.columns:
            trend = calculate_trend(df[metric["coluna"]])
            st.subheader(metric["nome"])
            st.line_chart(df.set_index("ano")[metric["coluna"]])
            st.caption(
                f"Tendencia: {trend['direcao']} ({trend['variacao']:+.1f}%)"
            )

    logger.info("Pagina Tendencias renderizada: %s", selected_metrics)


def _render_demo_trends(selected: list[str]) -> None:
    st.info("Exibindo dados demonstrativos")
    demo_data = pd.DataFrame({
        "ano": list(range(2015, 2024)),
        "taxa_aprovacao": [88.5, 89.1, 89.8, 90.2, 91.0, 91.5, 92.0, 92.3, 92.8],
        "taxa_reprovacao": [7.2, 6.8, 6.3, 5.9, 5.4, 5.0, 4.5, 4.1, 3.8],
        "taxa_abandono": [4.3, 4.1, 3.9, 3.9, 3.6, 3.5, 3.5, 1.8, 1.5],
        "ideb": [4.5, 4.7, 4.9, 5.0, 5.2, 5.3, 5.4, 5.4, 5.6],
        "total_matriculas": [48e6, 47.5e6, 47e6, 46.5e6, 46e6, 45.5e6, 45e6, 44.8e6, 44.5e6],
    })
    for metric in TREND_METRICS:
        if metric["nome"] in selected:
            st.subheader(metric["nome"])
            st.line_chart(demo_data.set_index("ano")[metric["coluna"]])
