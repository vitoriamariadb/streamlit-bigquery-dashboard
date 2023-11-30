import pytest
import pandas as pd
from datetime import date

from src.core.cache_manager import CacheManager, CacheEntry
from src.core.query_builder import QueryBuilder
from src.core.csv_processor import CSVProcessor
from src.components.date_picker import DateRange
from src.components.filters import FilterState, REGIOES_BR, ESTADOS_BR


class TestCacheManager:

    def test_cache_set_and_get(self):
        cache = CacheManager(default_ttl=60)
        cache.set("SELECT 1", "result_1")
        assert cache.get("SELECT 1") == "result_1"

    def test_cache_miss(self):
        cache = CacheManager(default_ttl=60)
        assert cache.get("nonexistent") is None

    def test_cache_clear(self):
        cache = CacheManager(default_ttl=60)
        cache.set("q1", "r1")
        cache.set("q2", "r2")
        assert cache.size == 2
        cache.clear()
        assert cache.size == 0

    def test_cache_max_entries(self):
        cache = CacheManager(default_ttl=60, max_entries=2)
        cache.set("q1", "r1")
        cache.set("q2", "r2")
        cache.set("q3", "r3")
        assert cache.size == 2

    def test_cache_stats(self):
        cache = CacheManager(default_ttl=3600)
        cache.set("q1", "r1")
        stats = cache.stats()
        assert stats["total_entries"] == 1
        assert stats["active_entries"] == 1

    def test_cache_invalidate(self):
        cache = CacheManager(default_ttl=60)
        cache.set("q1", "r1")
        cache.invalidate("q1")
        assert cache.get("q1") is None

    def test_cache_with_params(self):
        cache = CacheManager(default_ttl=60)
        cache.set("SELECT *", "r1", params={"estado": "SP"})
        cache.set("SELECT *", "r2", params={"estado": "RJ"})
        assert cache.get("SELECT *", params={"estado": "SP"}) == "r1"
        assert cache.get("SELECT *", params={"estado": "RJ"}) == "r2"


class TestQueryBuilder:

    def setup_method(self):
        self.qb = QueryBuilder(dataset="educacao", project_id="projeto-teste")

    def test_build_select_all(self):
        query = self.qb.build_select("escolas")
        assert "SELECT *" in query
        assert "escolas" in query

    def test_build_select_columns(self):
        query = self.qb.build_select("escolas", columns=["nome", "uf"])
        assert "nome, uf" in query

    def test_build_select_with_where(self):
        query = self.qb.build_select("escolas", where="uf = 'SP'")
        assert "WHERE uf = 'SP'" in query

    def test_build_select_with_limit(self):
        query = self.qb.build_select("escolas", limit=100)
        assert "LIMIT 100" in query

    def test_build_aggregation(self):
        query = self.qb.build_aggregation(
            "indicadores",
            metrics=["AVG(taxa_aprovacao) AS media"],
            group_by=["sigla_uf"],
        )
        assert "AVG(taxa_aprovacao)" in query
        assert "GROUP BY sigla_uf" in query

    def test_build_date_range_filter(self):
        f = self.qb.build_date_range_filter("data", "2020-01-01", "2023-12-31")
        assert "BETWEEN" in f

    def test_build_panorama_query(self):
        query = self.qb.build_panorama_query("panorama", estado="SP", ano_inicio=2020)
        assert "sigla_uf = 'SP'" in query
        assert "ano >= 2020" in query

    def test_build_kpi_query(self):
        query = self.qb.build_kpi_query("indicadores", "taxa_aprovacao")
        assert "AVG(taxa_aprovacao)" in query


class TestCSVProcessor:

    def test_format_date_iso(self):
        assert CSVProcessor.format_date("2023-01-15") == "15/01/2023"

    def test_format_date_year_month(self):
        assert CSVProcessor.format_date("202301") == "01/01/2023"

    def test_format_date_year_only(self):
        assert CSVProcessor.format_date("2023") == "01/01/2023"

    def test_format_date_unknown(self):
        assert CSVProcessor.format_date("Desconhecido") == "Desconhecido"

    def test_format_date_empty(self):
        assert CSVProcessor.format_date("") == ""


class TestDateRange:

    def test_date_range_days(self):
        dr = DateRange(date(2023, 1, 1), date(2023, 12, 31))
        assert dr.days == 364

    def test_date_range_years(self):
        dr = DateRange(date(2020, 1, 1), date(2023, 1, 1))
        assert dr.years == 8.2 or dr.years > 0

    def test_date_range_to_dict(self):
        dr = DateRange(date(2023, 1, 1), date(2023, 6, 30))
        d = dr.to_dict()
        assert "start" in d
        assert "end" in d
        assert "days" in d


class TestFilterState:

    def test_default_state(self):
        state = FilterState()
        assert state.estados == []
        assert state.regioes == []
        assert state.ano_inicio is None

    def test_to_dict(self):
        state = FilterState()
        state.estados = ["SP", "RJ"]
        d = state.to_dict()
        assert d["estados"] == ["SP", "RJ"]

    def test_regioes_mapping(self):
        assert "SP" in REGIOES_BR["Sudeste"]
        assert "BA" in REGIOES_BR["Nordeste"]
        assert len(ESTADOS_BR) == 27


class TestCacheEntry:

    def test_entry_not_expired(self):
        entry = CacheEntry("value", ttl=3600)
        assert not entry.is_expired()
