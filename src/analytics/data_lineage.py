import streamlit as st
import logging
from typing import Optional
from dataclasses import dataclass, field


logger: logging.Logger = logging.getLogger(__name__)


@dataclass
class DataSource:
    """Representacao de uma fonte de dados no lineage."""

    name: str
    source_type: str
    location: str
    description: str
    fields: list[str] = field(default_factory=list)
    refresh_frequency: str = "diario"


@dataclass
class Transformation:
    """Representacao de uma transformacao no pipeline."""

    name: str
    description: str
    input_sources: list[str]
    output_name: str
    transformation_type: str = "sql"


DATA_SOURCES: list[DataSource] = [
    DataSource(
        name="censo_escolar",
        source_type="bigquery",
        location="projeto.dataset.censo_escolar",
        description="Microdados do Censo Escolar",
        fields=["ano", "cod_escola", "matriculas", "docentes", "turmas"],
        refresh_frequency="anual",
    ),
    DataSource(
        name="ideb",
        source_type="bigquery",
        location="projeto.dataset.ideb",
        description="Indice de Desenvolvimento da Educacao Basica",
        fields=["ano", "sigla_uf", "municipio", "ideb_ai", "ideb_af"],
        refresh_frequency="bienal",
    ),
    DataSource(
        name="indicadores_fluxo",
        source_type="bigquery",
        location="projeto.dataset.indicadores_fluxo",
        description="Taxas de aprovacao, reprovacao e abandono",
        fields=["ano", "sigla_uf", "taxa_aprovacao", "taxa_reprovacao", "taxa_abandono"],
        refresh_frequency="anual",
    ),
    DataSource(
        name="pnad_educacao",
        source_type="bigquery",
        location="projeto.dataset.pnad_educacao",
        description="Dados educacionais da PNAD Continua",
        fields=["ano", "trimestre", "taxa_analfabetismo", "escolaridade_media"],
        refresh_frequency="trimestral",
    ),
]

TRANSFORMATIONS: list[Transformation] = [
    Transformation(
        name="educacao_consolidado",
        description="Consolidação dos indicadores educacionais por UF e ano",
        input_sources=["censo_escolar", "ideb", "indicadores_fluxo"],
        output_name="educacao_estadual",
    ),
    Transformation(
        name="educacao_municipal",
        description="Detalhamento municipal dos indicadores",
        input_sources=["censo_escolar", "ideb"],
        output_name="educacao_municipal",
    ),
]


def render_lineage_page() -> None:
    st.header("Linhagem de Dados")
    st.markdown("Rastreabilidade das fontes e transformacoes dos dados exibidos no dashboard.")

    tab1, tab2 = st.tabs(["Fontes de Dados", "Transformacoes"])

    with tab1:
        for source in DATA_SOURCES:
            with st.expander(f"{source.name} ({source.source_type})"):
                st.markdown(f"**Descricao:** {source.description}")
                st.markdown(f"**Localizacao:** `{source.location}`")
                st.markdown(f"**Frequencia de atualizacao:** {source.refresh_frequency}")
                st.markdown(f"**Campos:** {', '.join(source.fields)}")

    with tab2:
        for transform in TRANSFORMATIONS:
            with st.expander(transform.name):
                st.markdown(f"**Descricao:** {transform.description}")
                st.markdown(f"**Entradas:** {', '.join(transform.input_sources)}")
                st.markdown(f"**Saida:** {transform.output_name}")
                st.markdown(f"**Tipo:** {transform.transformation_type}")

    logger.info("Pagina Data Lineage renderizada")


def get_source_by_name(name: str) -> Optional[DataSource]:
    for source in DATA_SOURCES:
        if source.name == name:
            return source
    return None
