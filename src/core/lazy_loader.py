import streamlit as st
import pandas as pd
import logging
from typing import Any, Callable, Optional
from enum import Enum


logger: logging.Logger = logging.getLogger(__name__)


class LoadState(Enum):
    PENDING = "pending"
    LOADING = "loading"
    LOADED = "loaded"
    ERROR = "error"


class LazyDataLoader:
    """Carregador preguicoso de dados para melhorar tempo de inicializacao."""

    def __init__(self):
        self._loaders: dict[str, Callable] = {}
        self._data: dict[str, Any] = {}
        self._states: dict[str, LoadState] = {}
        self.logger: logging.Logger = logging.getLogger(__name__)

    def register(self, key: str, loader: Callable) -> None:
        self._loaders[key] = loader
        self._states[key] = LoadState.PENDING
        self.logger.debug("Loader registrado: %s", key)

    def get(self, key: str) -> Optional[Any]:
        if key in self._data:
            return self._data[key]

        if key not in self._loaders:
            self.logger.warning("Loader nao encontrado: %s", key)
            return None

        return self._load(key)

    def _load(self, key: str) -> Optional[Any]:
        self._states[key] = LoadState.LOADING
        try:
            data = self._loaders[key]()
            self._data[key] = data
            self._states[key] = LoadState.LOADED
            self.logger.info("Dados carregados: %s", key)
            return data
        except Exception as e:
            self._states[key] = LoadState.ERROR
            self.logger.error("Erro ao carregar '%s': %s", key, e)
            return None

    def preload(self, keys: list[str]) -> dict[str, LoadState]:
        results = {}
        for key in keys:
            self.get(key)
            results[key] = self._states.get(key, LoadState.ERROR)
        return results

    def invalidate(self, key: str) -> None:
        if key in self._data:
            del self._data[key]
        self._states[key] = LoadState.PENDING
        self.logger.debug("Cache invalidado: %s", key)

    def get_state(self, key: str) -> LoadState:
        return self._states.get(key, LoadState.PENDING)

    def get_all_states(self) -> dict[str, str]:
        return {k: v.value for k, v in self._states.items()}

    @property
    def loaded_count(self) -> int:
        return sum(1 for s in self._states.values() if s == LoadState.LOADED)

    @property
    def total_count(self) -> int:
        return len(self._loaders)


def create_paginated_loader(
    df: pd.DataFrame,
    page_size: int = 50,
) -> Callable:
    """Cria um loader paginado para grandes DataFrames."""
    total_pages = max(1, (len(df) - 1) // page_size + 1)

    def load_page(page: int = 1) -> pd.DataFrame:
        start = (page - 1) * page_size
        end = start + page_size
        return df.iloc[start:end]

    load_page.total_pages = total_pages
    load_page.total_rows = len(df)
    return load_page


def render_lazy_section(
    key: str,
    loader: LazyDataLoader,
    render_func: Callable,
) -> None:
    state = loader.get_state(key)

    if state == LoadState.PENDING:
        if st.button(f"Carregar {key}", key=f"load_{key}"):
            with st.spinner(f"Carregando {key}..."):
                data = loader.get(key)
                if data is not None:
                    render_func(data)
                else:
                    st.error(f"Erro ao carregar {key}")
        else:
            st.info(f"Clique para carregar: {key}")
    elif state == LoadState.LOADED:
        data = loader.get(key)
        render_func(data)
    elif state == LoadState.ERROR:
        st.error(f"Erro ao carregar {key}. Tente novamente.")
        if st.button(f"Retentar {key}", key=f"retry_{key}"):
            loader.invalidate(key)
            st.rerun()
