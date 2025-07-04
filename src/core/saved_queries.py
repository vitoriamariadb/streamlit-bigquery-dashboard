import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field, asdict


logger: logging.Logger = logging.getLogger(__name__)


@dataclass
class SavedQuery:
    """Representacao de uma query salva pelo usuario."""

    name: str
    query: str
    description: str = ""
    category: str = "geral"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    author: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    is_public: bool = False


class SavedQueryManager:
    """Gerenciador de queries salvas com persistencia em JSON."""

    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path: Path = storage_path or Path("data/saved_queries.json")
        self._queries: dict[str, SavedQuery] = {}
        self.logger: logging.Logger = logging.getLogger(__name__)
        self._load()

    def _load(self) -> None:
        if not self.storage_path.exists():
            return
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for name, entry in data.items():
                self._queries[name] = SavedQuery(**entry)
            self.logger.info("Queries carregadas: %d", len(self._queries))
        except Exception as e:
            self.logger.error("Erro ao carregar queries salvas: %s", e)

    def _save(self) -> None:
        try:
            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            data = {name: asdict(q) for name, q in self._queries.items()}
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.logger.debug("Queries salvas em disco")
        except Exception as e:
            self.logger.error("Erro ao salvar queries: %s", e)

    def save_query(self, query: SavedQuery) -> bool:
        if query.name in self._queries:
            query.updated_at = datetime.now().isoformat()
        self._queries[query.name] = query
        self._save()
        self.logger.info("Query salva: %s", query.name)
        return True

    def get_query(self, name: str) -> Optional[SavedQuery]:
        return self._queries.get(name)

    def delete_query(self, name: str) -> bool:
        if name in self._queries:
            del self._queries[name]
            self._save()
            self.logger.info("Query removida: %s", name)
            return True
        return False

    def list_queries(self, category: Optional[str] = None) -> list[SavedQuery]:
        queries = list(self._queries.values())
        if category:
            queries = [q for q in queries if q.category == category]
        return sorted(queries, key=lambda q: q.updated_at, reverse=True)

    def search(self, term: str) -> list[SavedQuery]:
        term_lower = term.lower()
        return [
            q for q in self._queries.values()
            if term_lower in q.name.lower()
            or term_lower in q.description.lower()
            or term_lower in q.query.lower()
        ]

    def get_categories(self) -> list[str]:
        return sorted(set(q.category for q in self._queries.values()))

    @property
    def count(self) -> int:
        return len(self._queries)
