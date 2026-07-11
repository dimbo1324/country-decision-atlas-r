from __future__ import annotations

import argparse
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[3]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.synthetic_data.core.dataset_discovery import (  # noqa: E402
    available_dataset_ids,
    find_dataset_dir,
)
from scripts.synthetic_data.core.paths import (  # noqa: E402
    DEFAULT_OUTPUT_DATA_ROOT,
)
from scripts.synthetic_data.core.world_models import (  # noqa: E402
    SyntheticWorld,
)
from scripts.synthetic_data.mock_server.app import (  # noqa: E402
    DEFAULT_CORS_ORIGINS,
    create_app,
)


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="synthetic-data-mock-server",
        description=(
            "Serves an already-generated synthetic dataset over HTTP, "
            "mimicking apps/api's public read endpoints closely enough "
            "for apps/web to run against it instead of a real database."
        ),
    )
    parser.add_argument(
        "--dataset",
        required=True,
        help="dataset_id to serve (see `cli.py list`).",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=DEFAULT_OUTPUT_DATA_ROOT,
        help="Root directory the dataset was generated under.",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument(
        "--cors-origin",
        action="append",
        dest="cors_origins",
        default=None,
        help=(
            "Allowed CORS origin (repeatable); default: "
            f"{', '.join(DEFAULT_CORS_ORIGINS)}"
        ),
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_arg_parser().parse_args(
        sys.argv[1:] if argv is None else argv
    )

    dataset_dir = find_dataset_dir(args.dataset, primary_root=args.output_root)
    if dataset_dir is None:
        known = available_dataset_ids(
            args.output_root, DEFAULT_OUTPUT_DATA_ROOT
        )
        suffix = f"; known dataset ids: {', '.join(known)}" if known else ""
        print(
            f"ERROR: dataset {args.dataset!r} not found under "
            f"{args.output_root} (also checked "
            f"{DEFAULT_OUTPUT_DATA_ROOT}){suffix}",
            file=sys.stderr,
        )
        return 2

    canonical_path = dataset_dir / "canonical" / "synthetic_world.json"
    world = SyntheticWorld.model_validate_json(
        canonical_path.read_text(encoding="utf-8")
    )

    import uvicorn

    cors_origins = tuple(args.cors_origins or DEFAULT_CORS_ORIGINS)
    app = create_app(world, cors_origins=cors_origins)
    print(
        f"serving dataset {world.metadata.dataset_id} "
        f"({len(world.countries)} countries) at "
        f"http://{args.host}:{args.port} -- SYNTHETIC TEST DATA, NOT REAL"
    )
    uvicorn.run(app, host=args.host, port=args.port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
