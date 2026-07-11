from __future__ import annotations

import argparse
import json
import os
import random
import secrets
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.synthetic_data.core.dataset_packager import (  # noqa: E402
    ALL_DOCUMENT_FORMATS,
    package_dataset,
    render_dataset_documents,
)
from scripts.synthetic_data.core.input_data import (  # noqa: E402
    InputDataError,
    load_input_data,
)
from scripts.synthetic_data.core.locale_corpus import (  # noqa: E402
    LocaleCorpusError,
    load_locale_corpus,
)
from scripts.synthetic_data.core.models import FileFormat  # noqa: E402
from scripts.synthetic_data.core.output_layout import (  # noqa: E402
    resolve_output_dir,
)
from scripts.synthetic_data.core.paths import (  # noqa: E402
    DEFAULT_INPUT_DATA_FILE,
    DEFAULT_OUTPUT_DATA_ROOT,
    DEFAULT_WORLD_INPUT_FILE,
)
from scripts.synthetic_data.core.random_content import (  # noqa: E402
    RandomContentFactory,
)
from scripts.synthetic_data.core.sql_loader import (  # noqa: E402
    SqlLoaderError,
    execute_sql_file,
)
from scripts.synthetic_data.core.world_generator import (  # noqa: E402
    WorldGenerationOptions,
    WorldGenerator,
)
from scripts.synthetic_data.core.world_input import (  # noqa: E402
    WorldInputError,
    load_world_input,
)
from scripts.synthetic_data.core.world_models import (  # noqa: E402
    SyntheticWorld,
)
from scripts.synthetic_data.core.world_validation import (  # noqa: E402
    WorldValidationError,
    validate_world,
)


_ALL_FORMATS_ALIAS = "all"
_WORLD_COMMANDS = frozenset(
    {"validate", "plan", "generate", "render", "load-sql", "cleanup-sql"}
)


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


def build_world_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="synthetic-data-generator",
        description="Builds a deterministic fictional country world for local testing.",
    )
    parser.add_argument("command", choices=sorted(_WORLD_COMMANDS))
    parser.add_argument(
        "--world-input",
        type=Path,
        default=DEFAULT_WORLD_INPUT_FILE,
        help="World JSON configuration (default: docs/synthetic_data/input_data/world_config.json).",
    )
    parser.add_argument(
        "--profile",
        default="balanced",
        help="World profile declared in the input configuration (default: balanced).",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Seed for reproducible world data; a seed is generated when omitted.",
    )
    parser.add_argument(
        "--countries",
        type=int,
        default=None,
        help="Override the configuration country count; only 4 or 5 are allowed.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_DATA_ROOT,
        help="Root directory for generated datasets.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Build and validate the world without writing output files.",
    )
    parser.add_argument(
        "--formats",
        default=_ALL_FORMATS_ALIAS,
        help=(
            "Comma-separated document formats to render: json, txt, xlsx, "
            "docx, pdf, all (default). Only used by generate/render."
        ),
    )
    parser.add_argument(
        "--dataset",
        default=None,
        help=(
            "Existing dataset_id to re-render documents for (render), or "
            "load/cleanup SQL for (load-sql/cleanup-sql)."
        ),
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help=(
            "Required explicit confirmation for load-sql/cleanup-sql — "
            "these connect to a real database."
        ),
    )
    parser.add_argument(
        "--database-url",
        default=None,
        help=(
            "Postgres connection string for load-sql/cleanup-sql "
            "(default: the DATABASE_URL environment variable)."
        ),
    )
    return parser


def _run_legacy(argv: list[str]) -> int:
    from scripts.synthetic_data.core.registry import get_generator

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


def _resolve_seed(seed: int | None) -> int:
    return secrets.randbelow(2**63) if seed is None else seed


def _parse_document_formats(raw: str) -> tuple[str, ...]:
    normalized = raw.strip().lower()
    if normalized == _ALL_FORMATS_ALIAS:
        return ALL_DOCUMENT_FORMATS
    formats: list[str] = []
    for alias in normalized.split(","):
        alias = alias.strip()
        if alias not in ALL_DOCUMENT_FORMATS:
            raise ValueError(f"Unknown document format alias: {alias!r}")
        if alias not in formats:
            formats.append(alias)
    return tuple(formats)


def _write_world_dataset(*, world: SyntheticWorld, output_root: Path) -> Path:
    dataset_dir = output_root / world.metadata.dataset_id
    canonical_dir = dataset_dir / "canonical"
    canonical_dir.mkdir(parents=True, exist_ok=True)
    payload = world.to_dict()
    (canonical_dir / "synthetic_world.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True)
        + "\n",
        encoding="utf-8",
    )
    return dataset_dir


