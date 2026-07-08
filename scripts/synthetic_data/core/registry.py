from __future__ import annotations

from scripts.synthetic_data.core.models import FileFormat
from scripts.synthetic_data.generators.base import BaseGenerator
from scripts.synthetic_data.generators.docx.copyable import (
    DocxCopyableGenerator,
)
from scripts.synthetic_data.generators.docx.mixed import DocxMixedGenerator
from scripts.synthetic_data.generators.docx.non_copyable import (
    DocxNonCopyableGenerator,
)
from scripts.synthetic_data.generators.excel_generator import ExcelGenerator
from scripts.synthetic_data.generators.json_generator import JsonGenerator
from scripts.synthetic_data.generators.markdown_generator import (
    MarkdownGenerator,
)
from scripts.synthetic_data.generators.pdf.copyable import (
    PdfCopyableGenerator,
)
from scripts.synthetic_data.generators.pdf.mixed import PdfMixedGenerator
from scripts.synthetic_data.generators.pdf.non_copyable import (
    PdfNonCopyableGenerator,
)


GENERATOR_REGISTRY: dict[FileFormat, BaseGenerator] = {
    FileFormat.JSON: JsonGenerator(),
    FileFormat.MARKDOWN: MarkdownGenerator(),
    FileFormat.EXCEL: ExcelGenerator(),
    FileFormat.DOCX_COPYABLE: DocxCopyableGenerator(),
    FileFormat.DOCX_NON_COPYABLE: DocxNonCopyableGenerator(),
    FileFormat.DOCX_MIXED: DocxMixedGenerator(),
    FileFormat.PDF_COPYABLE: PdfCopyableGenerator(),
    FileFormat.PDF_NON_COPYABLE: PdfNonCopyableGenerator(),
    FileFormat.PDF_MIXED: PdfMixedGenerator(),
}


def get_generator(file_format: FileFormat) -> BaseGenerator:
    return GENERATOR_REGISTRY[file_format]
