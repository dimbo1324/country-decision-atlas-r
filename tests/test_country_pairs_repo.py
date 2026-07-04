"""Country-pair repository queries filter to published sources/evidence only."""

import re
from app.repositories import country_pairs as repository


def test_get_country_pair_compatibility_filters_published_only() -> None:
    sql_source = _function_sql(repository.get_country_pair_compatibility)
    assert "cpc.status = 'published'" in sql_source


def test_list_destination_compatibility_filters_published_only() -> None:
    sql_source = _function_sql(repository.list_destination_compatibility)
    assert "cpc.status = 'published'" in sql_source


def test_list_pair_sources_filters_published_sources() -> None:
    sql_source = _function_sql(repository.list_pair_sources)
    assert "s.status = 'published'" in sql_source


def test_list_pair_evidence_filters_published_evidence() -> None:
    sql_source = _function_sql(repository.list_pair_evidence)
    assert "ei.status = 'published'" in sql_source


def test_repository_uses_parameterized_queries_only() -> None:
    import inspect

    module_source = inspect.getsource(repository)
    for line in module_source.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        assert not re.search(r"f\"\"\".*\{[a-z_]+_slug\}", stripped)


def test_repository_has_no_fastapi_import() -> None:
    import inspect

    module_source = inspect.getsource(repository)
    assert "fastapi" not in module_source.lower()


def test_repository_has_no_pydantic_import() -> None:
    import inspect

    module_source = inspect.getsource(repository)
    assert "pydantic" not in module_source.lower()


def test_repository_has_no_service_import() -> None:
    import inspect

    module_source = inspect.getsource(repository)
    assert "app.services" not in module_source


def _function_sql(func: object) -> str:
    import inspect

    return inspect.getsource(func)  # type: ignore[arg-type]
