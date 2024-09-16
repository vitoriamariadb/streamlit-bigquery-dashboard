import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import logging
from typing import Optional


logger: logging.Logger = logging.getLogger(__name__)

COLOR_PALETTE: list[str] = [
    "#2ecc71", "#3498db", "#e74c3c", "#f39c12", "#9b59b6",
    "#1abc9c", "#e67e22", "#34495e", "#16a085", "#c0392b",
]

CHART_TEMPLATE: str = "plotly_white"


def create_line_chart(
    df: pd.DataFrame,
    x: str,
    y: str | list[str],
    title: str = "",
    height: int = 400,
) -> go.Figure:
    if isinstance(y, str):
        y = [y]

    fig = go.Figure()
    for idx, col in enumerate(y):
        if col in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df[x],
                    y=df[col],
                    mode="lines+markers",
                    name=col,
                    line=dict(color=COLOR_PALETTE[idx % len(COLOR_PALETTE)]),
                )
            )

    fig.update_layout(
        title=title,
        template=CHART_TEMPLATE,
        height=height,
        xaxis_title=x,
        yaxis_title="Valor",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    return fig


def create_bar_chart(
    df: pd.DataFrame,
    x: str,
    y: str,
    title: str = "",
    color: Optional[str] = None,
    height: int = 400,
    orientation: str = "v",
) -> go.Figure:
    fig = px.bar(
        df,
        x=x if orientation == "v" else y,
        y=y if orientation == "v" else x,
        color=color,
        title=title,
        template=CHART_TEMPLATE,
        height=height,
        orientation=orientation,
        color_discrete_sequence=COLOR_PALETTE,
    )
    return fig


def create_pie_chart(
    df: pd.DataFrame,
    values: str,
    names: str,
    title: str = "",
    height: int = 400,
) -> go.Figure:
    fig = px.pie(
        df,
        values=values,
        names=names,
        title=title,
        template=CHART_TEMPLATE,
        height=height,
        color_discrete_sequence=COLOR_PALETTE,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    return fig


def create_heatmap(
    df: pd.DataFrame,
    x: str,
    y: str,
    values: str,
    title: str = "",
    height: int = 500,
) -> go.Figure:
    pivot = df.pivot_table(index=y, columns=x, values=values, aggfunc="mean")
    fig = go.Figure(
        data=go.Heatmap(
            z=pivot.values,
            x=pivot.columns.tolist(),
            y=pivot.index.tolist(),
            colorscale="RdYlGn",
        )
    )
    fig.update_layout(
        title=title,
        template=CHART_TEMPLATE,
        height=height,
    )
    return fig


def render_chart(fig: go.Figure, key: Optional[str] = None) -> None:
    st.plotly_chart(fig, use_container_width=True, key=key)
    logger.debug("Grafico renderizado")

