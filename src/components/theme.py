import streamlit as st
import logging
from typing import Optional
from dataclasses import dataclass


logger: logging.Logger = logging.getLogger(__name__)


@dataclass
class ThemeConfig:
    """Configuracao de tema do dashboard."""

    name: str
    primary_color: str
    background_color: str
    secondary_bg_color: str
    text_color: str
    font: str
    chart_palette: list[str]


THEMES: dict[str, ThemeConfig] = {
    "padrao": ThemeConfig(
        name="Padrao",
        primary_color="#2ecc71",
        background_color="#ffffff",
        secondary_bg_color="#f0f2f6",
        text_color="#262730",
        font="sans serif",
        chart_palette=["#2ecc71", "#3498db", "#e74c3c", "#f39c12", "#9b59b6"],
    ),
    "escuro": ThemeConfig(
        name="Escuro",
        primary_color="#1abc9c",
        background_color="#1e1e1e",
        secondary_bg_color="#2d2d2d",
        text_color="#e0e0e0",
        font="sans serif",
        chart_palette=["#1abc9c", "#3498db", "#e74c3c", "#f39c12", "#9b59b6"],
    ),
    "institucional": ThemeConfig(
        name="Institucional",
        primary_color="#003366",
        background_color="#ffffff",
        secondary_bg_color="#f5f5f5",
        text_color="#333333",
        font="serif",
        chart_palette=["#003366", "#006699", "#0099cc", "#66ccff", "#99ddff"],
    ),
    "acessivel": ThemeConfig(
        name="Acessivel (Alto Contraste)",
        primary_color="#0000ff",
        background_color="#ffffff",
        secondary_bg_color="#f0f0f0",
        text_color="#000000",
        font="sans serif",
        chart_palette=["#0000ff", "#ff0000", "#008000", "#ff8c00", "#800080"],
    ),
}


def get_current_theme() -> ThemeConfig:
    theme_name = st.session_state.get("selected_theme", "padrao")
    return THEMES.get(theme_name, THEMES["padrao"])


def render_theme_selector() -> ThemeConfig:
    selected: str = st.selectbox(
        "Tema",
        options=list(THEMES.keys()),
        format_func=lambda x: THEMES[x].name,
        key="selected_theme",
    )

    theme = THEMES[selected]

    st.markdown(
        f"""
        <style>
        .stApp {{
            font-family: {theme.font};
        }}
        .metric-card {{
            background-color: {theme.secondary_bg_color};
            border-left: 4px solid {theme.primary_color};
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 0.5rem;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    logger.info("Tema selecionado: %s", theme.name)
    return theme


def get_chart_colors(theme: Optional[ThemeConfig] = None) -> list[str]:
    if theme is None:
        theme = get_current_theme()
    return theme.chart_palette


def apply_chart_theme(fig, theme: Optional[ThemeConfig] = None) -> None:
    if theme is None:
        theme = get_current_theme()

    fig.update_layout(
        font=dict(family=theme.font, color=theme.text_color),
        plot_bgcolor=theme.background_color,
        paper_bgcolor=theme.background_color,
    )

