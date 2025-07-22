import streamlit as st
import pandas as pd
import logging
from typing import Optional


logger: logging.Logger = logging.getLogger(__name__)


KPI_DEFINITIONS: list[dict] = [
    {
        "nome": "Taxa de Aprovacao",
        "descricao": "Percentual de alunos aprovados no ano letivo",
        "coluna": "taxa_aprovacao",
        "formato": "{:.1f}%",
        "meta": 95.0,
    },
    {
        "nome": "Taxa de Reprovacao",
        "descricao": "Percentual de alunos reprovados no ano letivo",
        "coluna": "taxa_reprovacao",
        "formato": "{:.1f}%",
        "meta": 3.0,
    },
    {
        "nome": "Taxa de Abandono",
        "descricao": "Percentual de alunos que abandonaram a escola",
        "coluna": "taxa_abandono",
        "formato": "{:.1f}%",
        "meta": 1.0,
    },
    {
        "nome": "IDEB",
        "descricao": "Indice de Desenvolvimento da Educacao Basica",
        "coluna": "ideb",
        "formato": "{:.1f}",
        "meta": 6.0,
    },
]


def calculate_delta(current: float, previous: float) -> Optional[float]:
    if previous == 0:
        return None
    return round(current - previous, 2)


def render_kpi_card(
    col: st.delta_generator.DeltaGenerator,
    nome: str,
    valor_atual: float,
    valor_anterior: Optional[float] = None,
    formato: str = "{:.1f}",
    meta: Optional[float] = None,
) -> None:
    delta = None
    if valor_anterior is not None:
        delta = calculate_delta(valor_atual, valor_anterior)

    col.metric(
        label=nome,
        value=formato.format(valor_atual),
        delta=f"{delta:+.2f}" if delta is not None else None,
    )

    if meta is not None:
        progress = min(valor_atual / meta, 1.0) if meta > 0 else 0
        col.progress(progress)
        col.caption(f"Meta: {formato.format(meta)}")


def render_kpis_page(df: Optional[pd.DataFrame] = None) -> None:
    st.header("Indicadores Chave (KPIs)")
    st.markdown("Visao consolidada dos principais indicadores educacionais.")

    if df is None or df.empty:
        st.warning("Nenhum dado disponivel. Conecte-se ao BigQuery para carregar os dados.")
        _render_demo_kpis()
        return

    cols = st.columns(len(KPI_DEFINITIONS))
    for idx, kpi in enumerate(KPI_DEFINITIONS):
        if kpi["coluna"] in df.columns:
            valor = df[kpi["coluna"]].iloc[-1]
            anterior = df[kpi["coluna"]].iloc[-2] if len(df) > 1 else None
            render_kpi_card(
                cols[idx],
                kpi["nome"],
                valor,
                anterior,
                kpi["formato"],
                kpi["meta"],
            )

    logger.info("Pagina KPIs renderizada com %d indicadores", len(KPI_DEFINITIONS))


def _render_demo_kpis() -> None:
    st.info("Exibindo dados demonstrativos")
    cols = st.columns(4)
    demo_values = [92.3, 4.1, 1.8, 5.4]
    for idx, kpi in enumerate(KPI_DEFINITIONS):
        render_kpi_card(
            cols[idx],
            kpi["nome"],
            demo_values[idx],
            formato=kpi["formato"],
            meta=kpi["meta"],
        )