def _render_and_package(
    *,
    world: SyntheticWorld,
    world_errors: tuple[str, ...],
    dataset_dir: Path,
    formats: tuple[str, ...],
) -> None:
    locale_corpus = load_locale_corpus()
    documents = render_dataset_documents(
        world=world,
        locale_corpus=locale_corpus,
        dataset_dir=dataset_dir,
        formats=formats,
    )
    result = package_dataset(
        world=world,
        world_errors=world_errors,
        dataset_dir=dataset_dir,
        documents=documents,
    )
    print(
        f"rendered {len(documents)} documents -> manifest="
        f"{result.manifest_path} zip={result.zip_path}"
    )
    if result.artifact_errors:
        print(
            f"WARNING: {len(result.artifact_errors)} artifact validation "
            "issues; see validation_report.json",
            file=sys.stderr,
        )


def _run_render(args: argparse.Namespace) -> int:
    if not args.dataset:
        print("ERROR: render requires --dataset <dataset_id>", file=sys.stderr)
        return 2
    dataset_dir = args.output_root / args.dataset
    canonical_path = dataset_dir / "canonical" / "synthetic_world.json"
    if not canonical_path.exists():
        print(
            f"ERROR: no canonical world found at {canonical_path}",
            file=sys.stderr,
        )
        return 2
    try:
        formats = _parse_document_formats(args.formats)
    except ValueError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    try:
        world = SyntheticWorld.model_validate_json(
            canonical_path.read_text(encoding="utf-8")
        )
        errors = validate_world(world)
        if args.dry_run:
            print(
                f"[dry-run] would re-render {dataset_dir} "
                f"formats={','.join(formats)}"
            )
            return 0
        _render_and_package(
            world=world,
            world_errors=errors,
            dataset_dir=dataset_dir,
            formats=formats,
        )
        return 0
    except (ValueError, WorldValidationError, LocaleCorpusError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


def _run_sql_command(args: argparse.Namespace) -> int:
    if not args.dataset:
        print(
            f"ERROR: {args.command} requires --dataset <dataset_id>",
            file=sys.stderr,
        )
        return 2
    if not args.confirm:
        print(
            f"ERROR: {args.command} requires --confirm — it connects to a "
            "real database and modifies rows.",
            file=sys.stderr,
        )
        return 2
    database_url = args.database_url or os.environ.get("DATABASE_URL")
    if not database_url:
        print(
            "ERROR: no database URL given (--database-url or DATABASE_URL "
            "environment variable)",
            file=sys.stderr,
        )
        return 2

    dataset_dir = args.output_root / args.dataset
    sql_filename = (
        "seed_synthetic_world.sql"
        if args.command == "load-sql"
        else "cleanup_synthetic_world.sql"
    )
    sql_path = dataset_dir / "sql" / sql_filename
    try:
        execute_sql_file(sql_path, database_url=database_url)
    except SqlLoaderError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    print(
        f"{args.command}: applied {sql_path} to {database_url.split('@')[-1]}"
    )
    return 0


def _run_world(argv: list[str]) -> int:
    parser = build_world_arg_parser()
    args = parser.parse_args(argv)
    if args.command == "render":
        return _run_render(args)
    if args.command in ("load-sql", "cleanup-sql"):
        return _run_sql_command(args)
    try:
        input_data = load_world_input(args.world_input)
        if args.command == "validate":
            print(
                "valid world input "
                f"schema={input_data.schema_version} "
                f"profiles={','.join(profile.slug for profile in input_data.profiles)}"
            )
            return 0

        seed = _resolve_seed(args.seed)
        world = WorldGenerator(input_data=input_data).generate(
            WorldGenerationOptions(
                seed=seed,
                profile=args.profile,
                country_count=args.countries,
            )
        )
        errors = validate_world(
            world,
            forbidden_country_names=input_data.forbidden_country_names,
        )
        if errors:
            raise WorldValidationError("; ".join(errors))
        print(
            f"dataset_id={world.metadata.dataset_id} seed={seed} "
            f"profile={world.metadata.profile} countries={len(world.countries)} "
            f"users={len(world.users)} authors={len(world.authors)} "
            f"articles={len(world.articles)} comments={len(world.comments)} "
            f"legal_signals={len(world.legal_signals)} "
            f"document_recipes={len(world.document_recipes)} "
            f"scenarios={len(world.scenarios)}"
        )
        if args.command == "plan" or args.dry_run:
            for country in world.countries:
                print(f"- {country.name} ({country.code}): {country.archetype}")
            for scenario in world.scenarios:
                print(f"  scenario: {scenario.title} ({scenario.category})")
            return 0

        dataset_dir = _write_world_dataset(
            world=world, output_root=args.output_root
        )
        print(f"generated canonical world -> {dataset_dir}")
        formats = _parse_document_formats(args.formats)
        _render_and_package(
            world=world,
            world_errors=errors,
            dataset_dir=dataset_dir,
            formats=formats,
        )
        return 0
    except (
        ValueError,
        WorldInputError,
        WorldValidationError,
        LocaleCorpusError,
    ) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


def run(argv: list[str]) -> int:
    if argv and argv[0] in _WORLD_COMMANDS:
        return _run_world(argv)
    return _run_legacy(argv)


def main(argv: list[str] | None = None) -> int:
    return run(sys.argv[1:] if argv is None else argv)


if __name__ == "__main__":
    raise SystemExit(main())
