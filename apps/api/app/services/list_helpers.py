from typing import Any


def total_from_window_count(rows: list[dict[str, Any]]) -> int:
    """Reads the `COUNT(*) OVER()` window-count column repositories attach
    to the first row of a paginated list query, falling back to the number
    of rows returned when the list is empty or the column is absent.

    Shared across author_metrics, capabilities, country_contribution,
    migration_board, and moderation_feed, which each used to carry their
    own byte-identical copy (P3-11, Аудит-эпизод 10).
    """
    if not rows:
        return 0
    return int(rows[0].get("total_count") or len(rows))
