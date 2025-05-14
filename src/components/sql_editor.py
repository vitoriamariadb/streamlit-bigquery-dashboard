import streamlit as st
import pandas as pd
import logging
import re
from typing import Optional
from datetime import datetime


logger: logging.Logger = logging.getLogger(__name__)

BLOCKED_KEYWORDS: list[str] = [
    "DROP", "DELETE", "TRUNCATE", "ALTER", "CREATE", "INSERT",
    "UPDATE", "GRANT", "REVOKE", "EXEC", "EXECUTE",
]

QUERY_TEMPLATES: dict[str, str] = {
    "Matriculas por UF": (
        "SELECT sigla_uf, SUM(total_matriculas) AS total\n"
        "FROM `projeto.dataset.censo_escolar`\n"
        "WHERE ano = 2023\n"
        "GROUP BY sigla_uf\n"
        "ORDER BY total DESC"
    ),
    "IDEB por Regiao": (
        "SELECT regiao, AVG(ideb) AS media_ideb\n"
        "FROM `projeto.dataset.ideb`\n"
        "WHERE ano = 2021\n"
        "GROUP BY regiao\n"
        "ORDER BY media_ideb DESC"
    ),
    "Evolucao Taxa Aprovacao": (
        "SELECT ano, AVG(taxa_aprovacao) AS media_aprovacao\n"
        "FROM `projeto.dataset.indicadores_fluxo`\n"
        "WHERE ano BETWEEN 2015 AND 2023\n"
        "GROUP BY ano\n"
        "ORDER BY ano"
    ),
}


def validate_query(query: str) -> tuple[bool, str]:
    if not query or not query.strip():
        return False, "Query vazia"

    query_upper = query.upper().strip()

    if not query_upper.startswith("SELECT"):
        return False, "Apenas queries SELECT sao permitidas"

    for keyword in BLOCKED_KEYWORDS:
        pattern = r"\b" + keyword + r"\b"
        if re.search(pattern, query_upper):
            return False, f"Keyword proibida detectada: {keyword}"

    if query_upper.count("(") != query_upper.count(")"):
        return False, "Parenteses desbalanceados"

    return True, "Query valida"


def render_sql_editor(
    execute_callback: Optional[callable] = None,
) -> Optional[pd.DataFrame]:
    st.subheader("Editor SQL")
    st.markdown("Execute queries personalizadas no Data Lake educacional.")

    template: str = st.selectbox(
        "Templates",
        options=["Escrever query personalizada"] + list(QUERY_TEMPLATES.keys()),
        key="sql_template",
    )

    default_query = ""
    if template != "Escrever query personalizada":
        default_query = QUERY_TEMPLATES.get(template, "")

    query: str = st.text_area(
        "SQL Query",
        value=default_query,
        height=200,
        key="sql_query_input",
        help="Apenas queries SELECT sao permitidas",
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        execute = st.button("Executar", key="sql_execute", type="primary")
    with col2:
        limit: int = st.number_input(
            "Limite de linhas",
            min_value=10,
            max_value=10000,
            value=1000,
            key="sql_limit",
        )

    if execute and query:
        is_valid, message = validate_query(query)

        if not is_valid:
            st.error(f"Query invalida: {message}")
            return None

        limited_query = f"{query.rstrip().rstrip(';')}\nLIMIT {limit}"

        if execute_callback:
            with st.spinner("Executando query..."):
                result = execute_callback(limited_query)
                if result is not None:
                    st.success(f"Query executada: {len(result)} linhas retornadas")
                    st.dataframe(result, use_container_width=True)
                    logger.info("Query executada com sucesso: %d linhas", len(result))
                    return result
                else:
                    st.error("Erro ao executar a query.")
        else:
            st.info("Conexao BigQuery nao disponivel. Configure as credenciais.")

    return None
