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

from scripts.synthetic_data.core.dataset_diff import (  # noqa: E402
    diff_worlds,
)
from scripts.synthetic_data.core.dataset_discovery import (  # noqa: E402
    available_dataset_ids,
    find_dataset_dir,
    list_datasets,
)
from scripts.synthetic_data.core.dataset_prune import (  # noqa: E402
    apply_prune,
    plan_prune,
)
from scripts.synthetic_data.core.document_formats import (  # noqa: E402
    ALL_DOCUMENT_FORMATS,
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
    ensure_not_production,
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
    {
        "validate",
        "plan",
        "generate",
        "render",
        "load-sql",
        "cleanup-sql",
        "list",
        "package",
        "prune",
        "schema",
        "diff",
    }
)
# `dataset_packager` transitively imports reportlab/python-docx/openpyxl —
# it is only imported (lazily, inside the relevant command functions) by
# generate/render/package, so validate/plan/list/prune/schema stay usable
# without those libraries installed (spec section 12).


class _Report:
    """Collects a command's output as both human-readable lines and a
    structured dict, then emits exactly one of the two depending on
    `--json`/`--quiet` — every command builds its result the same way
    instead of sprinkling `print()` calls conditionally."""

    def __init__(self, args: argparse.Namespace) -> None:
        self._json = getattr(args, "json", False)
        self._quiet = getattr(args, "quiet", False)
        self.lines: list[str] = []
        self.data: dict[str, object] = {}

    def line(self, text: str) -> None:
        self.lines.append(text)

    def emit(self) -> None:
        if self._json:
            print(json.dumps(self.data, ensure_ascii=False, sort_keys=True))
        elif not self._quiet:
            for text in self.lines:
                print(text)


def _parse_formats(raw: str) -> list[FileFormat]:
    formats: list[FileFormat] = []
    for alias in raw.split(","):
        for file_format in FileFormat.from_alias(alias):
            if file_format not in formats:
                formats.append(file_format)
    return formats


