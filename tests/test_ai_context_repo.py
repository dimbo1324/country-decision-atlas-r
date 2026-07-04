"""Repository queries that assemble grounded AI context from published search documents and stored metrics."""

import inspect
from app.repositories import ai_context as repository


def test_ai_context_repository_uses_published_search_documents() -> None:
    source = inspect.getsource(repository)

    assert "sd.status = 'published'" in source
    assert "search_documents" in source


def test_metric_context_reads_stored_values_without_recompute() -> None:
    source = inspect.getsource(repository)

    assert "country_platform_metrics" in source
    assert "country_trust_scores" in source
    assert "country_drift_snapshots" in source
    assert "recompute" not in source.casefold()
