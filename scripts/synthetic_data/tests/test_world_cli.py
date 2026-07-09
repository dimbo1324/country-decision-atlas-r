from __future__ import annotations

import json
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
        "errors": [],
        "status": "valid",
    }


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
