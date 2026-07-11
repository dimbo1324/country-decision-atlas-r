from __future__ import annotations

import json
from pathlib import Path
from scripts.synthetic_data.core.dataset_discovery import (
    available_dataset_ids,
    find_dataset_dir,
    list_datasets,
)


def _write_fake_dataset(
    root: Path, dataset_id: str, *, seed: int = 1, profile: str = "balanced"
) -> Path:
    dataset_dir = root / dataset_id
    canonical_dir = dataset_dir / "canonical"
    canonical_dir.mkdir(parents=True, exist_ok=True)
    (canonical_dir / "synthetic_world.json").write_text(
        json.dumps(
            {
                "metadata": {
                    "dataset_id": dataset_id,
                    "seed": seed,
                    "profile": profile,
                    "generated_on": "2026-01-01",
                },
                "countries": [{"name": "A"}, {"name": "B"}],
            }
        ),
        encoding="utf-8",
    )
    return dataset_dir


def test_list_datasets_returns_empty_for_missing_root(tmp_path: Path) -> None:
    assert list_datasets(tmp_path / "does-not-exist") == []


def test_list_datasets_skips_directories_without_a_canonical_world(
    tmp_path: Path,
) -> None:
    (tmp_path / "not-a-dataset").mkdir()
    _write_fake_dataset(tmp_path, "syn-real")

    summaries = list_datasets(tmp_path)

    assert [summary.dataset_id for summary in summaries] == ["syn-real"]


def test_list_datasets_reports_seed_profile_and_country_count(
    tmp_path: Path,
) -> None:
    _write_fake_dataset(tmp_path, "syn-a", seed=42, profile="crisis")

    summaries = list_datasets(tmp_path)

    assert len(summaries) == 1
    summary = summaries[0]
    assert summary.seed == 42
    assert summary.profile == "crisis"
    assert summary.country_count == 2
    assert summary.size_bytes > 0


def test_find_dataset_dir_finds_it_at_the_given_root(tmp_path: Path) -> None:
    _write_fake_dataset(tmp_path, "syn-a")

    found = find_dataset_dir("syn-a", primary_root=tmp_path)

    assert found == tmp_path / "syn-a"


def test_find_dataset_dir_returns_none_when_missing_everywhere(
    tmp_path: Path,
) -> None:
    assert find_dataset_dir("syn-ghost", primary_root=tmp_path) is None


def test_available_dataset_ids_merges_multiple_roots_without_duplicates(
    tmp_path: Path,
) -> None:
    root_a = tmp_path / "a"
    root_b = tmp_path / "b"
    _write_fake_dataset(root_a, "syn-shared")
    _write_fake_dataset(root_b, "syn-shared")
    _write_fake_dataset(root_b, "syn-only-in-b")

    ids = available_dataset_ids(root_a, root_b)

    assert ids == ["syn-shared", "syn-only-in-b"]
