from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from scripts.synthetic_data.core.paths import DEFAULT_OUTPUT_DATA_ROOT


@dataclass(frozen=True)
class DatasetSummary:
    dataset_id: str
    seed: int
    profile: str
    generated_on: str
    country_count: int
    size_bytes: int
    path: Path


def _dataset_dir_size(dataset_dir: Path) -> int:
    return sum(
        path.stat().st_size for path in dataset_dir.rglob("*") if path.is_file()
    )


def _read_metadata(dataset_dir: Path) -> dict[str, object] | None:
    canonical_path = dataset_dir / "canonical" / "synthetic_world.json"
    if not canonical_path.exists():
        return None
    try:
        payload = json.loads(canonical_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    metadata = payload.get("metadata")
    return metadata if isinstance(metadata, dict) else None


def list_datasets(output_root: Path) -> list[DatasetSummary]:
    """List every dataset directory under `output_root` that has a
    canonical world (skips anything that isn't a generated dataset)."""
    if not output_root.exists():
        return []
    summaries: list[DatasetSummary] = []
    for entry in sorted(output_root.iterdir()):
        if not entry.is_dir():
            continue
        metadata = _read_metadata(entry)
        if metadata is None:
            continue
        countries_path = entry / "canonical" / "synthetic_world.json"
        try:
            payload = json.loads(countries_path.read_text(encoding="utf-8"))
            country_count = len(payload.get("countries", []))
        except (OSError, json.JSONDecodeError):
            country_count = 0
        seed_value = metadata.get("seed", 0)
        summaries.append(
            DatasetSummary(
                dataset_id=str(metadata.get("dataset_id", entry.name)),
                seed=seed_value if isinstance(seed_value, int) else 0,
                profile=str(metadata.get("profile", "")),
                generated_on=str(metadata.get("generated_on", "")),
                country_count=country_count,
                size_bytes=_dataset_dir_size(entry),
                path=entry,
            )
        )
    return summaries


def find_dataset_dir(dataset_id: str, *, primary_root: Path) -> Path | None:
    """Look for `dataset_id` at `primary_root` first, then fall back to
    the default output root if it differs — a dataset generated with the
    default `--output-root` shouldn't become unreachable just because a
    later command forgot to repeat a custom `--output-root`."""
    candidate = primary_root / dataset_id
    if candidate.exists():
        return candidate
    if primary_root.resolve() != DEFAULT_OUTPUT_DATA_ROOT.resolve():
        fallback = DEFAULT_OUTPUT_DATA_ROOT / dataset_id
        if fallback.exists():
            return fallback
    return None


def available_dataset_ids(*roots: Path) -> list[str]:
    ids: list[str] = []
    seen: set[str] = set()
    for root in roots:
        if not root.exists():
            continue
        for entry in sorted(root.iterdir()):
            if entry.is_dir() and entry.name not in seen:
                seen.add(entry.name)
                ids.append(entry.name)
    return ids
