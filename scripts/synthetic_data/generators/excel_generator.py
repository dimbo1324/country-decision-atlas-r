from __future__ import annotations

from openpyxl import Workbook
from pathlib import Path
from scripts.synthetic_data.core.models import FileFormat
from scripts.synthetic_data.core.random_content import RandomContentFactory
from scripts.synthetic_data.generators.base import BaseGenerator
from typing import Any


class ExcelGenerator(BaseGenerator):
    file_format = FileFormat.EXCEL
    extension = "xlsx"

    def _write(self, path: Path, content: RandomContentFactory) -> None:
        workbook = Workbook()

        first_sheet = workbook.active
        first_sheet.title = content.title(word_count=2)
        self._fill_sheet(first_sheet, content)

        second_sheet = workbook.create_sheet(title=content.title(word_count=2))
        self._fill_sheet(second_sheet, content)

        workbook.save(path)

    @staticmethod
    def _fill_sheet(sheet: Any, content: RandomContentFactory) -> None:
        table = content.table(row_count=10, column_count=5)
        sheet.append(table.headers)
        for row in table.rows:
            sheet.append(row)
