from __future__ import annotations

import shutil
from dataclasses import dataclass
from pathlib import Path
from utils.synthetic_data.core.dataset_discovery import (
    DatasetSummary,
    list_datasets,
)


@dataclass(frozen=True)
class PruneResult:
    kept: tuple[str, ...]
    removed: tuple[str, ...]


def _sort_key(summary: DatasetSummary) -> tuple[float, str]:
    manifest_path = summary.path / "manifest.json"
    reference = manifest_path if manifest_path.exists() else summary.path
    return (reference.stat().st_mtime, summary.dataset_id)


def plan_prune(output_root: Path, *, keep_last: int) -> PruneResult:
    """Decide which datasets under `output_root` to keep/remove without
    touching the filesystem — newest `keep_last` by manifest (or
    directory) mtime survive."""
    if keep_last < 0:
        raise ValueError("keep_last must not be negative")
    datasets = sorted(list_datasets(output_root), key=_sort_key, reverse=True)
    kept = tuple(summary.dataset_id for summary in datasets[:keep_last])
    removed = tuple(summary.dataset_id for summary in datasets[keep_last:])
    return PruneResult(kept=kept, removed=removed)


def apply_prune(output_root: Path, plan: PruneResult) -> None:
    for dataset_id in plan.removed:
        target = output_root / dataset_id
        if target.exists():
            shutil.rmtree(target)
