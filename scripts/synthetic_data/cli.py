from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.synthetic_data.core.input_data import (  # noqa: E402
    InputDataError,
    load_input_data,
)
from scripts.synthetic_data.core.models import FileFormat  # noqa: E402
from scripts.synthetic_data.core.output_layout import (  # noqa: E402
    resolve_output_dir,
)
from scripts.synthetic_data.core.paths import (  # noqa: E402
    DEFAULT_INPUT_DATA_FILE,
    DEFAULT_OUTPUT_DATA_ROOT,
)
from scripts.synthetic_data.core.random_content import (  # noqa: E402
    RandomContentFactory,
)
from scripts.synthetic_data.core.registry import get_generator  # noqa: E402


_ALL_FORMATS_ALIAS = "all"


def _parse_formats(raw: str) -> list[FileFormat]:
    formats: list[FileFormat] = []
    for alias in raw.split(","):
        for file_format in FileFormat.from_alias(alias):
            if file_format not in formats:
                formats.append(file_format)
    return formats


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="synthetic-data-generator",
        description=(
            "Generates placeholder PDF/DOCX/XLSX/Markdown/JSON sample files "
            "with random content unrelated to the project domain."
        ),
    )
    parser.add_argument(
        "--formats",
        default=_ALL_FORMATS_ALIAS,
        help=(
            "Comma-separated formats: json, markdown, xlsx, "
            "docx-copyable, docx-non-copyable, docx-mixed, docx (all 3), "
            "pdf-copyable, pdf-non-copyable, pdf-mixed, pdf (all 3), "
            "all (default)."
        ),
    )
    parser.add_argument(
        "--count",
        type=int,
        default=1,
        help="How many sample files to generate per format (default: 1).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help=(
            "Random seed for reproducible content (default: nondeterministic)."
        ),
    )
    parser.add_argument(
        "--input-file",
        type=Path,
        default=DEFAULT_INPUT_DATA_FILE,
        help=(
            "JSON file supplying the word/header pools used to fill "
            "generated documents (default: "
            "docs/synthetic_data/input_data/data.json)."
        ),
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_DATA_ROOT,
        help=(
            "Root directory for generated files "
            "(default: docs/synthetic_data/output_data)."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be generated without writing any files.",
    )
    return parser


def run(argv: list[str]) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    try:
        formats = _parse_formats(args.formats)
    except ValueError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    if args.count < 1:
        print("ERROR: --count must be at least 1", file=sys.stderr)
        return 2

    try:
        input_data = load_input_data(args.input_file)
    except InputDataError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    content = RandomContentFactory(
        rng=random.Random(args.seed), input_data=input_data
    )

    for file_format in formats:
        output_dir = resolve_output_dir(
            file_format, root=args.output_root, create=not args.dry_run
        )
        for _ in range(args.count):
            if args.dry_run:
                print(
                    f"[dry-run] would generate {file_format.value} "
                    f"-> {output_dir}"
                )
                continue
            generator = get_generator(file_format)
            artifact = generator.generate(
                output_dir=output_dir, content=content
            )
            print(
                f"generated {artifact.file_format.value} -> "
                f"{artifact.path} ({artifact.size_bytes} bytes)"
            )

    return 0


def main(argv: list[str] | None = None) -> int:
    return run(sys.argv[1:] if argv is None else argv)


if __name__ == "__main__":
    raise SystemExit(main())
