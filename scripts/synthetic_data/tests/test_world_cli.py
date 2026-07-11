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
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
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
    # The production guard must fire before dataset autodiscovery even
    # looks at disk — a nonexistent "syn-doesnotmatter" dataset must not
    # produce a "not found" error that masks the production block.
    assert "production" in capsys.readouterr().err.lower()


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


def test_load_sql_dry_run_previews_target_without_connecting(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("APP_ENV", "local")

    exit_code = cli.main(
        [
            "load-sql",
            "--dataset",
            "syn-doesnotmatter",
            "--output-root",
            str(tmp_path),
            "--database-url",
            "postgresql://user@localhost:5433/db",
            "--dry-run",
        ]
    )

    assert exit_code == 0


def test_load_sql_dry_run_reports_production_block_without_dataset_lookup(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("APP_ENV", raising=False)

    exit_code = cli.main(
        [
            "load-sql",
            "--dataset",
            "syn-doesnotmatter",
            "--output-root",
            str(tmp_path),
            "--database-url",
            "postgresql://user@localhost:5433/db",
            "--dry-run",
        ]
    )

    assert exit_code == 2


def test_schema_prints_synthetic_world_json_schema() -> None:
    exit_code = cli.main(["schema"])

    assert exit_code == 0


def test_list_reports_empty_output_root(tmp_path: Path) -> None:
    exit_code = cli.main(["list", "--output-root", str(tmp_path)])

    assert exit_code == 0


def test_list_reports_generated_dataset(tmp_path: Path) -> None:
    generate_exit_code = cli.main(
        [
            "generate",
            "--world-input",
            str(DEFAULT_WORLD_INPUT_FILE),
            "--seed",
            "1",
            "--output-root",
            str(tmp_path),
            "--formats",
            "json",
        ]
    )
    assert generate_exit_code == 0

    exit_code = cli.main(["list", "--output-root", str(tmp_path), "--json"])

    assert exit_code == 0


def test_package_rebuilds_manifest_without_rerendering(tmp_path: Path) -> None:
    generate_exit_code = cli.main(
        [
            "generate",
            "--world-input",
            str(DEFAULT_WORLD_INPUT_FILE),
            "--seed",
            "2",
            "--output-root",
            str(tmp_path),
            "--formats",
            "json",
        ]
    )
    assert generate_exit_code == 0
    dataset_dir = next(tmp_path.iterdir())
    dataset_id = dataset_dir.name
    manifest_before = (dataset_dir / "manifest.json").read_text(
        encoding="utf-8"
    )
    documents_before = sorted(
        path.name for path in (dataset_dir / "documents").rglob("*.json")
    )

    exit_code = cli.main(
        ["package", "--dataset", dataset_id, "--output-root", str(tmp_path)]
    )

    assert exit_code == 0
    documents_after = sorted(
        path.name for path in (dataset_dir / "documents").rglob("*.json")
    )
    assert documents_after == documents_before
    manifest_after = (dataset_dir / "manifest.json").read_text(encoding="utf-8")
    assert (
        json.loads(manifest_after)["dataset_id"]
        == json.loads(manifest_before)["dataset_id"]
    )


def test_package_dry_run_does_not_touch_manifest(tmp_path: Path) -> None:
    generate_exit_code = cli.main(
        [
            "generate",
            "--world-input",
            str(DEFAULT_WORLD_INPUT_FILE),
            "--seed",
            "3",
            "--output-root",
            str(tmp_path),
            "--formats",
            "json",
        ]
    )
    assert generate_exit_code == 0
    dataset_dir = next(tmp_path.iterdir())
    dataset_id = dataset_dir.name
    manifest_before_mtime = (dataset_dir / "manifest.json").stat().st_mtime

    exit_code = cli.main(
        [
            "package",
            "--dataset",
            dataset_id,
            "--output-root",
            str(tmp_path),
            "--dry-run",
        ]
    )

    assert exit_code == 0
    assert (
        dataset_dir / "manifest.json"
    ).stat().st_mtime == manifest_before_mtime


def test_package_without_dataset_flag_fails_cleanly() -> None:
    exit_code = cli.main(["package"])

    assert exit_code == 2


def test_prune_requires_keep_last(tmp_path: Path) -> None:
    exit_code = cli.main(["prune", "--output-root", str(tmp_path)])

    assert exit_code == 2


def test_prune_dry_run_removes_nothing(tmp_path: Path) -> None:
    generate_exit_code = cli.main(
        [
            "generate",
            "--world-input",
            str(DEFAULT_WORLD_INPUT_FILE),
            "--seed",
            "4",
            "--output-root",
            str(tmp_path),
            "--formats",
            "json",
        ]
    )
    assert generate_exit_code == 0

    exit_code = cli.main(
        [
            "prune",
            "--output-root",
            str(tmp_path),
            "--keep-last",
            "0",
            "--dry-run",
        ]
    )

    assert exit_code == 0
    assert list(tmp_path.iterdir())


def test_prune_without_confirm_does_not_delete(tmp_path: Path) -> None:
    generate_exit_code = cli.main(
        [
            "generate",
            "--world-input",
            str(DEFAULT_WORLD_INPUT_FILE),
            "--seed",
            "5",
            "--output-root",
            str(tmp_path),
            "--formats",
            "json",
        ]
    )
    assert generate_exit_code == 0

    exit_code = cli.main(
        ["prune", "--output-root", str(tmp_path), "--keep-last", "0"]
    )

    assert exit_code == 2
    assert list(tmp_path.iterdir())


def test_prune_with_confirm_deletes(tmp_path: Path) -> None:
    generate_exit_code = cli.main(
        [
            "generate",
            "--world-input",
            str(DEFAULT_WORLD_INPUT_FILE),
            "--seed",
            "6",
            "--output-root",
            str(tmp_path),
            "--formats",
            "json",
        ]
    )
    assert generate_exit_code == 0

    exit_code = cli.main(
        [
            "prune",
            "--output-root",
            str(tmp_path),
            "--keep-last",
            "0",
            "--confirm",
        ]
    )

    assert exit_code == 0
    assert list(tmp_path.iterdir()) == []


def test_generate_json_flag_prints_a_single_json_object(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = cli.main(
        [
            "generate",
            "--world-input",
            str(DEFAULT_WORLD_INPUT_FILE),
            "--seed",
            "7",
            "--output-root",
            str(tmp_path),
            "--formats",
            "json",
            "--json",
        ]
    )

    assert exit_code == 0
    out = capsys.readouterr().out.strip()
    payload = json.loads(out)
    assert payload["dataset_id"].startswith("syn-")
    assert "manifest_path" in payload


def test_quiet_flag_suppresses_routine_output(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = cli.main(
        [
            "plan",
            "--world-input",
            str(DEFAULT_WORLD_INPUT_FILE),
            "--seed",
            "8",
            "--output-root",
            str(tmp_path),
            "--quiet",
        ]
    )

    assert exit_code == 0
    assert capsys.readouterr().out == ""


def test_render_autodiscovers_dataset_from_default_output_root(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from scripts.synthetic_data.core import dataset_discovery

    # `find_dataset_dir` reads its own module-local binding of
    # DEFAULT_OUTPUT_DATA_ROOT (imported at module load time), so that is
    # the name that must be patched for the fallback lookup to see it.
    monkeypatch.setattr(dataset_discovery, "DEFAULT_OUTPUT_DATA_ROOT", tmp_path)

    generate_exit_code = cli.main(
        [
            "generate",
            "--world-input",
            str(DEFAULT_WORLD_INPUT_FILE),
            "--seed",
            "9",
            "--output-root",
            str(tmp_path),
            "--formats",
            "json",
        ]
    )
    assert generate_exit_code == 0
    dataset_id = next(tmp_path.iterdir()).name

    other_root = tmp_path / "unrelated-empty-root"
    exit_code = cli.main(
        [
            "render",
            "--dataset",
            dataset_id,
            "--output-root",
            str(other_root),
            "--formats",
            "txt",
        ]
    )

    assert exit_code == 0


def test_render_reports_known_dataset_ids_when_not_found(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = cli.main(
        ["render", "--dataset", "syn-ghost", "--output-root", str(tmp_path)]
    )

    assert exit_code == 2
    assert "not found" in capsys.readouterr().err


def test_diff_requires_both_dataset_flags() -> None:
    exit_code = cli.main(["diff", "--dataset-a", "syn-a"])

    assert exit_code == 2


def test_diff_reports_unknown_dataset_id(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    exit_code = cli.main(
        [
            "diff",
            "--dataset-a",
            "syn-ghost-a",
            "--dataset-b",
            "syn-ghost-b",
            "--output-root",
            str(tmp_path),
        ]
    )

    assert exit_code == 2
    assert "syn-ghost-a" in capsys.readouterr().err


def _generate_json_dataset(
    output_root: Path, *, seed: int, profile: str = "balanced"
) -> str:
    before = (
        {path.name for path in output_root.iterdir()}
        if output_root.exists()
        else set()
    )
    exit_code = cli.main(
        [
            "generate",
            "--world-input",
            str(DEFAULT_WORLD_INPUT_FILE),
            "--seed",
            str(seed),
            "--profile",
            profile,
            "--output-root",
            str(output_root),
            "--formats",
            "json",
        ]
    )
    assert exit_code == 0
    after = {path.name for path in output_root.iterdir()}
    (new_dataset_id,) = after - before
    return new_dataset_id


def test_diff_of_identical_dataset_reports_zero_exit_code(
    tmp_path: Path,
) -> None:
    dataset_id = _generate_json_dataset(tmp_path, seed=9001)

    exit_code = cli.main(
        [
            "diff",
            "--dataset-a",
            dataset_id,
            "--dataset-b",
            dataset_id,
            "--output-root",
            str(tmp_path),
        ]
    )

    assert exit_code == 0


def test_diff_of_different_seeds_lists_added_and_removed_countries(
    tmp_path: Path,
) -> None:
    dataset_id_a = _generate_json_dataset(tmp_path, seed=9001)
    dataset_id_b = _generate_json_dataset(tmp_path, seed=9002)

    exit_code = cli.main(
        [
            "diff",
            "--dataset-a",
            dataset_id_a,
            "--dataset-b",
            dataset_id_b,
            "--output-root",
            str(tmp_path),
            "--json",
        ]
    )

    assert exit_code == 1


def test_diff_json_flag_prints_a_single_parseable_json_object(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    dataset_id_a = _generate_json_dataset(tmp_path, seed=9101)
    dataset_id_b = _generate_json_dataset(tmp_path, seed=9102)
    capsys.readouterr()

    exit_code = cli.main(
        [
            "diff",
            "--dataset-a",
            dataset_id_a,
            "--dataset-b",
            dataset_id_b,
            "--output-root",
            str(tmp_path),
            "--json",
        ]
    )

    assert exit_code == 1
    payload = json.loads(capsys.readouterr().out)
    assert payload["dataset_id_a"] == dataset_id_a
    assert payload["dataset_id_b"] == dataset_id_b
    assert payload["is_identical"] is False
    assert payload["countries_added"]
    assert payload["countries_removed"]
