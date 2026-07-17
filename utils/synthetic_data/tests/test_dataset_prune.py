from __future__ import annotations

import json
import pytest
import time
from pathlib import Path
from utils.synthetic_data.core.dataset_prune import apply_prune, plan_prune


def _write_fake_dataset(root: Path, dataset_id: str) -> Path:
    dataset_dir = root / dataset_id
    canonical_dir = dataset_dir / "canonical"
    canonical_dir.mkdir(parents=True, exist_ok=True)
    (canonical_dir / "synthetic_world.json").write_text(
        json.dumps(
            {
                "metadata": {
                    "dataset_id": dataset_id,
                    "seed": 1,
                    "profile": "balanced",
                    "generated_on": "2026-01-01",
                },
                "countries": [],
            }
        ),
        encoding="utf-8",
    )
    return dataset_dir


def test_plan_prune_keeps_the_newest_n_datasets(tmp_path: Path) -> None:
    for name in ("syn-a", "syn-b", "syn-c"):
        _write_fake_dataset(tmp_path, name)
        time.sleep(0.01)

    plan = plan_prune(tmp_path, keep_last=2)

    assert plan.kept == ("syn-c", "syn-b")
    assert plan.removed == ("syn-a",)


def test_plan_prune_keep_last_zero_removes_everything(tmp_path: Path) -> None:
    _write_fake_dataset(tmp_path, "syn-a")

    plan = plan_prune(tmp_path, keep_last=0)

    assert plan.kept == ()
    assert plan.removed == ("syn-a",)


def test_plan_prune_rejects_negative_keep_last(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="not be negative"):
        plan_prune(tmp_path, keep_last=-1)


def test_apply_prune_deletes_only_the_removed_datasets(tmp_path: Path) -> None:
    _write_fake_dataset(tmp_path, "syn-old")
    time.sleep(0.01)
    _write_fake_dataset(tmp_path, "syn-new")

    plan = plan_prune(tmp_path, keep_last=1)
    apply_prune(tmp_path, plan)

    assert not (tmp_path / "syn-old").exists()
    assert (tmp_path / "syn-new").exists()
