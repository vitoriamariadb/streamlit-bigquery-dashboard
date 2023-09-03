import streamlit as st
import logging

from src.config import setup_logging, STREAMLIT_PAGE_TITLE, STREAMLIT_LAYOUT

logger: logging.Logger = setup_logging("panorama")


def configure_page() -> None:
    st.set_page_config(
        page_title=STREAMLIT_PAGE_TITLE,
        page_icon="",
        layout=STREAMLIT_LAYOUT,
        initial_sidebar_state="expanded",
    )


def render_header() -> None:
    st.title(STREAMLIT_PAGE_TITLE)
    st.markdown(
        "Dashboard interativo para analise de indicadores da educacao basica brasileira."
    )


def render_main_content() -> None:
    st.info("Selecione uma pagina no menu lateral para comecar a analise.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Indicadores", value="--", delta=None)
    with col2:
        st.metric(label="Estados", value="27", delta=None)
    with col3:
        st.metric(label="Municipios", value="5.570", delta=None)


def main() -> None:
    configure_page()
    render_header()
    render_main_content()
    logger.info("Aplicacao inicializada")


if __name__ == "__main__":
    main()
