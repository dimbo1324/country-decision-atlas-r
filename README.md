# Country Decision Atlas

A full-stack decision-support platform that helps a person choose a country
for a specific goal — relocation, residency/citizenship, remote work,
low-budget living, business, or safety. Every answer is structured,
sourced, and confidence-rated.

**This is not a country-ranking blog or listicle product.** Scores are
transparent, versioned, and always shown with their sources and
confidence — never a bare "best country" number.

## Tech stack

| Layer | Stack |
| --- | --- |
| Backend API | Python 3.12+, FastAPI, Pydantic v2, PostgreSQL (via `psycopg`), Redis |
| Frontend | Next.js 15, React 19, TypeScript |
| Notifier service | Go, gRPC, Kafka (Redpanda), MongoDB, Telegram |
| Contracts | OpenAPI spec, generated TypeScript + Python client types |
| Package management | `pnpm` 9.12.0 (workspace), Python `pyproject.toml` |

## Repository layout

| Path | What it is |
| --- | --- |
| `apps/api` | FastAPI backend. Routers in `app/api/v1/*`, business logic in `app/services/*`, SQL in `app/repositories/*`. |
| `apps/web` | Next.js frontend — the main user-facing application. |
| `apps/worker` | Python batch worker (e.g. processes queued translation jobs). |
| `apps/notifier` | Go gRPC service: consumes domain events from Kafka and delivers Telegram notifications. |
| `contracts/openapi.yaml` | Source of truth for the API contract. Run `pnpm contracts:generate` to regenerate `packages/contracts/generated` — never hand-edit the generated file. |
| `database/migrations` | Numbered, checksum-tracked SQL migrations. |
| `scripts/synthetic_data.py` + `utils/synthetic_data` | Generates a fully fictional "world" (countries, users, articles, documents, SQL fixtures) for local development and demos without any real data. Includes a local mock HTTP server so the frontend can run against synthetic data with no database at all — see [utils/synthetic_data/README.md](utils/synthetic_data/README.md). |
| `scripts/dev_tools`, `dev_tools_scripts_runner.py` | Developer automation: quality gates, formatting, releases, scheduled jobs. |
| `docs/` | Architecture, API, product, decisions, operations, and research documentation (`docs/README.md` is the index). |
| `.ai/` | Shared rule modules that both Claude Code and Codex read for how work is done in this repo. |

## Prerequisites

- Python 3.12+
- Node.js with `pnpm` 9.12.0 (`corepack enable` will pick up the pinned version)
- Docker Desktop (for Postgres/Redis/the API container)
- Go 1.25+ (only needed if you're touching `apps/notifier`)

## Quick start

```powershell
# 1. Clone and configure
git clone <this-repo>
cd country-decision-atlas-r
copy .env.example .env   # then edit values as needed

# 2. Install dependencies
corepack pnpm@9.12.0 install --frozen-lockfile
python -m pip install -e ".[dev]"

# 3. Start the backing services (Postgres, Redis, API)
docker compose up -d postgres redis api

# 4. Apply database migrations
python scripts/apply_migrations.py

# 5. Make the conserved demo countries (Russia, Uruguay, Argentina) visible
#    -- migrations seed them with is_demo=TRUE (hidden) by design (see
#    "Project status notes" below), so skipping this step leaves the
#    countries list empty even though the data is there. Reads DATABASE_URL
#    from .env (via get_settings()), same as apply_migrations.py.
python scripts/dev_tools/restore_demo_countries.py --visible

# 6. Generate frontend API types from the OpenAPI contract
corepack pnpm@9.12.0 contracts:generate
```

The API is now reachable at `http://localhost:8000` (see `/health` and
`/ready`).

## Frontend development

```powershell
pnpm dev   # starts apps/web on http://localhost:3000
```

`apps/web` reads its backend URL from `NEXT_PUBLIC_API_BASE_URL` (see
`.env.example`, default `http://localhost:8000`).

**Don't want to run Postgres/Redis/the API at all?** Point the frontend at
the synthetic mock server instead:

```powershell
python scripts/synthetic_data.py generate --seed 42017
python -m utils.synthetic_data.mock_server --dataset <dataset_id> --port 8000
```

This serves a fully fictional dataset that mimics the shape of the real
API's read endpoints (countries, trust, CII scores, search, ...) — useful
for frontend work that doesn't need a real backend yet.

## Common commands

```powershell
# Full local quality gate (static checks, all tests, Docker smokes, E2E, pre-commit)
python dev_tools_scripts_runner.py full-check

# Quick gate (minimum before pushing an intermediate change)
python dev_tools_scripts_runner.py full-check --profile quick

# Auto-format Python, frontend, and Go code
python dev_tools_scripts_runner.py format-code

# Read-only diagnostics (no changes)
python dev_tools_scripts_runner.py --doctor
```

Run `python dev_tools_scripts_runner.py` with no arguments for an
interactive, categorized menu of every available script (scheduled data
jobs, backups, derived-data recomputation, demo dataset management, and
more).

### Targeted checks

```powershell
python -m pytest <path> -q                          # Python tests
python -m ruff check apps packages scripts tests     # Python lint
python -m mypy apps packages scripts tests           # Python types
pnpm --filter @country-decision-atlas/web typecheck  # frontend types
pnpm --filter @country-decision-atlas/web lint       # frontend lint
cd apps/notifier && go vet ./... && go test ./...    # Go (drop -race locally on Windows without a C toolchain; CI runs the -race gate)
```

## Documentation

- `docs/README.md` — the documentation index (architecture, API, product, decisions, operations, research).
- `docs/operations/working-standard.md` — how any task is worked (branching, quality gate, layering rules).
- `docs/architecture/overview.md` — what's built today.
- `docs/product/roadmap.md` — the implementation plan, by episode.
- `docs/architecture/invariants.md` — invariants that must never be broken.
- `utils/synthetic_data/README.md` — the synthetic data pipeline in full detail.
- `.ai/universal/` and `.ai/project/` — the rule modules that govern how AI assistants work in this repo.

## Project status notes

- The three countries currently in the data (Russia, Uruguay, Argentina)
  are a manually-curated test set, conserved as a hidden, restorable demo
  dataset rather than deleted. Migrations seed them with `is_demo=TRUE`
  (hidden from the public API/UI) — run
  `python scripts/dev_tools/restore_demo_countries.py --visible` after
  `apply_migrations.py` (see Quick start above) to make them visible.
- The project runs in **autonomous development mode**: no real external
  service integrations (AI providers, translation, Telegram) are wired in
  yet — everything works offline through fake-by-default provider seams
  (e.g. `AI_MODE=fake`, `TELEGRAM_MODE=fake` in `.env.example`).
