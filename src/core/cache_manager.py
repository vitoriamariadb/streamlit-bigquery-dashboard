import hashlib
import time
import logging
from typing import Any, Optional
from threading import Lock


class CacheEntry:
    """Entrada individual do cache com TTL."""

    def __init__(self, value: Any, ttl: int):
        self.value: Any = value
        self.created_at: float = time.time()
        self.ttl: int = ttl

    def is_expired(self) -> bool:
        return (time.time() - self.created_at) > self.ttl


class CacheManager:
    """Gerenciador de cache em memoria para queries BigQuery."""

    def __init__(self, default_ttl: int = 3600, max_entries: int = 100):
        self.default_ttl: int = default_ttl
        self.max_entries: int = max_entries
        self._cache: dict[str, CacheEntry] = {}
        self._lock: Lock = Lock()
        self.logger: logging.Logger = logging.getLogger(__name__)

    @staticmethod
    def _generate_key(query: str, params: Optional[dict] = None) -> str:
        raw = query + str(sorted(params.items())) if params else query
        return hashlib.sha256(raw.encode()).hexdigest()

    def get(self, query: str, params: Optional[dict] = None) -> Optional[Any]:
        key = self._generate_key(query, params)
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                self.logger.debug("Cache miss: %s", key[:12])
                return None
            if entry.is_expired():
                del self._cache[key]
                self.logger.debug("Cache expirado: %s", key[:12])
                return None
            self.logger.debug("Cache hit: %s", key[:12])
            return entry.value

    def set(
        self,
        query: str,
        value: Any,
        params: Optional[dict] = None,
        ttl: Optional[int] = None,
    ) -> None:
        key = self._generate_key(query, params)
        effective_ttl = ttl or self.default_ttl

        with self._lock:
            if len(self._cache) >= self.max_entries:
                self._evict_oldest()
            self._cache[key] = CacheEntry(value, effective_ttl)
            self.logger.debug("Cache set: %s (TTL: %ds)", key[:12], effective_ttl)

    def _evict_oldest(self) -> None:
        if not self._cache:
            return
        oldest_key = min(
            self._cache, key=lambda k: self._cache[k].created_at
        )
        del self._cache[oldest_key]
        self.logger.debug("Cache evicted: %s", oldest_key[:12])

    def invalidate(self, query: str, params: Optional[dict] = None) -> None:
        key = self._generate_key(query, params)
        with self._lock:
            if key in self._cache:
                del self._cache[key]
                self.logger.debug("Cache invalidado: %s", key[:12])

    def clear(self) -> None:
        with self._lock:
            count = len(self._cache)
            self._cache.clear()
            self.logger.info("Cache limpo: %d entradas removidas", count)

    @property
    def size(self) -> int:
        return len(self._cache)

    def stats(self) -> dict:
        with self._lock:
            expired = sum(1 for e in self._cache.values() if e.is_expired())
            return {
                "total_entries": len(self._cache),
                "expired_entries": expired,
                "active_entries": len(self._cache) - expired,
                "max_entries": self.max_entries,
            }
