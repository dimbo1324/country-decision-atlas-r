from __future__ import annotations

from pathlib import Path
from scripts.synthetic_data.core.models import FileFormat
from scripts.synthetic_data.core.random_content import RandomContentFactory
from scripts.synthetic_data.core.registry import (
    GENERATOR_REGISTRY,
    get_generator,
)


def test_registry_covers_every_file_format() -> None:
    assert set(GENERATOR_REGISTRY.keys()) == set(FileFormat)


def test_get_generator_round_trip_generates_file(
    tmp_path: Path, content: RandomContentFactory
) -> None:
    for file_format in FileFormat:
        generator = get_generator(file_format)
        artifact = generator.generate(output_dir=tmp_path, content=content)
        assert artifact.path.exists()
        assert artifact.file_format is file_format
