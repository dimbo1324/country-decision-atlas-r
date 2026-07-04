import json
from collections.abc import Iterable, Mapping
from datetime import UTC, date, datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Any


def clamp(value: float, minimum: float = 0.0, maximum: float = 100.0) -> float:
    return max(minimum, min(maximum, value))


def decimal_score(value: float) -> Decimal:
    return Decimal(str(clamp(value))).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )


def risk_label(value: Decimal | None) -> str:
    if value is None:
        return "insufficient_data"
    numeric = float(value)
    if numeric < 20:
        return "low"
    if numeric < 45:
        return "moderate"
    if numeric < 70:
        return "elevated"
    if numeric < 90:
        return "high"
    return "critical"


def velocity_label(value: Decimal | None) -> str:
    if value is None:
        return "insufficient_data"
    numeric = float(value)
    if numeric < 20:
        return "low"
    if numeric < 50:
        return "moderate"
    if numeric < 75:
        return "elevated"
    if numeric < 90:
        return "high"
    return "critical"


def normalize_groups(value: Any) -> list[str]:
    raw: Any = value
    if raw is None:
        return []
    if isinstance(raw, str):
        try:
            decoded = json.loads(raw)
        except json.JSONDecodeError:
            decoded = [raw]
        raw = decoded
    if isinstance(raw, Iterable) and not isinstance(
        raw, bytes | bytearray | str
    ):
        return sorted(
            {
                str(item).strip()
                for item in raw
                if str(item).strip() and str(item).strip() != "None"
            }
        )
    return []


def parse_date(value: Any) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.astimezone(UTC).date() if value.tzinfo else value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).date()
        except ValueError:
            try:
                return date.fromisoformat(value)
            except ValueError:
                return None
    return None


def days_old(value: Any, today: date | None = None) -> int | None:
    parsed = parse_date(value)
    if parsed is None:
        return None
    current = today or date.today()
    return max(0, (current - parsed).days)


def unique_count(rows: Iterable[Mapping[str, Any]], key: str) -> int:
    return len({str(row[key]) for row in rows if row.get(key) is not None})


def frequency(items: Iterable[str], limit: int = 5) -> list[dict[str, Any]]:
    counts: dict[str, int] = {}
    for item in items:
        if item:
            counts[item] = counts.get(item, 0) + 1
    return [
        {"value": key, "count": count}
        for key, count in sorted(
            counts.items(), key=lambda entry: (-entry[1], entry[0])
        )[:limit]
    ]
