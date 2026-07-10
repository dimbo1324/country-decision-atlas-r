"""Shared list-pagination helper used by author metrics, capabilities, country contribution, migration board, and the moderation feed (P3-11, Аудит-эпизод 10)."""

from app.services.list_helpers import total_from_window_count


def test_total_returns_zero_for_empty_rows() -> None:
    assert total_from_window_count([]) == 0


def test_total_reads_window_function_count() -> None:
    rows = [{"total_count": 42}, {"total_count": 42}]
    assert total_from_window_count(rows) == 42


def test_total_falls_back_to_row_count_without_window_column() -> None:
    rows = [{"id": "a"}, {"id": "b"}, {"id": "c"}]
    assert total_from_window_count(rows) == 3
