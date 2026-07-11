"""Stage 7 smoke checks: a full pipeline run stays within a time/size
budget, produces the artifacts required by spec section 20, and CLI errors
for a missing dataset are actionable (spec section 12: reason + known
ids)."""

from __future__ import annotations

import json
import pytest
import time
import zipfile
from pathlib import Path
from scripts.synthetic_data import cli
from scripts.synthetic_data.core.paths import DEFAULT_WORLD_INPUT_FILE


# Generous margins over the ~23s / ~5MB observed locally: catches a
# runaway regression (e.g. unsubsetted fonts, duplicated locale content)
# without being flaky on a slower CI machine.
_MAX_GENERATE_SECONDS = 120
_MAX_ZIP_BYTES = 25 * 1024 * 1024


def test_full_balanced_world_stays_within_time_and_size_budget(
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "output_data"

    started = time.monotonic()
    exit_code = cli.main(
        [
            "generate",
            "--world-input",
            str(DEFAULT_WORLD_INPUT_FILE),
            "--profile",
            "balanced",
            "--seed",
            "42017",
            "--output-root",
            str(output_root),
        ]
    )
    elapsed = time.monotonic() - started

    assert exit_code == 0
    assert elapsed < _MAX_GENERATE_SECONDS, (
        f"full generate took {elapsed:.1f}s, budget is {_MAX_GENERATE_SECONDS}s"
    )

    dataset_dir = next(output_root.iterdir())
    world = json.loads(
        (dataset_dir / "canonical" / "synthetic_world.json").read_text(
            encoding="utf-8"
        )
    )
    assert 4 <= len(world["countries"]) <= 5
    assert len(world["scenarios"]) >= 3
    assert len(world["metadata"]["supported_locales"]) == 15

    manifest = json.loads(
        (dataset_dir / "manifest.json").read_text(encoding="utf-8")
    )
    locales_with_artifacts = {
        entry["locale"] for entry in manifest["artifacts"] if entry["locale"]
    }
    assert locales_with_artifacts == set(world["metadata"]["supported_locales"])

    sql_dir = dataset_dir / "sql"
    assert (sql_dir / "seed_synthetic_world.sql").exists()
    assert (sql_dir / "cleanup_synthetic_world.sql").exists()

    zip_path = next((dataset_dir / "package").glob("*.zip"))
    zip_size = zip_path.stat().st_size
    assert zip_size < _MAX_ZIP_BYTES, (
        f"package zip is {zip_size} bytes, budget is {_MAX_ZIP_BYTES}"
    )
    with zipfile.ZipFile(zip_path) as archive:
        assert archive.testzip() is None
        assert "manifest.json" in archive.namelist()


def test_render_error_for_unknown_dataset_lists_known_ids(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    output_root = tmp_path / "output_data"
    generate_exit_code = cli.main(
        [
            "generate",
            "--world-input",
            str(DEFAULT_WORLD_INPUT_FILE),
            "--seed",
            "42017",
            "--output-root",
            str(output_root),
            "--formats",
            "json",
        ]
    )
    assert generate_exit_code == 0
    real_dataset_id = next(output_root.iterdir()).name
    capsys.readouterr()

    exit_code = cli.main(
        [
            "render",
            "--dataset",
            "syn-does-not-exist",
            "--output-root",
            str(output_root),
        ]
    )

    assert exit_code == 2
    error = capsys.readouterr().err
    assert "syn-does-not-exist" in error
    assert str(output_root) in error
    assert "known dataset ids" in error
    assert real_dataset_id in error


def test_package_error_for_unknown_dataset_lists_known_ids(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    output_root = tmp_path / "output_data"
    generate_exit_code = cli.main(
        [
            "generate",
            "--world-input",
            str(DEFAULT_WORLD_INPUT_FILE),
            "--seed",
            "42017",
            "--output-root",
            str(output_root),
            "--formats",
            "json",
        ]
    )
    assert generate_exit_code == 0
    capsys.readouterr()

    exit_code = cli.main(
        [
            "package",
            "--dataset",
            "syn-does-not-exist",
            "--output-root",
            str(output_root),
        ]
    )

    assert exit_code == 2
    error = capsys.readouterr().err
    assert "known dataset ids" in error
