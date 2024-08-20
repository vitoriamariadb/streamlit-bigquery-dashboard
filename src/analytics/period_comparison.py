import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import logging
from typing import Optional


logger: logging.Logger = logging.getLogger(__name__)


def compare_periods(
    df: pd.DataFrame,
    period_col: str,
    metric_cols: list[str],
    period_a: int,
    period_b: int,
) -> pd.DataFrame:
    df_a = df[df[period_col] == period_a][metric_cols].mean()
    df_b = df[df[period_col] == period_b][metric_cols].mean()

    comparison = pd.DataFrame({
        f"Periodo {period_a}": df_a,
        f"Periodo {period_b}": df_b,
        "Variacao Absoluta": (df_b - df_a).round(2),
        "Variacao Percentual": (((df_b - df_a) / df_a) * 100).round(2),
    })

    return comparison


def create_comparison_chart(
    comparison: pd.DataFrame,
    title: str = "Comparacao entre Periodos",
) -> go.Figure:
    metrics = comparison.index.tolist()
    col_a = comparison.columns[0]
    col_b = comparison.columns[1]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name=col_a,
        x=metrics,
        y=comparison[col_a].values,
        marker_color="#3498db",
    ))
    fig.add_trace(go.Bar(
        name=col_b,
        x=metrics,
        y=comparison[col_b].values,
        marker_color="#2ecc71",
    ))

    fig.update_layout(
        title=title,
        barmode="group",
        template="plotly_white",
        height=450,
    )
    return fig


def render_comparison_section(df: Optional[pd.DataFrame] = None) -> None:
    st.subheader("Comparacao entre Periodos")

    if df is None or df.empty:
        st.warning("Nenhum dado disponivel.")
        _render_demo_comparison()
        return

    available_years = sorted(df["ano"].unique()) if "ano" in df.columns else []
    if len(available_years) < 2:
        st.info("Necessarios pelo menos 2 anos para comparacao.")
        return

    col1, col2 = st.columns(2)
    with col1:
        year_a: int = st.selectbox(
            "Periodo A",
            options=available_years,
            index=0,
            key="comp_year_a",
        )
    with col2:
        year_b: int = st.selectbox(
            "Periodo B",
            options=[y for y in available_years if y != year_a],
            index=min(1, len(available_years) - 2),
            key="comp_year_b",
        )

    numeric_cols = df.select_dtypes(include=["float64", "int64"]).columns.tolist()
    metric_cols = [c for c in numeric_cols if c != "ano"]

    if metric_cols:
        comparison = compare_periods(df, "ano", metric_cols, year_a, year_b)
        fig = create_comparison_chart(comparison, f"Comparacao {year_a} vs {year_b}")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(comparison, use_container_width=True)

    logger.info("Comparacao renderizada: %d vs %d", year_a, year_b)


def _render_demo_comparison() -> None:
    st.info("Exibindo dados demonstrativos")
    demo = pd.DataFrame({
        "Periodo 2022": [91.5, 4.5, 2.0, 5.3],
        "Periodo 2023": [92.8, 3.8, 1.5, 5.6],
        "Variacao Absoluta": [1.3, -0.7, -0.5, 0.3],
        "Variacao Percentual": [1.42, -15.56, -25.0, 5.66],
    }, index=["Taxa Aprovacao", "Taxa Reprovacao", "Taxa Abandono", "IDEB"])
    st.dataframe(demo, use_container_width=True)

