import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import logging
from typing import Optional


logger: logging.Logger = logging.getLogger(__name__)


def linear_forecast(
    series: pd.Series,
    periods_ahead: int = 3,
) -> dict:
    x = np.arange(len(series))
    y = series.values.astype(float)

    mask = ~np.isnan(y)
    if mask.sum() < 2:
        return {"forecast": [], "slope": 0.0, "intercept": 0.0, "r_squared": 0.0}

    x_clean, y_clean = x[mask], y[mask]
    coefficients = np.polyfit(x_clean, y_clean, 1)
    slope, intercept = coefficients

    y_pred = np.polyval(coefficients, x_clean)
    ss_res = np.sum((y_clean - y_pred) ** 2)
    ss_tot = np.sum((y_clean - np.mean(y_clean)) ** 2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

    future_x = np.arange(len(series), len(series) + periods_ahead)
    forecast_values = np.polyval(coefficients, future_x)

    return {
        "forecast": forecast_values.tolist(),
        "slope": round(float(slope), 4),
        "intercept": round(float(intercept), 4),
        "r_squared": round(float(r_squared), 4),
    }


def moving_average_forecast(
    series: pd.Series,
    window: int = 3,
    periods_ahead: int = 3,
) -> list[float]:
    ma = series.rolling(window=window).mean()
    last_ma = float(ma.iloc[-1]) if not ma.empty else 0.0

    trend = 0.0
    if len(ma.dropna()) > 1:
        trend = float(ma.dropna().diff().mean())

    forecast = [round(last_ma + trend * (i + 1), 2) for i in range(periods_ahead)]
    return forecast


def create_forecast_chart(
    historical: pd.DataFrame,
    year_col: str,
    value_col: str,
    forecast_years: list[int],
    forecast_values: list[float],
    title: str = "",
) -> go.Figure:
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=historical[year_col],
        y=historical[value_col],
        mode="lines+markers",
        name="Historico",
        line=dict(color="#3498db"),
    ))

    fig.add_trace(go.Scatter(
        x=forecast_years,
        y=forecast_values,
        mode="lines+markers",
        name="Projecao",
        line=dict(color="#e74c3c", dash="dash"),
    ))

    fig.update_layout(
        title=title,
        template="plotly_white",
        height=450,
        xaxis_title="Ano",
        yaxis_title="Valor",
    )
    return fig


def render_forecasting_section(df: Optional[pd.DataFrame] = None) -> None:
    st.subheader("Projecoes e Previsoes")
    st.markdown("Projecoes baseadas em tendencias historicas dos indicadores.")

    col1, col2 = st.columns(2)
    with col1:
        metric: str = st.selectbox(
            "Indicador",
            options=["Taxa de Aprovacao", "IDEB", "Taxa de Abandono"],
            key="forecast_metric",
        )
    with col2:
        periods: int = st.slider(
            "Anos a projetar",
            min_value=1,
            max_value=5,
            value=3,
            key="forecast_periods",
        )

    metric_map = {
        "Taxa de Aprovacao": "taxa_aprovacao",
        "IDEB": "ideb",
        "Taxa de Abandono": "taxa_abandono",
    }
    value_col = metric_map.get(metric, "taxa_aprovacao")

    if df is None or df.empty:
        st.warning("Nenhum dado disponivel.")
        _render_demo_forecast(metric, value_col, periods)
        return

    if value_col in df.columns and "ano" in df.columns:
        result = linear_forecast(df[value_col], periods)
        last_year = int(df["ano"].max())
        forecast_years = list(range(last_year + 1, last_year + periods + 1))

        fig = create_forecast_chart(df, "ano", value_col, forecast_years, result["forecast"], metric)
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"R-quadrado: {result['r_squared']:.4f} | Tendencia: {result['slope']:+.4f}/ano")

    logger.info("Projecao renderizada: %s (%d periodos)", metric, periods)


def _render_demo_forecast(metric: str, value_col: str, periods: int) -> None:
    st.info("Exibindo dados demonstrativos")
    demo = pd.DataFrame({
        "ano": list(range(2015, 2024)),
        "taxa_aprovacao": [88.5, 89.1, 89.8, 90.2, 91.0, 91.5, 92.0, 92.3, 92.8],
        "ideb": [4.5, 4.7, 4.9, 5.0, 5.2, 5.3, 5.4, 5.4, 5.6],
        "taxa_abandono": [4.3, 4.1, 3.9, 3.9, 3.6, 3.5, 3.5, 1.8, 1.5],
    })
    result = linear_forecast(demo[value_col], periods)
    forecast_years = list(range(2024, 2024 + periods))
    fig = create_forecast_chart(demo, "ano", value_col, forecast_years, result["forecast"], metric)
    st.plotly_chart(fig, use_container_width=True)
    st.caption(f"R-quadrado: {result['r_squared']:.4f}")
