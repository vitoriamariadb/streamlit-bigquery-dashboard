from google.cloud import bigquery
from google.oauth2 import service_account
from typing import Optional
import logging
from pathlib import Path

import pandas as pd


class BigQueryClient:
    """Cliente para conexao e execucao de queries no BigQuery."""

    def __init__(self, credentials_path: str, project_id: str):
        self.credentials_path: Path = Path(credentials_path)
        self.project_id: str = project_id
        self.client: Optional[bigquery.Client] = None
        self.logger: logging.Logger = logging.getLogger(__name__)

    def connect(self) -> bool:
        try:
            credentials = service_account.Credentials.from_service_account_file(
                str(self.credentials_path),
                scopes=["https://www.googleapis.com/auth/bigquery"],
            )
            self.client = bigquery.Client(
                credentials=credentials,
                project=self.project_id,
            )
            test_query = "SELECT 1 AS health_check"
            self.client.query(test_query).result()
            self.logger.info("Conexao BigQuery estabelecida: %s", self.project_id)
            return True
        except Exception as e:
            self.logger.error("Falha ao conectar no BigQuery: %s", e)
            return False

    def execute_query(self, query: str, timeout: int = 300) -> Optional[pd.DataFrame]:
        if not self.client:
            self.logger.error("Cliente BigQuery nao inicializado")
            return None
        try:
            job_config = bigquery.QueryJobConfig(
                use_query_cache=True,
            )
            query_job = self.client.query(query, job_config=job_config, timeout=timeout)
            df = query_job.to_dataframe()
            self.logger.info(
                "Query executada com sucesso: %d linhas retornadas", len(df)
            )
            return df
        except Exception as e:
            self.logger.error("Erro ao executar query: %s", e)
            return None

    def get_table_metadata(self, table_ref: str) -> dict:
        try:
            table = self.client.get_table(table_ref)
            return {
                "num_rows": table.num_rows,
                "num_bytes": table.num_bytes,
                "modified": table.modified.isoformat() if table.modified else None,
                "created": table.created.isoformat() if table.created else None,
            }
        except Exception as e:
            self.logger.error("Erro ao buscar metadados da tabela %s: %s", table_ref, e)
            return {}

    def close(self) -> None:
        if self.client:
            self.client.close()
            self.logger.info("Conexao BigQuery encerrada")

