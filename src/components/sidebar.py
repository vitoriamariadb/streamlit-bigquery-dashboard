import streamlit as st
import logging
from typing import Optional


logger: logging.Logger = logging.getLogger(__name__)

PAGES: dict[str, str] = {
    "Inicio": "home",
    "KPIs": "kpis",
    "Tendencias": "trends",
    "Segmentacao": "segmentation",
    "Analise de Coorte": "cohort",
    "Funil Educacional": "funnel",
    "Retencao e Evasao": "retention",
    "Editor SQL": "sql_editor",
    "Linhagem de Dados": "data_lineage",
}


def render_sidebar() -> str:
    with st.sidebar:
        st.header("Navegacao")
        st.markdown("---")

        selected_page: str = st.radio(
            label="Selecione a pagina",
            options=list(PAGES.keys()),
            index=0,
            key="nav_radio",
        )

        st.markdown("---")
        st.markdown("### Configuracoes")

        auto_refresh: bool = st.checkbox(
            "Auto-refresh",
            value=False,
            key="auto_refresh",
        )

        if auto_refresh:
            refresh_interval: int = st.slider(
                "Intervalo (segundos)",
                min_value=30,
                max_value=300,
                value=60,
                key="refresh_interval",
            )
            st.caption(f"Atualizando a cada {refresh_interval}s")

        st.markdown("---")

        username = st.session_state.get("username")
        if username:
            st.caption(f"Usuario: {username}")
            if st.button("Sair", key="logout_btn"):
                from src.auth.authenticator import Authenticator
                Authenticator().logout()

        st.markdown("---")
        st.caption("Painel Educação Básica v2.0")

        page_key = PAGES.get(selected_page, "home")
        logger.info("Pagina selecionada: %s", page_key)
        return page_key


def get_current_page() -> str:
    if "nav_radio" not in st.session_state:
        return "home"
    selected = st.session_state.get("nav_radio", "Inicio")
    return PAGES.get(selected, "home")
