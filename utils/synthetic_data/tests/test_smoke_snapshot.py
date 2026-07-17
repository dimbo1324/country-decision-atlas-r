"""Structural regression guard for the committed smoke-world fixture
(spec section 23, Этап 7: "маленький фиксированный smoke-набор для
быстрых тестов"). Unlike test_world_generator.py's
`test_balanced_profile_world_is_unchanged_across_this_change` (which only
compares two in-memory generations against each other within the same
test run), this compares against a fixture committed to git — so a
generator change made today is caught even if nobody happened to also
change this test in the same commit.

If this test fails after a deliberate, reviewed generator change: inspect
the diff, confirm it's intentional, then regenerate the fixture with the
same options used below (WorldGenerator(...).generate(...).to_dict(),
written with json.dump(..., indent=2, ensure_ascii=False, sort_keys=True))
and commit the updated fixture in the same change."""

from __future__ import annotations

import json
from pathlib import Path
from utils.synthetic_data.core.world_generator import (
    WorldGenerationOptions,
    WorldGenerator,
)
from utils.synthetic_data.core.world_input import load_world_input


_FIXTURE_PATH = (
    Path(__file__).resolve().parent / "fixtures" / "smoke_world_snapshot.json"
)


def test_smoke_world_snapshot_is_unchanged() -> None:
    world = WorldGenerator(input_data=load_world_input()).generate(
        WorldGenerationOptions(
            seed=42017,
            profile="balanced",
            generated_on="2026-01-01",
        )
    )
    expected = json.loads(_FIXTURE_PATH.read_text(encoding="utf-8"))

    assert world.to_dict() == expected
