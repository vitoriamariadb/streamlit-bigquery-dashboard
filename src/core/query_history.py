import logging
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field


logger: logging.Logger = logging.getLogger(__name__)


@dataclass
class QueryRecord:
    """Registro de uma query executada."""

    query: str
    executed_at: datetime = field(default_factory=datetime.now)
    execution_time_ms: float = 0.0
    rows_returned: int = 0
    status: str = "success"
    error_message: Optional[str] = None
    user: Optional[str] = None

    @property
    def is_success(self) -> bool:
        return self.status == "success"


class QueryHistory:
    """Historico de queries executadas no sistema."""

    def __init__(self, max_entries: int = 500):
        self.max_entries: int = max_entries
        self._history: list[QueryRecord] = []
        self.logger: logging.Logger = logging.getLogger(__name__)

    def add(self, record: QueryRecord) -> None:
        self._history.append(record)
        if len(self._history) > self.max_entries:
            self._history = self._history[-self.max_entries:]
        self.logger.debug(
            "Query registrada: %s (%dms, %d linhas)",
            record.query[:50], record.execution_time_ms, record.rows_returned,
        )

    def get_recent(self, count: int = 20) -> list[QueryRecord]:
        return list(reversed(self._history[-count:]))

    def get_by_user(self, user: str) -> list[QueryRecord]:
        return [r for r in self._history if r.user == user]

    def get_failed(self) -> list[QueryRecord]:
        return [r for r in self._history if not r.is_success]

    def search(self, term: str) -> list[QueryRecord]:
        term_lower = term.lower()
        return [r for r in self._history if term_lower in r.query.lower()]

    def clear(self) -> None:
        count = len(self._history)
        self._history.clear()
        self.logger.info("Historico limpo: %d registros removidos", count)

    def get_stats(self) -> dict:
        if not self._history:
            return {
                "total_queries": 0,
                "success_rate": 0.0,
                "avg_execution_time_ms": 0.0,
                "total_rows_returned": 0,
            }

        successes = sum(1 for r in self._history if r.is_success)
        avg_time = sum(r.execution_time_ms for r in self._history) / len(self._history)
        total_rows = sum(r.rows_returned for r in self._history)

        return {
            "total_queries": len(self._history),
            "success_rate": round(successes / len(self._history) * 100, 1),
            "avg_execution_time_ms": round(avg_time, 1),
            "total_rows_returned": total_rows,
        }

    @property
    def size(self) -> int:
        return len(self._history)
