import streamlit as st
import pandas as pd
import logging
from typing import Optional


logger: logging.Logger = logging.getLogger(__name__)

SEGMENTATION_DIMENSIONS: list[dict] = [
    {"nome": "Regiao", "coluna": "regiao"},
    {"nome": "UF", "coluna": "sigla_uf"},
    {"nome": "Dependencia Administrativa", "coluna": "dependencia_administrativa"},
    {"nome": "Localizacao", "coluna": "localizacao"},
    {"nome": "Etapa de Ensino", "coluna": "etapa_ensino"},
]


def compute_segment_stats(df: pd.DataFrame, segment_col: str, metric_col: str) -> pd.DataFrame:
    stats = df.groupby(segment_col)[metric_col].agg(
        ["mean", "median", "std", "min", "max", "count"]
    ).round(2)
    stats.columns = ["Media", "Mediana", "Desvio Padrao", "Minimo", "Maximo", "Contagem"]
    return stats.sort_values("Media", ascending=False)


def render_segmentation_page(df: Optional[pd.DataFrame] = None) -> None:
    st.header("Segmentacao")
    st.markdown("Analise comparativa entre diferentes segmentos educacionais.")

    col1, col2 = st.columns(2)
    with col1:
        dimension: str = st.selectbox(
            "Dimensao de segmentacao",
            options=[d["nome"] for d in SEGMENTATION_DIMENSIONS],
            index=0,
            key="seg_dimension",
        )
    with col2:
        metric: str = st.selectbox(
            "Indicador",
            options=["Taxa de Aprovacao", "IDEB", "Taxa de Abandono"],
            index=0,
            key="seg_metric",
        )

    metric_map = {
        "Taxa de Aprovacao": "taxa_aprovacao",
        "IDEB": "ideb",
        "Taxa de Abandono": "taxa_abandono",
    }
    metric_col = metric_map.get(metric, "taxa_aprovacao")

    dim_col = next(
        (d["coluna"] for d in SEGMENTATION_DIMENSIONS if d["nome"] == dimension),
        "regiao",
    )

    if df is None or df.empty:
        st.warning("Nenhum dado disponivel. Conecte-se ao BigQuery.")
        _render_demo_segmentation()
        return

    if dim_col in df.columns and metric_col in df.columns:
        stats = compute_segment_stats(df, dim_col, metric_col)
        st.dataframe(stats, use_container_width=True)
        st.bar_chart(stats["Media"])

    logger.info("Pagina Segmentacao renderizada: %s x %s", dimension, metric)


def _render_demo_segmentation() -> None:
    st.info("Exibindo dados demonstrativos")
    demo = pd.DataFrame({
        "Regiao": ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"],
        "Media": [87.2, 88.5, 91.3, 93.1, 94.0],
        "Mediana": [87.0, 88.0, 91.0, 93.0, 94.0],
        "Contagem": [450, 1800, 480, 1680, 1190],
    })
    st.dataframe(demo, use_container_width=True)
    st.bar_chart(demo.set_index("Regiao")["Media"])
