from __future__ import annotations

import random
from pathlib import Path
from scripts.synthetic_data.core.models import FileFormat
from scripts.synthetic_data.core.random_content import (
    random_paragraphs,
    random_table,
    random_title,
)
from scripts.synthetic_data.generators.base import BaseGenerator


class MarkdownGenerator(BaseGenerator):
    file_format = FileFormat.MARKDOWN
    extension = "md"

    def _write(self, path: Path, rng: random.Random) -> None:
        title = random_title(rng)
        paragraphs = random_paragraphs(rng, count=rng.randint(2, 4))
        table = random_table(rng, row_count=5, column_count=3)

        lines = [f"# {title}", ""]
        for paragraph in paragraphs:
            lines.extend([paragraph, ""])

        lines.append(f"## {random_title(rng, word_count=2)}")
        lines.append("")
        lines.append("| " + " | ".join(table.headers) + " |")
        lines.append("| " + " | ".join(["---"] * len(table.headers)) + " |")
        for row in table.rows:
            lines.append("| " + " | ".join(row) + " |")
        lines.append("")

        path.write_text("\n".join(lines), encoding="utf-8")
