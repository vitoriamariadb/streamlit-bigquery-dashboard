import streamlit as st
import pandas as pd
import logging
import time
from typing import Any, Callable, Optional
from functools import wraps


logger: logging.Logger = logging.getLogger(__name__)


def timed_execution(func: Callable) -> Callable:
    """Decorador para medir tempo de execucao de funcoes."""

    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = (time.perf_counter() - start) * 1000
        logger.info(
            "Funcao '%s' executada em %.1fms", func.__name__, elapsed
        )
        return result

    return wrapper


@st.cache_data(ttl=3600, show_spinner=False)
def cached_query(query: str, _client: Any) -> Optional[pd.DataFrame]:
    """Executa query com cache do Streamlit."""
    try:
        start = time.perf_counter()
        df = _client.execute_query(query)
        elapsed = (time.perf_counter() - start) * 1000
        logger.info("Query cached executada em %.1fms", elapsed)
        return df
    except Exception as e:
        logger.error("Erro em cached_query: %s", e)
        return None


@st.cache_data(ttl=7200, show_spinner=False)
def cached_dataframe_transform(
    df_hash: str,
    transform_name: str,
    **kwargs,
) -> Optional[pd.DataFrame]:
    """Cache para transformacoes de DataFrame."""
    logger.debug("Cache transform: %s (%s)", transform_name, df_hash[:12])
    return None


def optimize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Otimiza tipos de dados do DataFrame para reducao de memoria."""
    optimized = df.copy()
    initial_mem = optimized.memory_usage(deep=True).sum()

    for col in optimized.select_dtypes(include=["int64"]).columns:
        col_min = optimized[col].min()
        col_max = optimized[col].max()
        if col_min >= 0:
            if col_max <= 255:
                optimized[col] = optimized[col].astype("uint8")
            elif col_max <= 65535:
                optimized[col] = optimized[col].astype("uint16")
            elif col_max <= 4294967295:
                optimized[col] = optimized[col].astype("uint32")
        else:
            if col_min >= -128 and col_max <= 127:
                optimized[col] = optimized[col].astype("int8")
            elif col_min >= -32768 and col_max <= 32767:
                optimized[col] = optimized[col].astype("int16")
            elif col_min >= -2147483648 and col_max <= 2147483647:
                optimized[col] = optimized[col].astype("int32")

    for col in optimized.select_dtypes(include=["float64"]).columns:
        optimized[col] = optimized[col].astype("float32")

    for col in optimized.select_dtypes(include=["object"]).columns:
        nunique = optimized[col].nunique()
        if nunique / len(optimized) < 0.5:
            optimized[col] = optimized[col].astype("category")

    final_mem = optimized.memory_usage(deep=True).sum()
    reduction = (1 - final_mem / initial_mem) * 100 if initial_mem > 0 else 0
    logger.info(
        "DataFrame otimizado: %.1fMB -> %.1fMB (reducao de %.1f%%)",
        initial_mem / 1e6, final_mem / 1e6, reduction,
    )
    return optimized


class PerformanceMonitor:
    """Monitor de performance da aplicacao."""

    def __init__(self):
        self._timings: dict[str, list[float]] = {}
        self.logger: logging.Logger = logging.getLogger(__name__)

    def record(self, operation: str, elapsed_ms: float) -> None:
        if operation not in self._timings:
            self._timings[operation] = []
        self._timings[operation].append(elapsed_ms)

    def get_stats(self) -> dict[str, dict]:
        stats = {}
        for op, timings in self._timings.items():
            stats[op] = {
                "count": len(timings),
                "avg_ms": round(sum(timings) / len(timings), 1),
                "min_ms": round(min(timings), 1),
                "max_ms": round(max(timings), 1),
            }
        return stats
