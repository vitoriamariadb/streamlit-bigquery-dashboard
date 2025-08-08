import pytest
import pandas as pd
import numpy as np
from datetime import datetime

from src.core.cache_manager import CacheManager
from src.core.query_builder import QueryBuilder
from src.core.query_history import QueryHistory, QueryRecord
from src.core.saved_queries import SavedQuery
from src.core.performance import optimize_dataframe, PerformanceMonitor
from src.core.lazy_loader import LazyDataLoader, LoadState
from src.analytics.alerts import AlertManager, AlertRule, Alert
from src.analytics.anomaly_detection import AnomalyDetector
from src.analytics.data_quality import DataQualityChecker
from src.analytics.forecasting import linear_forecast, moving_average_forecast
from src.analytics.period_comparison import compare_periods
from src.pages.cohort import build_cohort_matrix
from src.pages.funnel import calculate_funnel_rates
from src.pages.retention import calculate_retention_rate


class TestEndToEndQueryFlow:
    """Testes end-to-end do fluxo de queries."""

    def test_query_build_cache_history(self):
        qb = QueryBuilder(dataset="educacao", project_id="teste")
        query = qb.build_education_query("educacao", estado="SP", ano_inicio=2020)

        cache = CacheManager(default_ttl=60)
        cache.set(query, pd.DataFrame({"ano": [2020, 2021], "ideb": [5.0, 5.2]}))

        history = QueryHistory()
        history.add(QueryRecord(
            query=query,
            execution_time_ms=150.0,
            rows_returned=2,
        ))

        assert cache.get(query) is not None
        assert history.size == 1
        assert "sigla_uf = 'SP'" in query

    def test_full_analysis_pipeline(self):
        df = pd.DataFrame({
            "ano": list(range(2015, 2024)),
            "taxa_aprovacao": [88.5, 89.1, 89.8, 90.2, 91.0, 91.5, 92.0, 92.3, 92.8],
            "taxa_reprovacao": [7.2, 6.8, 6.3, 5.9, 5.4, 5.0, 4.5, 4.1, 3.8],
            "taxa_abandono": [4.3, 4.1, 3.9, 3.9, 3.6, 3.5, 3.5, 1.8, 1.5],
            "ideb": [4.5, 4.7, 4.9, 5.0, 5.2, 5.3, 5.4, 5.4, 5.6],
        })

        forecast = linear_forecast(df["ideb"], periods_ahead=3)
        assert len(forecast["forecast"]) == 3
        assert forecast["r_squared"] > 0.9

        detector = AnomalyDetector()
        anomalies = detector.analyze_dataframe(df)
        assert isinstance(anomalies, dict)

        checker = DataQualityChecker()
        results = checker.run_education_checks(df)
        summary = checker.get_summary()
        assert summary["total_checks"] > 0
        assert summary["score"] > 0


class TestAlertSystem:

    def test_alert_evaluation_flow(self):
        manager = AlertManager()
        manager.setup_default_rules()

        metrics = {
            "taxa_aprovacao": 80.0,
            "taxa_abandono": 6.0,
            "ideb": 3.5,
        }

        alerts = manager.evaluate_all(metrics)
        assert len(alerts) >= 2

        critical_count = manager.get_active_count()["critico"]
        assert critical_count >= 1

    def test_alert_acknowledge(self):
        manager = AlertManager()
        manager.add_rule(AlertRule("test", "acima", 50, "aviso"))
        alerts = manager.evaluate_all({"test": 60})
        assert len(alerts) == 1

        manager.acknowledge(alerts[0])
        assert len(manager.active_alerts) == 0


class TestForecastingPipeline:

    def test_linear_forecast_accuracy(self):
        series = pd.Series([1.0, 2.0, 3.0, 4.0, 5.0])
        result = linear_forecast(series, periods_ahead=2)
        assert abs(result["forecast"][0] - 6.0) < 0.1
        assert result["r_squared"] > 0.99

    def test_moving_average_forecast(self):
        series = pd.Series([10.0, 12.0, 11.0, 13.0, 14.0])
        forecast = moving_average_forecast(series, window=3, periods_ahead=2)
        assert len(forecast) == 2
        assert all(v > 0 for v in forecast)


