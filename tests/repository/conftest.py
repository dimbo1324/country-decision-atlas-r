"""Integration tests against a real Postgres instance (P2-7, Аудит-эпизод 8).

Repository unit tests elsewhere mock the connection entirely, so the actual
SQL never runs outside the Docker-based smoke/E2E jobs. This layer runs the
real queries for the highest-traffic repository functions, against a real,
migrated database.

Gated behind RUN_REPOSITORY_INTEGRATION_TESTS=1, mirroring the
RUN_RUNTIME_SMOKE_TESTS pattern in tests/smoke/test_api_runtime_smoke.py.
That pattern uses a module-level `pytestmark`, which only covers tests in
the same file - this package has multiple test files, so the skip lives in
the shared `connection` fixture instead, which every test here depends on.

Each test runs inside one transaction that is rolled back on teardown, so
this layer never leaves residue in whichever database DATABASE_URL points
at.
"""

import os
import psycopg
import pytest
import uuid
from collections.abc import Iterator
from psycopg.rows import dict_row
from typing import Any


RUN_REPOSITORY_INTEGRATION_TESTS = (
    os.getenv("RUN_REPOSITORY_INTEGRATION_TESTS") == "1"
)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://country_atlas:change-me@localhost:5432/country_atlas",
)


@pytest.fixture
def connection() -> Iterator[psycopg.Connection[dict[str, Any]]]:
    if not RUN_REPOSITORY_INTEGRATION_TESTS:
        pytest.skip("Repository integration tests are disabled.")
    conn: psycopg.Connection[dict[str, Any]] = psycopg.connect(
        DATABASE_URL, row_factory=dict_row
    )
    try:
        yield conn
    finally:
        conn.rollback()
        conn.close()


@pytest.fixture
def unique_suffix() -> str:
    return uuid.uuid4().hex[:12]
