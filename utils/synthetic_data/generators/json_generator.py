from __future__ import annotations

import json
from pathlib import Path
from utils.synthetic_data.core.models import FileFormat
from utils.synthetic_data.core.random_content import RandomContentFactory
from utils.synthetic_data.generators.base import BaseGenerator


class JsonGenerator(BaseGenerator):
    file_format = FileFormat.JSON
    extension = "json"

    def _write(self, path: Path, content: RandomContentFactory) -> None:
        document = content.json_document(depth=3, field_count=6)
        path.write_text(
            json.dumps(document, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
