from __future__ import annotations

from pathlib import Path
from utils.synthetic_data.core.models import FileFormat
from utils.synthetic_data.core.random_content import RandomContentFactory
from utils.synthetic_data.generators.base import BaseGenerator


class MarkdownGenerator(BaseGenerator):
    file_format = FileFormat.MARKDOWN
    extension = "md"

    def _write(self, path: Path, content: RandomContentFactory) -> None:
        title = content.title()
        paragraphs = content.paragraphs(count=content.randint(2, 4))
        table = content.table(row_count=5, column_count=3)

        lines = [f"# {title}", ""]
        for paragraph in paragraphs:
            lines.extend([paragraph, ""])

        lines.append(f"## {content.title(word_count=2)}")
        lines.append("")
        lines.append("| " + " | ".join(table.headers) + " |")
        lines.append("| " + " | ".join(["---"] * len(table.headers)) + " |")
        for row in table.rows:
            lines.append("| " + " | ".join(row) + " |")
        lines.append("")

        path.write_text("\n".join(lines), encoding="utf-8")
