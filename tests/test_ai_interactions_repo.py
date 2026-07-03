"""SQL-only repository for logging and listing AI interaction records."""

from app.repositories import ai_interactions as repository
import inspect


def test_repository_is_sql_only() -> None:
    source = inspect.getsource(repository)

    assert "fastapi" not in source
    assert "AIProvider" not in source
    assert "BaseModel" not in source
    assert "INSERT INTO ai_interaction_logs" in source


def test_repository_supports_insert_count_and_admin_list() -> None:
    source = inspect.getsource(repository)

    assert "def insert_ai_interaction_log" in source
    assert "def count_ai_interactions" in source
    assert "def list_ai_interaction_logs_for_admin" in source
    assert "sanitized_preview" in source