def _add_output_flags(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print one structured JSON object instead of human text.",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress routine output (errors still go to stderr).",
    )


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
        help=(
            "Build and validate without writing files (generate/render), "
            "or preview without connecting/deleting (load-sql/cleanup-sql/"
            "prune)."
        ),
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
            "Existing dataset_id to re-render (render), load/cleanup SQL "
            "for (load-sql/cleanup-sql), or repackage (package)."
        ),
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        help=(
            "Required explicit confirmation for load-sql/cleanup-sql "
            "(connects to a real database) and prune (deletes directories)."
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
    parser.add_argument(
        "--keep-last",
        type=int,
        default=None,
        help="Number of newest datasets to keep; required by prune.",
    )
    parser.add_argument(
        "--dataset-a",
        default=None,
        help="First dataset_id to compare; required by diff.",
    )
    parser.add_argument(
        "--dataset-b",
        default=None,
        help="Second dataset_id to compare; required by diff.",
    )
    _add_output_flags(parser)
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


def _resolve_dataset_dir(args: argparse.Namespace) -> Path | None:
    if not args.dataset:
        return None
    return find_dataset_dir(args.dataset, primary_root=args.output_root)


def _dataset_not_found_error(args: argparse.Namespace) -> str:
    known = available_dataset_ids(args.output_root, DEFAULT_OUTPUT_DATA_ROOT)
    suffix = f"; known dataset ids: {', '.join(known)}" if known else ""
    return (
        f"dataset {args.dataset!r} not found under {args.output_root} "
        f"(also checked {DEFAULT_OUTPUT_DATA_ROOT}){suffix}"
    )


def _resolve_named_dataset_dir(
    dataset_id: str, args: argparse.Namespace
) -> Path | None:
    return find_dataset_dir(dataset_id, primary_root=args.output_root)


def _named_dataset_not_found_error(
    dataset_id: str, args: argparse.Namespace
) -> str:
    known = available_dataset_ids(args.output_root, DEFAULT_OUTPUT_DATA_ROOT)
    suffix = f"; known dataset ids: {', '.join(known)}" if known else ""
    return (
        f"dataset {dataset_id!r} not found under {args.output_root} "
        f"(also checked {DEFAULT_OUTPUT_DATA_ROOT}){suffix}"
    )


def _load_world(dataset_dir: Path) -> SyntheticWorld:
    canonical_path = dataset_dir / "canonical" / "synthetic_world.json"
    return SyntheticWorld.model_validate_json(
        canonical_path.read_text(encoding="utf-8")
    )


def _render_and_package(
    *,
    world: SyntheticWorld,
    world_errors: tuple[str, ...],
    dataset_dir: Path,
    formats: tuple[str, ...],
    report: _Report,
) -> None:
    from scripts.synthetic_data.core.dataset_packager import (
        package_dataset,
        render_dataset_documents,
    )

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
    report.line(
        f"rendered {len(documents)} documents -> manifest="
        f"{result.manifest_path} zip={result.zip_path} "
        f"(sha256 in {result.package_checksum_path.name}) "
        f"dashboard={result.dashboard_path}"
    )
    report.data["documents_rendered"] = len(documents)
    report.data["manifest_path"] = str(result.manifest_path)
    report.data["manifest_checksum_path"] = str(result.manifest_checksum_path)
    report.data["dashboard_path"] = str(result.dashboard_path)
    report.data["zip_path"] = str(result.zip_path)
    report.data["package_checksum_path"] = str(result.package_checksum_path)
    report.data["artifact_errors"] = list(result.artifact_errors)
    if result.artifact_errors:
        print(
            f"WARNING: {len(result.artifact_errors)} artifact validation "
            "issues; see validation_report.json",
            file=sys.stderr,
        )


def _run_render(args: argparse.Namespace, report: _Report) -> int:
    if not args.dataset:
        print("ERROR: render requires --dataset <dataset_id>", file=sys.stderr)
        return 2
    dataset_dir = _resolve_dataset_dir(args)
    if dataset_dir is None:
        print(f"ERROR: {_dataset_not_found_error(args)}", file=sys.stderr)
        return 2
    canonical_path = dataset_dir / "canonical" / "synthetic_world.json"
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
            report.line(
                f"[dry-run] would re-render {dataset_dir} "
                f"formats={','.join(formats)}"
            )
            report.data.update(
                {
                    "dry_run": True,
                    "dataset_dir": str(dataset_dir),
                    "formats": list(formats),
                }
            )
            report.emit()
            return 0
        _render_and_package(
            world=world,
            world_errors=errors,
            dataset_dir=dataset_dir,
            formats=formats,
            report=report,
        )
        report.data["dataset_id"] = world.metadata.dataset_id
        report.emit()
        return 0
    except (ValueError, WorldValidationError, LocaleCorpusError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


def _run_package(args: argparse.Namespace, report: _Report) -> int:
    if not args.dataset:
        print("ERROR: package requires --dataset <dataset_id>", file=sys.stderr)
        return 2
    dataset_dir = _resolve_dataset_dir(args)
    if dataset_dir is None:
        print(f"ERROR: {_dataset_not_found_error(args)}", file=sys.stderr)
        return 2
    canonical_path = dataset_dir / "canonical" / "synthetic_world.json"
    try:
        world = SyntheticWorld.model_validate_json(
            canonical_path.read_text(encoding="utf-8")
        )
    except ValueError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    errors = validate_world(world)
    if args.dry_run:
        report.line(f"[dry-run] would repackage {dataset_dir}")
        report.data.update({"dry_run": True, "dataset_dir": str(dataset_dir)})
        report.emit()
        return 0

    from scripts.synthetic_data.core.dataset_packager import (
        discover_existing_documents,
        package_dataset,
    )

    documents = discover_existing_documents(
        world=world, dataset_dir=dataset_dir
    )
    result = package_dataset(
        world=world,
        world_errors=errors,
        dataset_dir=dataset_dir,
        documents=documents,
    )
    report.line(
        f"repackaged {len(documents)} existing documents -> manifest="
        f"{result.manifest_path} zip={result.zip_path} "
        f"(sha256 in {result.package_checksum_path.name}) "
        f"dashboard={result.dashboard_path}"
    )
    report.data.update(
        {
            "dataset_id": world.metadata.dataset_id,
            "documents_found": len(documents),
            "manifest_path": str(result.manifest_path),
            "manifest_checksum_path": str(result.manifest_checksum_path),
            "dashboard_path": str(result.dashboard_path),
            "zip_path": str(result.zip_path),
            "package_checksum_path": str(result.package_checksum_path),
            "artifact_errors": list(result.artifact_errors),
        }
    )
    report.emit()
    return 0


def _run_list(args: argparse.Namespace, report: _Report) -> int:
    datasets = list_datasets(args.output_root)
    report.data["datasets"] = [
        {
            "dataset_id": summary.dataset_id,
            "seed": summary.seed,
            "profile": summary.profile,
            "generated_on": summary.generated_on,
            "country_count": summary.country_count,
            "size_bytes": summary.size_bytes,
            "path": str(summary.path),
        }
        for summary in datasets
    ]
    if not datasets:
        report.line(f"no datasets found under {args.output_root}")
    for summary in datasets:
        size_mb = summary.size_bytes / (1024 * 1024)
        report.line(
            f"{summary.dataset_id}  seed={summary.seed} "
            f"profile={summary.profile} generated_on={summary.generated_on} "
            f"countries={summary.country_count} size={size_mb:.1f}MB"
        )
    report.emit()
    return 0


def _run_prune(args: argparse.Namespace, report: _Report) -> int:
    if args.keep_last is None:
        print("ERROR: prune requires --keep-last N", file=sys.stderr)
        return 2
    try:
        plan = plan_prune(args.output_root, keep_last=args.keep_last)
    except ValueError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    report.data["kept"] = list(plan.kept)
    report.data["removed"] = list(plan.removed)
    if args.dry_run:
        report.line(
            f"[dry-run] would keep {len(plan.kept)}, "
            f"remove {len(plan.removed)}: {', '.join(plan.removed) or '(none)'}"
        )
        report.data["dry_run"] = True
        report.emit()
        return 0
    if plan.removed and not args.confirm:
        print(
            "ERROR: prune requires --confirm to actually delete "
            f"{len(plan.removed)} dataset(s); use --dry-run to preview",
            file=sys.stderr,
        )
        return 2

    apply_prune(args.output_root, plan)
    report.line(
        f"kept {len(plan.kept)}, removed {len(plan.removed)}: "
        f"{', '.join(plan.removed) or '(none)'}"
    )
    report.emit()
    return 0


def _run_diff(args: argparse.Namespace, report: _Report) -> int:
    if not args.dataset_a or not args.dataset_b:
        print(
            "ERROR: diff requires --dataset-a <id> and --dataset-b <id>",
            file=sys.stderr,
        )
        return 2
    dataset_dir_a = _resolve_named_dataset_dir(args.dataset_a, args)
    if dataset_dir_a is None:
        print(
            f"ERROR: {_named_dataset_not_found_error(args.dataset_a, args)}",
            file=sys.stderr,
        )
        return 2
    dataset_dir_b = _resolve_named_dataset_dir(args.dataset_b, args)
    if dataset_dir_b is None:
        print(
            f"ERROR: {_named_dataset_not_found_error(args.dataset_b, args)}",
            file=sys.stderr,
        )
        return 2

    try:
        world_a = _load_world(dataset_dir_a)
        world_b = _load_world(dataset_dir_b)
    except (OSError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    diff = diff_worlds(world_a, world_b)

    if diff.is_identical:
        report.line(
            f"{diff.dataset_id_a} and {diff.dataset_id_b} are equivalent: "
            "same countries, metrics, and scenario mix."
        )
    else:
        report.line(
            f"comparing {diff.dataset_id_a} (a) vs {diff.dataset_id_b} (b)"
        )
        for slug in diff.countries_added:
            report.line(f"  + country only in b: {slug}")
        for slug in diff.countries_removed:
            report.line(f"  - country only in a: {slug}")
        for country_diff in diff.countries_changed:
            report.line(
                f"  ~ {country_diff.slug}: archetype "
                f"{country_diff.archetype_a} -> {country_diff.archetype_b}"
                if country_diff.archetype_a != country_diff.archetype_b
                else f"  ~ {country_diff.slug}:"
            )
            for metric_change in country_diff.metric_changes:
                report.line(
                    f"      {metric_change.metric}: "
                    f"{metric_change.value_a} -> {metric_change.value_b}"
                )
        for category_diff in diff.scenario_category_diffs:
            report.line(
                f"  scenarios[{category_diff.category}]: "
                f"{category_diff.count_a} -> {category_diff.count_b}"
            )

    report.data.update(
        {
            "dataset_id_a": diff.dataset_id_a,
            "dataset_id_b": diff.dataset_id_b,
            "profile_a": diff.profile_a,
            "profile_b": diff.profile_b,
            "seed_a": diff.seed_a,
            "seed_b": diff.seed_b,
            "is_identical": diff.is_identical,
            "countries_added": list(diff.countries_added),
            "countries_removed": list(diff.countries_removed),
            "countries_changed": [
                {
                    "slug": country_diff.slug,
                    "name_a": country_diff.name_a,
                    "name_b": country_diff.name_b,
                    "archetype_a": country_diff.archetype_a,
                    "archetype_b": country_diff.archetype_b,
                    "metric_changes": [
                        {
                            "metric": metric_change.metric,
                            "value_a": metric_change.value_a,
                            "value_b": metric_change.value_b,
                        }
                        for metric_change in country_diff.metric_changes
                    ],
                }
                for country_diff in diff.countries_changed
            ],
            "scenario_count_a": diff.scenario_count_a,
            "scenario_count_b": diff.scenario_count_b,
            "scenario_category_diffs": [
                {
                    "category": category_diff.category,
                    "count_a": category_diff.count_a,
                    "count_b": category_diff.count_b,
                }
                for category_diff in diff.scenario_category_diffs
            ],
        }
    )
    report.emit()
    return 0 if diff.is_identical else 1


def _run_schema() -> int:
    schema = SyntheticWorld.model_json_schema()
    print(json.dumps(schema, indent=2, ensure_ascii=False, sort_keys=True))
    return 0


def _run_sql_command(args: argparse.Namespace, report: _Report) -> int:
    """`load-sql`/`cleanup-sql`. Flag validation and the production guard
    both run before the dataset directory is resolved from disk — a
    misconfigured or forbidden invocation must be rejected the same way
    whether or not the named dataset happens to exist locally, and never
    later than the point where a real connection would be opened."""
    if not args.dataset:
        print(
            f"ERROR: {args.command} requires --dataset <dataset_id>",
            file=sys.stderr,
        )
        return 2
    database_url = args.database_url or os.environ.get("DATABASE_URL")
    if not database_url and not args.dry_run:
        print(
            "ERROR: no database URL given (--database-url or DATABASE_URL "
            "environment variable)",
            file=sys.stderr,
        )
        return 2
    target = (
        database_url.split("@")[-1] if database_url else "(no database url)"
    )
    sql_filename = (
        "seed_synthetic_world.sql"
        if args.command == "load-sql"
        else "cleanup_synthetic_world.sql"
    )

    if args.dry_run:
        try:
            ensure_not_production()
            blocked = False
        except SqlLoaderError as error:
            blocked = True
            report.line(f"[dry-run] would refuse: {error}")
        dataset_dir = _resolve_dataset_dir(args)
        sql_path = (
            dataset_dir / "sql" / sql_filename
            if dataset_dir is not None
            else args.output_root / args.dataset / "sql" / sql_filename
        )
        if not blocked:
            report.line(
                f"[dry-run] would apply {sql_path} to {target} "
                f"(dataset={args.dataset})"
            )
        report.data.update(
            {
                "dry_run": True,
                "dataset_id": args.dataset,
                "sql_path": str(sql_path),
                "target": target,
                "blocked_by_production_guard": blocked,
            }
        )
        report.emit()
        return 2 if blocked else 0

    if not args.confirm:
        print(
            f"ERROR: {args.command} requires --confirm — it connects to a "
            "real database and modifies rows.",
            file=sys.stderr,
        )
        return 2
    try:
        ensure_not_production()
    except SqlLoaderError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    dataset_dir = _resolve_dataset_dir(args)
    if dataset_dir is None:
        print(f"ERROR: {_dataset_not_found_error(args)}", file=sys.stderr)
        return 2
    sql_path = dataset_dir / "sql" / sql_filename
    assert database_url is not None  # guaranteed by the check above
    try:
        execute_sql_file(sql_path, database_url=database_url)
    except SqlLoaderError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2
    report.line(f"{args.command}: applied {sql_path} to {target}")
    report.data.update(
        {
            "dataset_id": args.dataset,
            "sql_path": str(sql_path),
            "target": target,
            "applied": True,
        }
    )
    report.emit()
    return 0


def _run_world(argv: list[str]) -> int:
    parser = build_world_arg_parser()
    args = parser.parse_args(argv)
    report = _Report(args)

    if args.command == "render":
        return _run_render(args, report)
    if args.command == "package":
        return _run_package(args, report)
    if args.command == "list":
        return _run_list(args, report)
    if args.command == "prune":
        return _run_prune(args, report)
    if args.command == "diff":
        return _run_diff(args, report)
    if args.command == "schema":
        return _run_schema()
    if args.command in ("load-sql", "cleanup-sql"):
        return _run_sql_command(args, report)
    try:
        input_data = load_world_input(args.world_input)
        if args.command == "validate":
            report.line(
                "valid world input "
                f"schema={input_data.schema_version} "
                f"profiles={','.join(profile.slug for profile in input_data.profiles)}"
            )
            report.data.update(
                {
                    "status": "valid",
                    "schema_version": input_data.schema_version,
                    "profiles": [
                        profile.slug for profile in input_data.profiles
                    ],
                }
            )
            report.emit()
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
        report.line(
            f"dataset_id={world.metadata.dataset_id} seed={seed} "
            f"profile={world.metadata.profile} countries={len(world.countries)} "
            f"users={len(world.users)} authors={len(world.authors)} "
            f"articles={len(world.articles)} comments={len(world.comments)} "
            f"legal_signals={len(world.legal_signals)} "
            f"document_recipes={len(world.document_recipes)} "
            f"scenarios={len(world.scenarios)}"
        )
        report.data.update(
            {
                "dataset_id": world.metadata.dataset_id,
                "seed": seed,
                "profile": world.metadata.profile,
                "countries": len(world.countries),
                "users": len(world.users),
                "authors": len(world.authors),
                "articles": len(world.articles),
                "comments": len(world.comments),
                "legal_signals": len(world.legal_signals),
                "document_recipes": len(world.document_recipes),
                "scenarios": len(world.scenarios),
            }
        )
        if args.command == "plan" or args.dry_run:
            for country in world.countries:
                report.line(
                    f"- {country.name} ({country.code}): {country.archetype}"
                )
            for scenario in world.scenarios:
                report.line(
                    f"  scenario: {scenario.title} ({scenario.category})"
                )
            report.data["country_list"] = [
                {
                    "name": country.name,
                    "code": country.code,
                    "archetype": country.archetype,
                }
                for country in world.countries
            ]
            report.data["scenario_list"] = [
                {"title": scenario.title, "category": scenario.category}
                for scenario in world.scenarios
            ]
            report.emit()
            return 0

        dataset_dir = _write_world_dataset(
            world=world, output_root=args.output_root
        )
        report.line(f"generated canonical world -> {dataset_dir}")
        report.data["dataset_dir"] = str(dataset_dir)
        formats = _parse_document_formats(args.formats)
        _render_and_package(
            world=world,
            world_errors=errors,
            dataset_dir=dataset_dir,
            formats=formats,
            report=report,
        )
        report.emit()
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
