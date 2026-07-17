from __future__ import annotations

import hashlib
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


def write_archive_checksum(archive_path: Path) -> Path:
    """Sidecar sha256 of the finished ZIP, in the standard `sha256sum`
    `<hex>  <filename>` format, next to the archive itself — so a copy
    moved between machines or CI runners can be verified (`sha256sum -c
    <name>.zip.sha256`) without extracting it first."""
    digest = hashlib.sha256()
    digest.update(archive_path.read_bytes())
    checksum_path = archive_path.with_name(archive_path.name + ".sha256")
    checksum_path.write_text(
        f"{digest.hexdigest()}  {archive_path.name}\n", encoding="utf-8"
    )
    return checksum_path
