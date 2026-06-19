from collections.abc import Mapping


def resolve_sort_clause(
    sort: str,
    order: str,
    columns: Mapping[str, str],
    default_sort: str,
) -> tuple[str, str]:
    sort_column = columns.get(sort, columns[default_sort])
    order_sql = "ASC" if order == "asc" else "DESC"
    return sort_column, order_sql
