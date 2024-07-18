import pandas as pd
import numpy as np
import logging
from typing import Optional
from dataclasses import dataclass


logger: logging.Logger = logging.getLogger(__name__)


@dataclass
class Anomaly:
    """Representacao de uma anomalia detectada nos dados."""

    index: int
    column: str
    value: float
    expected_min: float
    expected_max: float
    severity: str
    description: str

    @property
    def deviation(self) -> float:
        midpoint = (self.expected_min + self.expected_max) / 2
        return round(abs(self.value - midpoint), 2)


class AnomalyDetector:
    """Detector de anomalias baseado em metodos estatisticos."""

    def __init__(self, z_threshold: float = 2.5, iqr_multiplier: float = 1.5):
        self.z_threshold: float = z_threshold
        self.iqr_multiplier: float = iqr_multiplier
        self.logger: logging.Logger = logging.getLogger(__name__)

    def detect_zscore(self, series: pd.Series) -> list[int]:
        mean = series.mean()
        std = series.std()
        if std == 0:
            return []
        z_scores = ((series - mean) / std).abs()
        return z_scores[z_scores > self.z_threshold].index.tolist()

    def detect_iqr(self, series: pd.Series) -> list[int]:
        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        lower = q1 - self.iqr_multiplier * iqr
        upper = q3 + self.iqr_multiplier * iqr
        outliers = series[(series < lower) | (series > upper)]
        return outliers.index.tolist()

    def detect_sudden_change(
        self,
        series: pd.Series,
        threshold_pct: float = 20.0,
    ) -> list[int]:
        pct_change = series.pct_change().abs() * 100
        return pct_change[pct_change > threshold_pct].index.tolist()

    def analyze_column(
        self,
        df: pd.DataFrame,
        column: str,
        methods: Optional[list[str]] = None,
    ) -> list[Anomaly]:
        if column not in df.columns:
            return []

        if methods is None:
            methods = ["zscore", "iqr"]

        series = df[column].dropna()
        if len(series) < 5:
            return []

        anomaly_indices: set[int] = set()

        if "zscore" in methods:
            anomaly_indices.update(self.detect_zscore(series))
        if "iqr" in methods:
            anomaly_indices.update(self.detect_iqr(series))
        if "sudden_change" in methods:
            anomaly_indices.update(self.detect_sudden_change(series))

        q1 = series.quantile(0.25)
        q3 = series.quantile(0.75)
        iqr = q3 - q1
        expected_min = q1 - self.iqr_multiplier * iqr
        expected_max = q3 + self.iqr_multiplier * iqr

        anomalies = []
        for idx in sorted(anomaly_indices):
            value = float(series.loc[idx])
            severity = "alta" if abs(value - series.mean()) > 3 * series.std() else "media"
            anomalies.append(Anomaly(
                index=int(idx),
                column=column,
                value=value,
                expected_min=round(expected_min, 2),
                expected_max=round(expected_max, 2),
                severity=severity,
                description=f"Valor {value:.2f} fora do intervalo [{expected_min:.2f}, {expected_max:.2f}]",
            ))

        self.logger.info(
            "Anomalias detectadas em '%s': %d ocorrencias", column, len(anomalies)
        )
        return anomalies

    def analyze_dataframe(
        self,
        df: pd.DataFrame,
        columns: Optional[list[str]] = None,
    ) -> dict[str, list[Anomaly]]:
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()

        results = {}
        for col in columns:
            anomalies = self.analyze_column(df, col)
            if anomalies:
                results[col] = anomalies

        total = sum(len(v) for v in results.values())
        self.logger.info(
            "Analise completa: %d anomalias em %d colunas",
            total, len(results),
        )
        return results

