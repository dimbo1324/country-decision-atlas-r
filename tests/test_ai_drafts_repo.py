"""SQL-only repository layer for AI drafts: required functions and reviewed_at bookkeeping."""

from app.repositories import ai_drafts as repository
import inspect


def test_ai_drafts_repository_is_sql_only() -> None:
    source = inspect.getsource(repository)

    assert "fastapi" not in source
    assert "BaseModel" not in source
    assert "AIProvider" not in source
    assert "INSERT INTO ai_drafts" in source


def test_ai_drafts_repository_has_required_functions() -> None:
    assert hasattr(repository, "insert_ai_draft")
    assert hasattr(repository, "get_ai_draft")
    assert hasattr(repository, "list_ai_drafts")
    assert hasattr(repository, "update_ai_draft_status")
    assert hasattr(repository, "count_ai_drafts")


def test_ai_drafts_repository_status_update_sets_reviewed_at() -> None:
    source = inspect.getsource(repository.update_ai_draft_status)

    assert "reviewed_at = NOW()" in source
    assert "status = %s" in source
