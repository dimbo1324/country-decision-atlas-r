from __future__ import annotations

import json
import random
from pathlib import Path
from scripts.synthetic_data.core.models import FileFormat
from scripts.synthetic_data.core.random_content import random_json_document
from scripts.synthetic_data.generators.base import BaseGenerator


class JsonGenerator(BaseGenerator):
    file_format = FileFormat.JSON
    extension = "json"

    def _write(self, path: Path, rng: random.Random) -> None:
        document = random_json_document(rng, depth=3, field_count=6)
        path.write_text(
            json.dumps(document, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
