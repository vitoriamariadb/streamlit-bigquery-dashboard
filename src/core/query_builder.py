from typing import Optional
import logging


class QueryBuilder:
    """Construtor de queries SQL para o BigQuery."""

    def __init__(self, dataset: str, project_id: str):
        self.dataset: str = dataset
        self.project_id: str = project_id
        self.logger: logging.Logger = logging.getLogger(__name__)

    def _full_table(self, table: str) -> str:
        return f"`{self.project_id}.{self.dataset}.{table}`"

    def build_select(
        self,
        table: str,
        columns: list[str] | None = None,
        where: Optional[str] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> str:
        cols = ", ".join(columns) if columns else "*"
        query = f"SELECT {cols} FROM {self._full_table(table)}"

        if where:
            query += f" WHERE {where}"
        if order_by:
            query += f" ORDER BY {order_by}"
        if limit:
            query += f" LIMIT {limit}"

        self.logger.debug("Query construida: %s", query)
        return query

    def build_aggregation(
        self,
        table: str,
        metrics: list[str],
        group_by: list[str],
        where: Optional[str] = None,
        having: Optional[str] = None,
    ) -> str:
        select_cols = group_by + metrics
        cols = ", ".join(select_cols)
        groups = ", ".join(group_by)

        query = f"SELECT {cols} FROM {self._full_table(table)}"
        if where:
            query += f" WHERE {where}"
        query += f" GROUP BY {groups}"
        if having:
            query += f" HAVING {having}"

        self.logger.debug("Query de agregacao construida: %s", query)
        return query

    def build_date_range_filter(
        self,
        date_column: str,
        start_date: str,
        end_date: str,
    ) -> str:
        return f"{date_column} BETWEEN '{start_date}' AND '{end_date}'"

    def build_panorama_query(
        self,
        table: str,
        estado: Optional[str] = None,
        ano_inicio: Optional[int] = None,
        ano_fim: Optional[int] = None,
    ) -> str:
        conditions: list[str] = []

        if estado:
            conditions.append(f"sigla_uf = '{estado}'")
        if ano_inicio:
            conditions.append(f"ano >= {ano_inicio}")
        if ano_fim:
            conditions.append(f"ano <= {ano_fim}")

        where = " AND ".join(conditions) if conditions else None
        return self.build_select(table, where=where, order_by="ano DESC")

    def build_kpi_query(
        self,
        table: str,
        metric_column: str,
        aggregation: str = "AVG",
        where: Optional[str] = None,
    ) -> str:
        query = (
            f"SELECT {aggregation}({metric_column}) AS valor "
            f"FROM {self._full_table(table)}"
        )
        if where:
            query += f" WHERE {where}"
        return query
