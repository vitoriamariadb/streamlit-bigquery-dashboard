import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import logging
from typing import Optional


logger: logging.Logger = logging.getLogger(__name__)

NATIONAL_BENCHMARKS: dict[str, dict] = {
    "taxa_aprovacao": {"meta_pne": 95.0, "media_nacional": 92.3, "top_10": 97.5},
    "taxa_reprovacao": {"meta_pne": 2.0, "media_nacional": 4.1, "top_10": 1.5},
    "taxa_abandono": {"meta_pne": 0.5, "media_nacional": 1.8, "top_10": 0.3},
    "ideb": {"meta_pne": 6.0, "media_nacional": 5.4, "top_10": 7.2},
}


def calculate_benchmark_position(
    value: float,
    benchmark: dict[str, float],
) -> dict:
    position = "abaixo"
    if value >= benchmark["top_10"]:
        position = "top_10"
    elif value >= benchmark["meta_pne"]:
        position = "acima_meta"
    elif value >= benchmark["media_nacional"]:
        position = "acima_media"

    gap_to_target = round(benchmark["meta_pne"] - value, 2)

    return {
        "posicao": position,
        "gap_meta": gap_to_target,
        "distancia_media": round(value - benchmark["media_nacional"], 2),
    }


def create_benchmark_gauge(
    value: float,
    metric_name: str,
    benchmark: dict[str, float],
) -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        delta={"reference": benchmark["meta_pne"]},
        title={"text": metric_name},
        gauge={
            "axis": {"range": [0, max(benchmark["top_10"] * 1.1, 100)]},
            "bar": {"color": "#2ecc71"},
            "steps": [
                {"range": [0, benchmark["media_nacional"]], "color": "#fadbd8"},
                {"range": [benchmark["media_nacional"], benchmark["meta_pne"]], "color": "#fdebd0"},
                {"range": [benchmark["meta_pne"], benchmark["top_10"]], "color": "#d5f5e3"},
            ],
            "threshold": {
                "line": {"color": "#e74c3c", "width": 4},
                "thickness": 0.75,
                "value": benchmark["meta_pne"],
            },
        },
    ))
    fig.update_layout(height=300, template="plotly_white")
    return fig


def render_benchmarks_section(df: Optional[pd.DataFrame] = None) -> None:
    st.subheader("Benchmarks e Metas")
    st.markdown("Comparacao dos indicadores com metas do PNE e medias nacionais.")

    if df is None or df.empty:
        st.warning("Nenhum dado disponivel.")
        _render_demo_benchmarks()
        return

    cols = st.columns(len(NATIONAL_BENCHMARKS))
    for idx, (metric, benchmark) in enumerate(NATIONAL_BENCHMARKS.items()):
        if metric in df.columns:
            current_value = float(df[metric].iloc[-1])
            fig = create_benchmark_gauge(current_value, metric, benchmark)
            cols[idx].plotly_chart(fig, use_container_width=True)

            position = calculate_benchmark_position(current_value, benchmark)
            cols[idx].caption(f"Posicao: {position['posicao']} | Gap: {position['gap_meta']:+.1f}")

    logger.info("Benchmarks renderizados")


def _render_demo_benchmarks() -> None:
    st.info("Exibindo dados demonstrativos")
    demo_values = {
        "taxa_aprovacao": 92.3,
        "taxa_reprovacao": 4.1,
        "taxa_abandono": 1.8,
        "ideb": 5.4,
    }
    cols = st.columns(len(demo_values))
    for idx, (metric, value) in enumerate(demo_values.items()):
        benchmark = NATIONAL_BENCHMARKS[metric]
        fig = create_benchmark_gauge(value, metric.replace("_", " ").title(), benchmark)
        cols[idx].plotly_chart(fig, use_container_width=True)
