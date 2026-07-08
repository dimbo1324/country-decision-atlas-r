from __future__ import annotations

import zipfile
from pathlib import Path
from scripts.synthetic_data.archive.zip_archiver import create_zip_archive


def test_create_zip_archive_bundles_given_files(tmp_path: Path) -> None:
    first_file = tmp_path / "a.txt"
    second_file = tmp_path / "b.txt"
    first_file.write_text("alpha", encoding="utf-8")
    second_file.write_text("beta", encoding="utf-8")

    destination = tmp_path / "out" / "archive.zip"
    result = create_zip_archive([first_file, second_file], destination)

    assert result == destination
    with zipfile.ZipFile(destination) as archive:
        assert set(archive.namelist()) == {"a.txt", "b.txt"}


def test_create_zip_archive_uses_relative_posix_arcnames(
    tmp_path: Path,
) -> None:
    nested_dir = tmp_path / "nested"
    nested_dir.mkdir()
    nested_file = nested_dir / "c.txt"
    nested_file.write_text("gamma", encoding="utf-8")

    destination = tmp_path / "archive.zip"
    create_zip_archive([nested_file], destination, arcname_root=tmp_path)

    with zipfile.ZipFile(destination) as archive:
        assert archive.namelist() == ["nested/c.txt"]
