from __future__ import annotations

import pytest
from utils.synthetic_data.core.models import FileFormat


def test_from_alias_all_returns_every_format() -> None:
    assert FileFormat.from_alias("all") == tuple(FileFormat)


def test_from_alias_docx_returns_all_three_docx_variants() -> None:
    assert FileFormat.from_alias("docx") == (
        FileFormat.DOCX_COPYABLE,
        FileFormat.DOCX_NON_COPYABLE,
        FileFormat.DOCX_MIXED,
    )


def test_from_alias_pdf_returns_all_three_pdf_variants() -> None:
    assert FileFormat.from_alias("pdf") == (
        FileFormat.PDF_COPYABLE,
        FileFormat.PDF_NON_COPYABLE,
        FileFormat.PDF_MIXED,
    )


def test_from_alias_exact_value() -> None:
    assert FileFormat.from_alias("json") == (FileFormat.JSON,)
    assert FileFormat.from_alias("docx-mixed") == (FileFormat.DOCX_MIXED,)


def test_from_alias_unknown_raises() -> None:
    with pytest.raises(ValueError):
        FileFormat.from_alias("not-a-format")
