import streamlit as st
import pandas as pd
import logging
from typing import Optional


logger: logging.Logger = logging.getLogger(__name__)

ESTADOS_BR: list[str] = [
    "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA",
    "MG", "MS", "MT", "PA", "PB", "PE", "PI", "PR", "RJ", "RN",
    "RO", "RR", "RS", "SC", "SE", "SP", "TO",
]

REGIOES_BR: dict[str, list[str]] = {
    "Norte": ["AC", "AM", "AP", "PA", "RO", "RR", "TO"],
    "Nordeste": ["AL", "BA", "CE", "MA", "PB", "PE", "PI", "RN", "SE"],
    "Centro-Oeste": ["DF", "GO", "MS", "MT"],
    "Sudeste": ["ES", "MG", "RJ", "SP"],
    "Sul": ["PR", "RS", "SC"],
}

DEPENDENCIAS: list[str] = ["Federal", "Estadual", "Municipal", "Privada"]
ETAPAS: list[str] = [
    "Educacao Infantil",
    "Ensino Fundamental - Anos Iniciais",
    "Ensino Fundamental - Anos Finais",
    "Ensino Medio",
]


class FilterState:
    """Estado centralizado dos filtros aplicados."""

    def __init__(self):
        self.estados: list[str] = []
        self.regioes: list[str] = []
        self.dependencias: list[str] = []
        self.etapas: list[str] = []
        self.ano_inicio: Optional[int] = None
        self.ano_fim: Optional[int] = None

    def to_dict(self) -> dict:
        return {
            "estados": self.estados,
            "regioes": self.regioes,
            "dependencias": self.dependencias,
            "etapas": self.etapas,
            "ano_inicio": self.ano_inicio,
            "ano_fim": self.ano_fim,
        }


def render_filters(available_years: Optional[list[int]] = None) -> FilterState:
    state = FilterState()

    with st.expander("Filtros", expanded=True):
        col1, col2 = st.columns(2)

        with col1:
            state.regioes = st.multiselect(
                "Regioes",
                options=list(REGIOES_BR.keys()),
                key="filter_regioes",
            )

            available_estados = ESTADOS_BR
            if state.regioes:
                available_estados = []
                for r in state.regioes:
                    available_estados.extend(REGIOES_BR.get(r, []))

            state.estados = st.multiselect(
                "Estados",
                options=sorted(available_estados),
                key="filter_estados",
            )

        with col2:
            state.dependencias = st.multiselect(
                "Dependencia Administrativa",
                options=DEPENDENCIAS,
                key="filter_dependencias",
            )

            state.etapas = st.multiselect(
                "Etapa de Ensino",
                options=ETAPAS,
                key="filter_etapas",
            )

    logger.info("Filtros aplicados: %s", state.to_dict())
    return state


def apply_filters(df: pd.DataFrame, filters: FilterState) -> pd.DataFrame:
    filtered = df.copy()

    if filters.estados and "sigla_uf" in filtered.columns:
        filtered = filtered[filtered["sigla_uf"].isin(filters.estados)]

    if filters.dependencias and "dependencia_administrativa" in filtered.columns:
        filtered = filtered[
            filtered["dependencia_administrativa"].isin(filters.dependencias)
        ]

    if filters.etapas and "etapa_ensino" in filtered.columns:
        filtered = filtered[filtered["etapa_ensino"].isin(filters.etapas)]

    if filters.ano_inicio and "ano" in filtered.columns:
        filtered = filtered[filtered["ano"] >= filters.ano_inicio]

    if filters.ano_fim and "ano" in filtered.columns:
        filtered = filtered[filtered["ano"] <= filters.ano_fim]

    logger.info(
        "Filtro aplicado: %d -> %d linhas", len(df), len(filtered)
    )
    return filtered
