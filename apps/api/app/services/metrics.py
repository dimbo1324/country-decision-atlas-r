import threading
from app.core.database import get_pool_stats
from collections import defaultdict


# Minimal in-process metrics, no prometheus-client dependency (P2-1, Аудит-
# эпизод 7): request count by response status, a latency histogram, and the
# DB pool gauges from AE-6's get_pool_stats(). Deliberately hand-rolls the
# Prometheus text exposition format (a simple, stable, documented format)
# rather than pulling in a library for ~30 lines of counter bookkeeping.
_LATENCY_BUCKETS_SECONDS: tuple[float, ...] = (
    0.01,
    0.05,
    0.1,
    0.25,
    0.5,
    1.0,
    2.5,
    5.0,
    10.0,
)

_lock = threading.Lock()
_request_count_by_status: dict[int, int] = defaultdict(int)
_latency_bucket_counts: dict[float, int] = defaultdict(int)
_latency_sum_seconds: float = 0.0
_latency_count: int = 0


def record_request(status_code: int, duration_seconds: float) -> None:
    global _latency_sum_seconds, _latency_count
    with _lock:
        _request_count_by_status[status_code] += 1
        _latency_sum_seconds += duration_seconds
        _latency_count += 1
        for bucket in _LATENCY_BUCKETS_SECONDS:
            if duration_seconds <= bucket:
                _latency_bucket_counts[bucket] += 1
        _latency_bucket_counts[float("inf")] += 1


def reset_metrics() -> None:
    """Test-only: clear accumulated counters between test cases."""
    global _latency_sum_seconds, _latency_count
    with _lock:
        _request_count_by_status.clear()
        _latency_bucket_counts.clear()
        _latency_sum_seconds = 0.0
        _latency_count = 0


def render_prometheus_text() -> str:
    with _lock:
        status_counts = dict(_request_count_by_status)
        bucket_counts = dict(_latency_bucket_counts)
        latency_sum = _latency_sum_seconds
        latency_count = _latency_count

    lines: list[str] = []
    lines.append(
        "# HELP http_requests_total Total HTTP requests processed, "
        "labeled by response status code."
    )
    lines.append("# TYPE http_requests_total counter")
    for status_code in sorted(status_counts):
        lines.append(
            f'http_requests_total{{status="{status_code}"}} '
            f"{status_counts[status_code]}"
        )

    lines.append(
        "# HELP http_request_duration_seconds HTTP request latency in seconds."
    )
    lines.append("# TYPE http_request_duration_seconds histogram")
    cumulative = 0
    for bucket in _LATENCY_BUCKETS_SECONDS:
        cumulative = bucket_counts.get(bucket, 0)
        lines.append(
            f'http_request_duration_seconds_bucket{{le="{bucket}"}} {cumulative}'
        )
    lines.append(
        'http_request_duration_seconds_bucket{le="+Inf"} '
        f"{bucket_counts.get(float('inf'), 0)}"
    )
    lines.append(f"http_request_duration_seconds_sum {latency_sum}")
    lines.append(f"http_request_duration_seconds_count {latency_count}")

    lines.append(
        "# HELP db_pool_connections Database connection pool gauges "
        "(size, available, requests_waiting)."
    )
    lines.append("# TYPE db_pool_connections gauge")
    try:
        pool_stats = get_pool_stats()
    except RuntimeError:
        pool_stats = {}
    for key in ("pool_size", "pool_available", "requests_waiting"):
        if key in pool_stats:
            lines.append(
                f'db_pool_connections{{stat="{key}"}} {pool_stats[key]}'
            )

    return "\n".join(lines) + "\n"
