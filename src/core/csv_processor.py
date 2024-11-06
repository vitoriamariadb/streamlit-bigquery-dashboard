import csv
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime
import re

import pandas as pd


logger: logging.Logger = logging.getLogger(__name__)


class CSVProcessor:
    """Processador de arquivos CSV para dados educacionais."""

    def __init__(self, input_path: Path, output_path: Path):
        self.input_path: Path = input_path
        self.output_path: Path = output_path
        self.logger: logging.Logger = logging.getLogger(__name__)

    @staticmethod
    def format_date(date_str: str) -> str:
        if not date_str or date_str in ["Desconhecido", "N/A", "Erro"]:
            return date_str

        date_str = date_str.strip()

        if re.match(r"^\d{6}$", date_str):
            year = date_str[:4]
            month = date_str[4:6]
            return f"01/{month}/{year}"

        if re.match(r"^\d{4}-\d{2}-\d{2}$", date_str):
            parts = date_str.split("-")
            return f"{parts[2]}/{parts[1]}/{parts[0]}"

        if re.match(r"^\d{4}$", date_str):
            return f"01/01/{date_str}"

        return date_str

    def read_csv(self, delimiter: str = ";") -> list[list[str]]:
        try:
            with open(self.input_path, "r", encoding="utf-8-sig") as f:
                reader = csv.reader(f, delimiter=delimiter)
                rows = list(reader)
            self.logger.info("CSV lido: %d linhas de %s", len(rows), self.input_path)
            return rows
        except Exception as e:
            self.logger.error("Erro ao ler CSV %s: %s", self.input_path, e)
            return []

    def write_csv(self, rows: list[list[str]], delimiter: str = ";") -> bool:
        try:
            self.output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.output_path, "w", encoding="utf-8-sig", newline="") as f:
                writer = csv.writer(f, delimiter=delimiter)
                writer.writerows(rows)
            self.logger.info("CSV escrito: %s", self.output_path)
            return True
        except Exception as e:
            self.logger.error("Erro ao escrever CSV %s: %s", self.output_path, e)
            return False

    def to_dataframe(self, delimiter: str = ";") -> Optional[pd.DataFrame]:
        try:
            df = pd.read_csv(self.input_path, delimiter=delimiter, encoding="utf-8-sig")
            self.logger.info("DataFrame criado: %d linhas x %d colunas", *df.shape)
            return df
        except Exception as e:
            self.logger.error("Erro ao criar DataFrame: %s", e)
            return None

