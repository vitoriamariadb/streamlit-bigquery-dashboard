import pandas as pd
import numpy as np
import logging
from typing import Optional
from dataclasses import dataclass, field
from datetime import datetime


logger: logging.Logger = logging.getLogger(__name__)


@dataclass
class QualityCheckResult:
    """Resultado de uma verificacao de qualidade."""

    check_name: str
    passed: bool
    details: str
    severity: str = "info"
    column: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


class DataQualityChecker:
    """Verificador de qualidade de dados para o dashboard."""

    def __init__(self):
        self.results: list[QualityCheckResult] = []
        self.logger: logging.Logger = logging.getLogger(__name__)

    def check_completeness(self, df: pd.DataFrame, threshold: float = 0.95) -> list[QualityCheckResult]:
        results = []
        for col in df.columns:
            completeness = 1 - (df[col].isna().sum() / len(df))
            passed = completeness >= threshold
            results.append(QualityCheckResult(
                check_name="completude",
                passed=passed,
                details=f"Coluna '{col}': {completeness:.1%} preenchida (limiar: {threshold:.1%})",
                severity="aviso" if not passed else "info",
                column=col,
            ))
        self.results.extend(results)
        return results

    def check_duplicates(self, df: pd.DataFrame, key_columns: Optional[list[str]] = None) -> QualityCheckResult:
        if key_columns:
            dupes = df.duplicated(subset=key_columns).sum()
        else:
            dupes = df.duplicated().sum()

        result = QualityCheckResult(
            check_name="duplicatas",
            passed=dupes == 0,
            details=f"{dupes} linhas duplicadas encontradas",
            severity="aviso" if dupes > 0 else "info",
        )
        self.results.append(result)
        return result

    def check_range(
        self,
        df: pd.DataFrame,
        column: str,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None,
    ) -> QualityCheckResult:
        if column not in df.columns:
            result = QualityCheckResult(
                check_name="intervalo",
                passed=False,
                details=f"Coluna '{column}' nao encontrada",
                severity="erro",
                column=column,
            )
            self.results.append(result)
            return result

        series = df[column].dropna()
        violations = 0

        if min_value is not None:
            violations += (series < min_value).sum()
        if max_value is not None:
            violations += (series > max_value).sum()

        result = QualityCheckResult(
            check_name="intervalo",
            passed=violations == 0,
            details=(
                f"Coluna '{column}': {violations} valores fora do intervalo "
                f"[{min_value}, {max_value}]"
            ),
            severity="aviso" if violations > 0 else "info",
            column=column,
        )
        self.results.append(result)
        return result

    def check_freshness(
        self,
        df: pd.DataFrame,
        date_column: str,
        max_age_days: int = 30,
    ) -> QualityCheckResult:
        if date_column not in df.columns:
            result = QualityCheckResult(
                check_name="atualidade",
                passed=False,
                details=f"Coluna '{date_column}' nao encontrada",
                severity="erro",
                column=date_column,
            )
            self.results.append(result)
            return result

        try:
            dates = pd.to_datetime(df[date_column])
            most_recent = dates.max()
            age_days = (datetime.now() - most_recent).days

            result = QualityCheckResult(
                check_name="atualidade",
                passed=age_days <= max_age_days,
                details=f"Dados mais recentes: {age_days} dias atras (limiar: {max_age_days} dias)",
                severity="aviso" if age_days > max_age_days else "info",
                column=date_column,
            )
        except Exception as e:
            result = QualityCheckResult(
                check_name="atualidade",
                passed=False,
                details=f"Erro ao verificar datas: {e}",
                severity="erro",
                column=date_column,
            )

        self.results.append(result)
        return result

    def run_education_checks(self, df: pd.DataFrame) -> list[QualityCheckResult]:
        results = []
        results.extend(self.check_completeness(df))
        results.append(self.check_duplicates(df))

        education_ranges = {
            "taxa_aprovacao": (0, 100),
            "taxa_reprovacao": (0, 100),
            "taxa_abandono": (0, 100),
            "ideb": (0, 10),
        }
        for col, (min_v, max_v) in education_ranges.items():
            if col in df.columns:
                results.append(self.check_range(df, col, min_v, max_v))

        self.logger.info(
            "Verificacao de qualidade concluida: %d checks, %d falhas",
            len(results),
            sum(1 for r in results if not r.passed),
        )
        return results

    def get_summary(self) -> dict:
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        return {
            "total_checks": total,
            "passed": passed,
            "failed": failed,
            "score": round((passed / total * 100) if total > 0 else 0, 1),
        }