class TestAnomalyDetection:

    def test_zscore_detection(self):
        detector = AnomalyDetector(z_threshold=2.0)
        series = pd.Series([10, 11, 10, 12, 10, 50, 11, 10])
        outliers = detector.detect_zscore(series)
        assert 5 in outliers

    def test_iqr_detection(self):
        detector = AnomalyDetector()
        series = pd.Series([10, 11, 10, 12, 10, 50, 11, 10])
        outliers = detector.detect_iqr(series)
        assert 5 in outliers

    def test_sudden_change_detection(self):
        detector = AnomalyDetector()
        series = pd.Series([100, 102, 101, 103, 150, 103])
        changes = detector.detect_sudden_change(series, threshold_pct=30)
        assert 4 in changes


class TestDataQualityEndToEnd:

    def test_education_data_quality(self):
        df = pd.DataFrame({
            "ano": [2020, 2021, 2022, 2023],
            "taxa_aprovacao": [91.0, 92.0, 93.0, 94.0],
            "taxa_reprovacao": [5.0, 4.0, 3.5, 3.0],
            "taxa_abandono": [2.0, 1.5, 1.2, 1.0],
            "ideb": [5.0, 5.2, 5.4, 5.6],
        })

        checker = DataQualityChecker()
        results = checker.run_education_checks(df)

        passed = [r for r in results if r.passed]
        assert len(passed) > 0
        assert checker.get_summary()["score"] > 80

    def test_data_with_issues(self):
        df = pd.DataFrame({
            "taxa_aprovacao": [91.0, None, 93.0, 110.0],
            "ideb": [5.0, 5.2, None, 5.6],
        })

        checker = DataQualityChecker()
        results = checker.run_education_checks(df)
        failed = [r for r in results if not r.passed]
        assert len(failed) > 0


class TestPeriodComparison:

    def test_compare_two_years(self):
        df = pd.DataFrame({
            "ano": [2022, 2022, 2023, 2023],
            "taxa_aprovacao": [90.0, 92.0, 93.0, 95.0],
            "ideb": [5.0, 5.1, 5.3, 5.5],
        })

        comparison = compare_periods(df, "ano", ["taxa_aprovacao", "ideb"], 2022, 2023)
        assert "Variacao Absoluta" in comparison.columns
        assert "Variacao Percentual" in comparison.columns


class TestPerformanceOptimization:

    def test_dataframe_optimization(self):
        df = pd.DataFrame({
            "small_int": [1, 2, 3, 4, 5],
            "big_float": [1.1, 2.2, 3.3, 4.4, 5.5],
            "category": ["a", "b", "a", "b", "a"],
        })

        optimized = optimize_dataframe(df)
        assert optimized["small_int"].dtype != "int64"
        assert optimized["big_float"].dtype == "float32"

    def test_performance_monitor(self):
        monitor = PerformanceMonitor()
        monitor.record("query", 100.0)
        monitor.record("query", 200.0)
        monitor.record("render", 50.0)

        stats = monitor.get_stats()
        assert stats["query"]["count"] == 2
        assert stats["query"]["avg_ms"] == 150.0


class TestLazyLoader:

    def test_lazy_load_flow(self):
        loader = LazyDataLoader()
        loader.register("test_data", lambda: pd.DataFrame({"x": [1, 2, 3]}))

        assert loader.get_state("test_data") == LoadState.PENDING
        data = loader.get("test_data")
        assert data is not None
        assert loader.get_state("test_data") == LoadState.LOADED
        assert loader.loaded_count == 1

    def test_invalidate_and_reload(self):
        loader = LazyDataLoader()
        counter = {"calls": 0}

        def load_fn():
            counter["calls"] += 1
            return [1, 2, 3]

        loader.register("data", load_fn)
        loader.get("data")
        assert counter["calls"] == 1

        loader.invalidate("data")
        assert loader.get_state("data") == LoadState.PENDING

        loader.get("data")
        assert counter["calls"] == 2


class TestFunnelCalculation:

    def test_funnel_rates(self):
        values = [100000, 92000, 85000, 78000, 72000]
        rates = calculate_funnel_rates(values)

        assert len(rates) == 5
        assert rates[0]["taxa_inicio"] == 100.0
        assert rates[-1]["taxa_inicio"] == 72.0


class TestRetentionCalculation:

    def test_retention_rate(self):
        df = pd.DataFrame({
            "ano": [2020, 2021, 2022, 2023],
            "total_matriculas": [100000, 95000, 93000, 92000],
        })
        result = calculate_retention_rate(df)
        assert "taxa_retencao" in result.columns
        assert "taxa_evasao" in result.columns
