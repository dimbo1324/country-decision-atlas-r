from __future__ import annotations

import json
from pathlib import Path
from utils.synthetic_data import cli
from utils.synthetic_data.core.paths import DEFAULT_WORLD_INPUT_FILE


def _dataset_dir(output_root: Path) -> Path:
    return next(output_root.iterdir())


def test_generate_formats_web_renders_a_website(tmp_path: Path) -> None:
    output_root = tmp_path / "output_data"

    exit_code = cli.main(
        [
            "generate",
            "--world-input",
            str(DEFAULT_WORLD_INPUT_FILE),
            "--seed",
            "42017",
            "--scale",
            "small",
            "--output-root",
            str(output_root),
            "--formats",
            "web",
        ]
    )

    assert exit_code == 0
    dataset_dir = _dataset_dir(output_root)
    assert (dataset_dir / "websites" / "graph.json").exists()
    assert (dataset_dir / "websites" / "source_pages.json").exists()

    manifest = json.loads(
        (dataset_dir / "manifest.json").read_text(encoding="utf-8")
    )
    website_entries = [
        a for a in manifest["artifacts"] if a["path"].startswith("websites/")
    ]
    assert website_entries

    validation_report = json.loads(
        (dataset_dir / "reports" / "validation_report.json").read_text(
            encoding="utf-8"
        )
    )
    assert validation_report["status"] == "valid"


def test_generate_without_web_format_does_not_render_a_website(
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
            "--scale",
            "small",
            "--output-root",
            str(output_root),
            "--formats",
            "json",
        ]
    )

    assert exit_code == 0
    dataset_dir = _dataset_dir(output_root)
    assert not (dataset_dir / "websites").exists()


def test_render_web_reuses_already_rendered_documents_for_downloads(
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "output_data"
    cli.main(
        [
            "generate",
            "--world-input",
            str(DEFAULT_WORLD_INPUT_FILE),
            "--seed",
            "42017",
            "--scale",
            "small",
            "--output-root",
            str(output_root),
            "--formats",
            "pdf",
        ]
    )
    dataset_dir = _dataset_dir(output_root)
    dataset_id = dataset_dir.name

    exit_code = cli.main(
        [
            "render-web",
            "--dataset",
            dataset_id,
            "--output-root",
            str(output_root),
        ]
    )

    assert exit_code == 0
    graph_payload = json.loads(
        (dataset_dir / "websites" / "graph.json").read_text(encoding="utf-8")
    )
    download_links = [
        link
        for site in graph_payload["sites"]
        for page in site["pages"]
        for link in page["links"]
        if link["kind"] == "download"
    ]
    assert download_links


def test_render_web_without_a_dataset_flag_is_an_error() -> None:
    assert cli.main(["render-web"]) == 2


def test_render_web_dry_run_writes_nothing(tmp_path: Path) -> None:
    output_root = tmp_path / "output_data"
    cli.main(
        [
            "generate",
            "--world-input",
            str(DEFAULT_WORLD_INPUT_FILE),
            "--seed",
            "42017",
            "--scale",
            "small",
            "--output-root",
            str(output_root),
            "--formats",
            "json",
        ]
    )
    dataset_dir = _dataset_dir(output_root)

    exit_code = cli.main(
        [
            "render-web",
            "--dataset",
            dataset_dir.name,
            "--output-root",
            str(output_root),
            "--dry-run",
        ]
    )

    assert exit_code == 0
    assert not (dataset_dir / "websites").exists()


def test_serve_without_a_generated_website_is_a_clear_error(
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "output_data"
    cli.main(
        [
            "generate",
            "--world-input",
            str(DEFAULT_WORLD_INPUT_FILE),
            "--seed",
            "42017",
            "--scale",
            "small",
            "--output-root",
            str(output_root),
            "--formats",
            "json",
        ]
    )
    dataset_dir = _dataset_dir(output_root)

    exit_code = cli.main(
        [
            "serve",
            "--dataset",
            dataset_dir.name,
            "--output-root",
            str(output_root),
        ]
    )

    assert exit_code == 2


def test_unknown_format_alias_is_rejected(tmp_path: Path) -> None:
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
            "not-a-real-format",
        ]
    )

    assert exit_code == 2
