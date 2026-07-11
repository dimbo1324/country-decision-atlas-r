from __future__ import annotations

import json
import pytest
from pathlib import Path
from scripts.synthetic_data import cli
from scripts.synthetic_data.core.paths import DEFAULT_WORLD_INPUT_FILE


def test_validate_world_input_returns_success() -> None:
    assert (
        cli.main(["validate", "--world-input", str(DEFAULT_WORLD_INPUT_FILE)])
        == 0
    )


def test_plan_does_not_create_output_root(tmp_path: Path) -> None:
    output_root = tmp_path / "output_data"

    exit_code = cli.main(
        [
            "plan",
            "--world-input",
            str(DEFAULT_WORLD_INPUT_FILE),
            "--seed",
            "42017",
            "--output-root",
            str(output_root),
        ]
    )

    assert exit_code == 0
    assert not output_root.exists()


def test_generate_writes_canonical_world_and_validation_report(
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "output_data"

    exit_code = cli.main(
        [
            "generate",
            "--world-input",
            str(DEFAULT_WORLD_INPUT_FILE),
            "--seed",
            "42017",
            "--output-root",
            str(output_root),
            "--formats",
            "json,txt",
        ]
    )

    assert exit_code == 0
    dataset_dir = next(output_root.iterdir())
    payload = json.loads(
        (dataset_dir / "canonical" / "synthetic_world.json").read_text(
            encoding="utf-8"
        )
    )
    report = json.loads(
        (dataset_dir / "reports" / "validation_report.json").read_text(
            encoding="utf-8"
        )
    )
    assert payload["metadata"]["seed"] == 42017
    assert len(payload["countries"]) == 5
    assert report == {
        "dataset_id": payload["metadata"]["dataset_id"],
        "world_errors": [],
        "artifact_errors": [],
        "status": "valid",
    }
    assert (dataset_dir / "manifest.json").exists()
    assert (dataset_dir / "reports" / "generation_summary.md").exists()
    zip_files = list((dataset_dir / "package").glob("*.zip"))
    assert len(zip_files) == 1
    for locale in payload["metadata"]["supported_locales"]:
        assert (dataset_dir / "documents" / locale / "json").is_dir()
        assert (dataset_dir / "documents" / locale / "txt").is_dir()


def test_generate_dry_run_creates_no_documents_or_package(
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "output_data"

    exit_code = cli.main(
        [
            "generate",
            "--world-input",
            str(DEFAULT_WORLD_INPUT_FILE),
            "--seed",
            "42017",
            "--output-root",
            str(output_root),
            "--dry-run",
        ]
    )

    assert exit_code == 0
    assert not output_root.exists()


def test_render_rebuilds_documents_from_existing_canonical_json(
    tmp_path: Path,
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
    dataset_dir = next(output_root.iterdir())
    payload = json.loads(
        (dataset_dir / "canonical" / "synthetic_world.json").read_text(
            encoding="utf-8"
        )
    )
    dataset_id = payload["metadata"]["dataset_id"]

    render_exit_code = cli.main(
        [
            "render",
            "--dataset",
            dataset_id,
            "--output-root",
            str(output_root),
            "--formats",
            "txt",
        ]
    )

    assert render_exit_code == 0
    for locale in payload["metadata"]["supported_locales"]:
        assert list((dataset_dir / "documents" / locale / "txt").glob("*.txt"))


def test_render_without_dataset_flag_fails_cleanly() -> None:
    exit_code = cli.main(["render"])

    assert exit_code == 2


def test_world_command_rejects_an_invalid_country_count() -> None:
    exit_code = cli.main(
        [
            "plan",
            "--world-input",
            str(DEFAULT_WORLD_INPUT_FILE),
            "--countries",
            "3",
        ]
    )

    assert exit_code == 2


def test_load_sql_without_dataset_flag_fails_cleanly() -> None:
    exit_code = cli.main(["load-sql", "--confirm"])

    assert exit_code == 2


def test_load_sql_without_confirm_flag_fails_cleanly(tmp_path: Path) -> None:
    exit_code = cli.main(
        [
            "load-sql",
            "--dataset",
            "syn-doesnotmatter",
            "--output-root",
            str(tmp_path),
        ]
    )

    assert exit_code == 2


def test_load_sql_refuses_in_production(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DATABASE_URL", "postgresql://unreachable-host/db")

    exit_code = cli.main(
        [
            "load-sql",
            "--dataset",
            "syn-doesnotmatter",
            "--output-root",
            str(tmp_path),
            "--confirm",
        ]
    )

    assert exit_code == 2


def test_load_sql_without_database_url_fails_cleanly(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_ENV", "local")
    monkeypatch.delenv("DATABASE_URL", raising=False)

    exit_code = cli.main(
        [
            "load-sql",
            "--dataset",
            "syn-doesnotmatter",
            "--output-root",
            str(tmp_path),
            "--confirm",
        ]
    )

    assert exit_code == 2
