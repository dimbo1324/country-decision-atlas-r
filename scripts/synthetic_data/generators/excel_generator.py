from __future__ import annotations

import random
from openpyxl import Workbook
from pathlib import Path
from scripts.synthetic_data.core.models import FileFormat
from scripts.synthetic_data.core.random_content import (
    random_table,
    random_title,
)
from scripts.synthetic_data.generators.base import BaseGenerator
from typing import Any


class ExcelGenerator(BaseGenerator):
    file_format = FileFormat.EXCEL
    extension = "xlsx"

    def _write(self, path: Path, rng: random.Random) -> None:
        workbook = Workbook()

        first_sheet = workbook.active
        first_sheet.title = random_title(rng, word_count=2)
        self._fill_sheet(first_sheet, rng)

        second_sheet = workbook.create_sheet(
            title=random_title(rng, word_count=2)
        )
        self._fill_sheet(second_sheet, rng)

        workbook.save(path)

    @staticmethod
    def _fill_sheet(sheet: Any, rng: random.Random) -> None:
        table = random_table(rng, row_count=10, column_count=5)
        sheet.append(table.headers)
        for row in table.rows:
            sheet.append(row)
