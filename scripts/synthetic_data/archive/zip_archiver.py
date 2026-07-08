from __future__ import annotations

import zipfile
from collections.abc import Sequence
from pathlib import Path


def create_zip_archive(
    paths: Sequence[Path],
    destination: Path,
    *,
    arcname_root: Path | None = None,
) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(
        destination, mode="w", compression=zipfile.ZIP_DEFLATED
    ) as archive:
        for path in paths:
            relative = (
                path.relative_to(arcname_root)
                if arcname_root
                else Path(path.name)
            )
            archive.write(path, arcname=relative.as_posix())
    return destination
