import logging
from datetime import datetime, timedelta
from typing import Optional, Callable
from dataclasses import dataclass, field
from enum import Enum


logger: logging.Logger = logging.getLogger(__name__)


class Frequency(Enum):
    DIARIO = "diario"
    SEMANAL = "semanal"
    MENSAL = "mensal"
    TRIMESTRAL = "trimestral"


@dataclass
class ScheduledReport:
    """Definicao de um relatorio agendado."""

    name: str
    description: str
    frequency: Frequency
    recipients: list[str]
    query_name: str
    export_format: str = "csv"
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.now)

    def calculate_next_run(self) -> datetime:
        base = self.last_run or datetime.now()
        intervals = {
            Frequency.DIARIO: timedelta(days=1),
            Frequency.SEMANAL: timedelta(weeks=1),
            Frequency.MENSAL: timedelta(days=30),
            Frequency.TRIMESTRAL: timedelta(days=90),
        }
        self.next_run = base + intervals.get(self.frequency, timedelta(days=1))
        return self.next_run

    def should_run(self) -> bool:
        if not self.enabled:
            return False
        if self.next_run is None:
            return True
        return datetime.now() >= self.next_run


class ReportScheduler:
    """Agendador de relatorios automaticos."""

    def __init__(self):
        self.reports: list[ScheduledReport] = []
        self.logger: logging.Logger = logging.getLogger(__name__)

    def add_report(self, report: ScheduledReport) -> None:
        report.calculate_next_run()
        self.reports.append(report)
        self.logger.info(
            "Relatorio agendado: %s (%s)", report.name, report.frequency.value
        )

    def remove_report(self, name: str) -> bool:
        for i, report in enumerate(self.reports):
            if report.name == name:
                self.reports.pop(i)
                self.logger.info("Relatorio removido: %s", name)
                return True
        return False

    def get_pending_reports(self) -> list[ScheduledReport]:
        return [r for r in self.reports if r.should_run()]

    def execute_report(
        self,
        report: ScheduledReport,
        executor: Optional[Callable] = None,
    ) -> bool:
        try:
            self.logger.info("Executando relatorio: %s", report.name)

            if executor:
                executor(report)

            report.last_run = datetime.now()
            report.calculate_next_run()
            self.logger.info(
                "Relatorio executado: %s. Proxima execucao: %s",
                report.name, report.next_run,
            )
            return True
        except Exception as e:
            self.logger.error("Erro ao executar relatorio %s: %s", report.name, e)
            return False

    def run_pending(self, executor: Optional[Callable] = None) -> int:
        pending = self.get_pending_reports()
        executed = 0
        for report in pending:
            if self.execute_report(report, executor):
                executed += 1
        self.logger.info("Relatorios executados: %d de %d pendentes", executed, len(pending))
        return executed

    def get_status(self) -> list[dict]:
        return [
            {
                "nome": r.name,
                "frequencia": r.frequency.value,
                "ultima_execucao": r.last_run.isoformat() if r.last_run else "Nunca",
                "proxima_execucao": r.next_run.isoformat() if r.next_run else "Pendente",
                "habilitado": r.enabled,
            }
            for r in self.reports
        ]
