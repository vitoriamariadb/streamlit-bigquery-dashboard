import streamlit as st
import logging

from src.config import setup_logging, STREAMLIT_PAGE_TITLE, STREAMLIT_LAYOUT
from src.components.sidebar import render_sidebar, PAGES
from src.components.filters import render_filters, apply_filters
from src.pages.kpis import render_kpis_page
from src.pages.trends import render_trends_page
from src.pages.segmentation import render_segmentation_page
from src.pages.cohort import render_cohort_page
from src.pages.funnel import render_funnel_page
from src.pages.retention import render_retention_page
from src.auth.authenticator import Authenticator

logger: logging.Logger = setup_logging("painel_educacao")

PAGE_REGISTRY: dict[str, dict] = {
    "home": {"titulo": "Inicio", "render": None},
    "kpis": {"titulo": "KPIs", "render": render_kpis_page},
    "trends": {"titulo": "Tendencias", "render": render_trends_page},
    "segmentation": {"titulo": "Segmentacao", "render": render_segmentation_page},
    "cohort": {"titulo": "Analise de Coorte", "render": render_cohort_page},
    "funnel": {"titulo": "Funil Educacional", "render": render_funnel_page},
    "retention": {"titulo": "Retencao e Evasao", "render": render_retention_page},
}


def configure_page() -> None:
    st.set_page_config(
        page_title=STREAMLIT_PAGE_TITLE,
        page_icon="",
        layout=STREAMLIT_LAYOUT,
        initial_sidebar_state="expanded",
    )


def render_home() -> None:
    st.title(STREAMLIT_PAGE_TITLE)
    st.markdown(
        "Dashboard interativo para analise de indicadores da educacao basica brasileira."
    )
    st.markdown("---")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Indicadores", value="15+")
    with col2:
        st.metric(label="Estados", value="27")
    with col3:
        st.metric(label="Municipios", value="5.570")
    with col4:
        st.metric(label="Anos de Dados", value="2005-2023")

    st.markdown("---")
    st.subheader("Paginas Disponiveis")

    features = [
        ("KPIs", "Indicadores chave com metas e deltas"),
        ("Tendencias", "Evolucao temporal dos indicadores"),
        ("Segmentacao", "Comparativos regionais e por rede"),
        ("Coorte", "Acompanhamento de grupos ao longo do tempo"),
        ("Funil", "Fluxo de alunos da matricula a conclusao"),
        ("Retencao", "Taxas de retencao e evasao escolar"),
    ]

    cols = st.columns(3)
    for idx, (name, desc) in enumerate(features):
        with cols[idx % 3]:
            st.markdown(f"**{name}**")
            st.caption(desc)


def main() -> None:
    configure_page()

    auth = Authenticator()
    if not auth.require_auth():
        auth.render_login_form()
        return

    current_page: str = render_sidebar()

    if current_page == "home":
        render_home()
    elif current_page in PAGE_REGISTRY:
        page_config = PAGE_REGISTRY[current_page]
        st.header(page_config["titulo"])

        filters = render_filters()

        if page_config["render"]:
            page_config["render"]()
    else:
        st.error(f"Pagina nao encontrada: {current_page}")

    logger.info("Pagina renderizada: %s", current_page)


if __name__ == "__main__":
    main()
