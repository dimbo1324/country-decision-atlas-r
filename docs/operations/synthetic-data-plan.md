# Synthetic Data Ecosystem — Master Plan

Date: 2026-07-17. Status: an approved plan; Stages 0-2 implemented (see the
per-stage status notes below), Stages 3-4 not started.
Decision owner: the project owner. Execution: one stage per task, each
stage its own branch + `task-checklist.md` + a full quality gate,
per the rules in `.ai/universal/01-workflow.md` and `02-task-checklist.md`.

---

## 1. Goal

Move completely off real-country data (Russia, Argentina, Uruguay in
`database/fixtures/demo_countries/`) onto fully fictional synthetic data that
the application runs on entirely: countries, metrics, sources, documents,
users, articles, comments — and, crucially, a **Synthetic Web Environment**:
local web pages you can browse, download synthetic files from, and that
sources (`sources`) inside the app link to.

Why:

- reproducibility: any bug and any hypothesis can be checked against a
  deterministic, rebuildable world;
- zero claims about real facts regarding real countries;
- full control over the test ecosystem: an "internet" that never disappears
  and never shifts under your feet;
- one script (one command) rebuilds the entire world.

An explicit anti-goal (stated by the owner): **don't rabbit-hole**. This
module should help, not turn into its own forever-project. So the plan builds
on what already exists and cuts everything unnecessary (section 7).

## 2. What already exists — and what we're reusing

`scripts/synthetic_data/` — a mature pipeline (~117 files, 302 tests).
The canonical reference is `scripts/synthetic_data/README.md`. The key
pieces:

| Already works | Where |
| --- | --- |
| A canonical fictional world (countries, metrics, users, authors, articles, comments, sources, legal signals, scenarios) | `core/world_models.py`, `core/world_generator.py` |
| "Metadata anchors": country archetypes with ranges across 8 metrics + bias profiles (`balanced`/`crisis`/`optimistic`/…) | `docs/synthetic_data/input_data/world_config.json`, `core/world_generator.py` |
| Determinism: `derived_seed = hash(master_seed, entity, id, purpose)` — a PDF, a SQL row, and a JSON record for the same country never disagree | `core/seed.py` |
| Safety: a deny-list of 195 real countries, a network ban (a static test), a `SYNTHETIC TEST DATA - NOT REAL` marker on every artifact, a production guard for SQL | `core/world_validation.py`, `tests/test_no_network_imports.py`, `core/sql_loader.py` |
| Documents: PDF/DOCX (copyable / non-copyable "scan" / mixed), XLSX, TXT, JSON, ZIP; 15 locales, RTL/CJK, embedded fonts | `core/document_rendering/`, `assets/fonts/` |
| SQL fixtures into a real database (`countries`, `country_profiles`, `sources`, `legal_signals`), idempotent, with demo-country protection | `core/sql_fixture.py`, `core/sql_loader.py` |
| A mock HTTP API — the frontend runs on synthetic data with no database | `mock_server/` |
| A CLI: `validate / plan / generate / render / package / list / prune / diff / translate / cii-preview / load-sql / cleanup-sql` | `cli.py` |

**The plan's core principle: don't rewrite this — instead (a) relocate it to
the right place, (b) build out the one large missing layer — the web
environment, (c) carry it through to replacing the real fixtures.**

## 3. Principles and guardrails (inherited, not revisited)

1. No real countries, people, or documents; a deny-list is mandatory.
2. No network access and no LLM calls in the generator (offline-by-default;
   an LLM seam is only ever added by a separate owner decision, in the
   integration tranche).
3. Every artifact is marked as synthetic.
4. Determinism: one `seed + profile + config` = one and the same world.
   "Fresh data on every run" = a random seed by default, which is printed
   and always reproducible.
5. Migrations (`database/migrations/`) are untouchable — synthetic data only
   enters the database through idempotent fixtures, after
   `apply_migrations.py`.
6. Generated output never goes into git; in git — only code, input configs,
   and small test snapshots.
7. Heavy generation is never part of the default quality gate — only an
   explicit flag/command.

## 4. Target architecture

### 4.1. Repository layout (after every stage)

```text
scripts/synthetic_data.py            # the entry point, <=10 lines (like dev_tools_scripts_runner.py)
utils/synthetic_data/                # THE ENTIRE IMPLEMENTATION
  __init__.py
  cli.py                             # commands (moved from scripts/synthetic_data/cli.py)
  core/                              # the world, seeds, validation, document renderers (moved)
  generators/                        # legacy format generators (moved)
  mock_server/                       # the mock API (moved)
  archive/                           # zip (moved)
  assets/fonts/                      # fonts (moved)
  web/                               # NEW: the Synthetic Web Environment (Stage 1)
  input_data/                        # input JSON configs (moved from docs/synthetic_data/input_data)
    world_config.json                # archetypes, profiles, name pools, the deny-list, document blocks
    locale_corpus.json                # text for all 15 locales
    web_config.json                  # NEW: site archetypes, link density, anomaly rates
    data.json                        # word/heading pools for the legacy generators
  tests/                             # moved from scripts/synthetic_data/tests
.synthetic_data/                     # generation output (gitignored), formerly docs/synthetic_data/output_data
docs/synthetic_data/                 # REMOVED at the end of Stage 0
```

### 4.2. Data flow

```text
input_data/*.json  +  seed  +  profile  +  scale
        |
        v
  WorldGenerator ----> SyntheticWorld (the single source of truth)
        |                    |
        v                    | (validation: the deny-list, referential integrity)
  world_validation.py <------+
        |
        +---------+-----------+-----------+------------------+-----------------+
        |         |           |           |                  |                 |
        v         v           v           v                  v                 v
   canonical    SQL        documents    manifest/ZIP     Synthetic Web     mock API
     JSON      fixture   PDF/DOCX/...   + reports        (sites, HTML,     (FastAPI)
                                                          the link graph,
                                                          file downloads)
```

The web layer is **just another renderer on top of the same world**, like
JSON/SQL/PDF. It never invents its own facts: the site pages tell the story
of the same countries, events, and sources already in `SyntheticWorld`, and
`SyntheticSource.url` starts pointing at an actually-loadable local page.

### 4.3. Running it (after every stage)

```powershell
# directly
python scripts/synthetic_data.py generate --seed 42017
python scripts/synthetic_data.py serve --dataset <id> --port 8080

# through the dev-tools orchestrator (catalog: utils/dev_tools_scripts_runner/config/scripts.json)
python dev_tools_scripts_runner.py synthetic-data generate --scale small
```

## 5. Input data: a JSON "database" of metadata

The owner's requirement for "a few JSONs with a complex structure and
metadata as anchors for the algorithms" is already implemented via the
**archetypes + profiles + recipes** model, and gets extended, not
reinvented:

| File | Role | Metadata anchors |
| --- | --- | --- |
| `input_data/world_config.json` | The "world schema": name pools, the deny-list, archetypes, profiles, document blocks/recipes | `[min,max]` ranges across 8 metrics per archetype; a profile = a controlled bias; no country is "best at everything" |
| `input_data/locale_corpus.json` | Text for all 15 locales | a fact's meaning never changes across locales — only its rendered text does |
| `input_data/web_config.json` (new, Stage 1) | The "internet schema" | site archetypes (gov portal/news/blog/wiki/corporate), page counts, internal/cross-site link density, anomaly shares (404/500/loops/redirects/duplicates/empty) |
| `input_data/data.json` | Word pools for the legacy generators | as-is |

A rule for the future: new "anchors" are added as declarative fields in
these JSON files, not as branches in Python code.

## 6. Implementation stages

Order is mandatory: 0 → 1 → 2 → 3 → 4. Every stage is self-contained and
leaves the project fully green.

---

### Stage 0 — moving into `utils/synthetic_data` (mechanical, no new features)

Goal: the same architecture as `dev_tools_scripts_runner`: a thin entry
point + a package under `utils/`; `docs/synthetic_data/` stops existing.

Steps:

1. `git mv scripts/synthetic_data utils/synthetic_data` (including `tests/`,
   `assets/`, `README.md`).
2. Bulk-rename imports `scripts.synthetic_data.*` →
   `utils.synthetic_data.*` (the whole package, tests, `conftest.py`).
3. Move the input data: `docs/synthetic_data/input_data/*.json` →
   `utils/synthetic_data/input_data/`; update `core/paths.py`
   (the input and default-output paths).
4. A new default output location: `.synthetic_data/` at the repo root
   (gitignored). In `.gitignore`: remove the `docs/synthetic_data/output_data/`
   line, add `.synthetic_data/`.
5. Create the entry point `scripts/synthetic_data.py` (<=10 lines):
   `from utils.synthetic_data.cli import main; raise SystemExit(main(sys.argv[1:]))`.
6. Update every piece of scaffolding that knows the old path:
   - `scripts/dev_tools/full_check.py` — the separate pytest step
     `scripts/synthetic_data/tests` → `utils/synthetic_data/tests`;
   - `pyproject.toml` — grep for `scripts/synthetic_data` (per-file-ignores,
     excludes) and update it; `utils/` is already wired into ruff/mypy;
   - `.pre-commit-config.yaml` — the regex already covers `utils/`;
   - the `tests/test_no_network_imports.py` equivalent inside the package — the
     scanned path;
   - documentation: `.ai/project/10-project-map.md`, `11-commands.md`
     (+ `sync-agents`), the package README.
7. Register it in the runner's catalog,
   `utils/dev_tools_scripts_runner/config/scripts.json`: title
   `synthetic-data`, filename `synthetic_data.py`, directory `scripts`,
   category `demo` (Demo Dataset Management), aliases `synth`,
   `syn-data`; examples: `generate --scale small`, `validate`, `list`.
8. An optional gate flag: a `synthetic-data smoke` phase in
   `full_check.py` (`validate` + `generate --scale small --dry-run`),
   enabled only via `--with-synthetic`, **off by default**.
9. Remove `docs/synthetic_data/` entirely.

Verification: `py -3.12 -m pytest utils/synthetic_data/tests -q` is green;
`python scripts/synthetic_data.py validate` and `generate --scale small`
work; the full gate is green; `git grep scripts/synthetic_data` and
`git grep docs/synthetic_data` find no live references.

Size: medium. Risk: low (pure mechanics + wide scaffolding).

---

### Stage 1 — the Synthetic Web Environment (the one large new layer)

Goal: a network of local sites generated from the same `SyntheticWorld`,
browsable, with synthetic documents you can download, and that the app's
sources link to.

New modules under `utils/synthetic_data/web/`:

```text
web/
  __init__.py
  models.py         # SyntheticSite, SitePage, LinkEdge, PageAnomaly
  archetypes.py     # loading/validating web_config.json (site types and their structure)
  graph.py          # deterministic page/link graph construction
                    # (within-site and cross-site), tied to the world's countries/events/sources
  html_renderer.py  # HTML rendering from stdlib templates (NO new dependency: no jinja2)
  assets.py         # shared CSS, placeholder images, a favicon
  anomalies.py      # deliberately "bad" pages: 404, 500, loops, redirects,
                    # duplicates, empty/huge pages, broken encoding — shares set by web_config.json
  validation.py     # every link resolves, EXCEPT registered anomalies;
                    # every "download" link points at an artifact that exists in the manifest
  server.py         # serving: one local server, /sites/<slug>/... and /files/...
                    # (FastAPI StaticFiles on top of mock_server OR stdlib http.server — decided during the stage's own task)
```

Key decisions:

- **One server + path-based routing** (`http://localhost:8080/sites/<site>/...`),
  no nginx, no per-site container, no local DNS — exactly the "lighter for
  Docker" conclusion from application A. Virtual hosts remain a deferred
  option, only if it's ever genuinely needed.
- Downloads: pages link to **already-generated** documents from the dataset
  (`documents/<locale>/pdf/...`, etc.), served with
  `Content-Disposition: attachment` — "download/open" works like the real web.
- World integration: `SyntheticSource.url` (currently a placeholder) starts
  pointing at a specific page on a specific synthetic site — clicking a
  source in the app opens a live local page.
- Every HTML page carries a synthetic marker (a comment + a visible footer,
  `SYNTHETIC TEST DATA — NOT REAL`).
- The dataset's output layer: `<dataset>/websites/<site_slug>/...`; the link
  graph and the anomaly list go into the manifest and
  `validation_report.json`.

CLI: `generate --formats web` (as part of a full run) and separately
`render-web --dataset <id>`, `serve --dataset <id> --port 8080`.

Verification: tests for graph determinism, resolving every non-anomalous
link, matching the configured anomaly shares, downloading a file through the
server; a manual pass in a browser.

Size: large (but isolated — no existing subsystem changes, except
`SyntheticSource.url` and the manifest). Risk: medium.

**Status.** Fully implemented: `utils/synthetic_data/web/` (models,
archetypes, graph, anomalies, html_renderer, assets, validation, server —
all 8 modules from the plan), `input_data/web_config.json` (4 site
archetypes, anomaly shares), the CLI commands `generate --formats web` /
`render-web` / `serve` in `cli.py`. One server on FastAPI (an existing
project dependency — not `http.server`, chosen for
`Content-Disposition`, redirects, and correct status codes out of the box,
with no manual HTTP-protocol implementation). 39 new tests
(`test_web_*.py`), 341 total in the package; ruff/mypy clean.

One deviation from the plan's literal text, found and documented along the
way: `SyntheticSource.url` **is not mutated**.
`core/world_validation.py` requires this field to always start with
`synthetic://` — a hard, pre-existing invariant, not an unfilled
placeholder. Instead of mutating the field, `web/graph.py`'s
`source_page_urls()` builds a separate `source_id -> "/sites/..."` map,
written to `websites/source_pages.json` and folded into `manifest.json`
— "the source's live page" is resolved through that map, not by changing
the canonical world model. This keeps `world_generator.py` and its golden
fixture (`test_smoke_snapshot.py`) fully backward-compatible and untouched.

---

### Stage 2 — the full local stack on synthetic data ("the data-migration core")

Goal: one command brings up the whole app on a synthetic world — including
users and user-generated content in the real database.

Steps:

1. An analytical spike (a mandatory first step): mapping
   `SyntheticUser/SyntheticArticle/SyntheticComment` onto real tables
   (`users`, the migration-051 community tables, user stories). The
   package README honestly records that no mapping exists yet today —
   wherever the mapping is unclear, the decision goes to the owner rather
   than being invented.
2. Extending `core/sql_fixture.py`: users (fictional emails on
   `example.test`, a fake password hash, roles), articles/comments per the
   spike's findings. The same guarantees: `syn_<dataset_id>` identity,
   idempotency, `cleanup-sql` deletes only its own rows, the production
   guard.
3. A new `bootstrap-app` command: the chain
   `apply_migrations.py` → `load-sql` → `rebuild_search_index.py --all` →
   `bootstrap_runtime_read_models.py` — "a world inside a running app" in
   one command.
4. Tests: idempotency of the new fixtures, cleanup isolation, an e2e smoke
   test logging in as a synthetic user on the local stack.

Size: medium. Risk: medium (depends on the spike; owner decisions may be
needed).

**Status.** Fully implemented. The analytical spike (step 1) found that the
real schema has no "public articles + comments" concept at all — the owner
decided (see the chat record): `SyntheticArticle`/`SyntheticComment` stay
JSON-only, while `SyntheticUser` maps onto `users` +
`user_auth_credentials`, and every synthetic user gets the ordinary
`role='user'`. The password is real and documented
(`SYNTHETIC_USER_PASSWORD` in `core/sql_fixture.py`), the hash uses a
deterministic salt (dataset_id+user_id) but the same PBKDF2
algorithm/iteration count as the real app — verified against the real
`verify_password()`. `bootstrap-app` is implemented in `cli.py`.

A live check (step 4) against a real
`docker compose up -d postgres redis` + `docker compose up --build -d api`
stack: the full `bootstrap-app` chain ran end to end,
`POST /api/v1/auth/login` with a synthetic user's email and the documented
password returned 200 and a working session token; the wrong password —
401; after `cleanup-sql`, the same login is 401 again (the user is really
gone). 11 new tests for idempotency/determinism/role/hash/marking/cleanup
isolation — all green (33 total in `test_sql_fixture.py`).

**A real bug was found and later fixed** (found outside Stage 2's original
scope, fixed in a separate "whole-project verification" pass): the live
check exposed that `country_fixture_ids()` (Stage 0/1 code) derived
`countries.iso2`/`iso3` only from a country's index within its dataset, not
from `dataset_id` — a second dataset loaded without first running
`cleanup-sql` on the first one always failed with a `UniqueViolation`
(`countries_iso2_key`). Fixed with a dataset_id-seeded permutation of the
26 safe iso2 codes and 676 iso3 codes — guaranteed collision-free within one
dataset, and collisions between two arbitrary datasets are now unlikely
rather than certain (it can't be fully eliminated — `CHAR(2)` only has 26
safe combinations to begin with). Re-verified live after the fix: two
datasets generated back to back with different seeds both `load-sql`'d
successfully with no cleanup in between. Detail —
`utils/synthetic_data/README.md`, "Known limitations."

---

### Stage 3 — replacing `database/fixtures/demo_countries` (only with the owner's explicit approval)

Goal: the real Russia/Argentina/Uruguay leave the fixtures; a "conserved"
synthetic set takes their place.

This is the most tightly coupled stage: the demo countries are protected by
an invariant (`is_demo`, the conservation logic), their slugs are baked into
e2e specs (`tests/e2e/web-mvp-*.spec.ts`), `full_check.py`'s runtime smokes
(`/api/v1/countries/russia/trust`, etc.), and the
`restore/export_demo_countries.py` scripts. So — phased:

1. Fix a seed → generate a reference set of 3 synthetic countries; export
   it in the demo-fixture format (the same
   `scripts/dev_tools/_demo_countries_fixture_spec.py`) into
   `database/fixtures/demo_countries_synthetic/` — **alongside**, not
   replacing.
2. Parameterize the demo-country slugs in e2e and smokes (a constant/fixture
   instead of a hardcoded "russia"), switchable by a flag.
3. Run the full gate and every e2e spec against the synthetic set; get it
   green.
4. Switch the default to the synthetic set; delete
   `database/fixtures/demo_countries/` with the real data; rename the
   synthetic directory to `demo_countries/`.
5. Update the documentation (`docs/…`, `.ai/project/12-domain-rules.md` —
   the "conserved demo countries" rule gets rephrased around synthetic
   slugs) via `sync-agents`.
6. `database/migrations/` are never touched (an invariant); `is_demo`
   semantics stay as-is.

Note: `../decisions/open-questions.md` already records the intent to move
e2e off the fixed real-data set — this stage closes that too.

Size: medium-to-large, mostly test edits. Risk: high in blast radius →
run strictly as its own task, after the owner's explicit "go," with a
rollback plan (the real fixtures stay in git history).

---

### Stage 4 — polish and closeout

1. Final documentation: the package README as the canonical reference;
   commands in `.ai/project/11-commands.md` + `sync-agents`.
2. A review of the README's "known limitations": what stages 1–3 closed,
   what deliberately remains (fake-translate, no LLM).
3. A full gate + e2e run against a clean clone (portability: no dependency
   on local paths/machine specifics).
4. Tidy up: `prune --keep-last N` documented, no clutter in git,
   `--doctor` recommends nothing synthetic-related.

---

## 7. What we're deliberately NOT doing (guarding against rabbit-holing)

| An idea from the original vision | Decision | Why |
| --- | --- | --- |
| nginx, virtual hosts, local DNS, one container per site | no; one server + path routing | the same realism for tests, an order of magnitude less operational overhead |
| Generation via an LLM | no (only a future seam) | the project rule: offline-by-default, integrations come in a separate tranche |
| Video files | no | the app doesn't consume them anywhere |
| New real countries/languages, AI translation | no | forbidden directly by `.ai/project/12-domain-rules.md` |
| "Fresh data on every run" with no seed control | no; a random but printed, reproducible seed | otherwise bug reproducibility is lost |
| Storing generated output in git | no; `.synthetic_data/` is gitignored | the repository holds code and configs, not artifacts |
| Synthetic data in the default quality gate | no; only `--with-synthetic` / an explicit command | the gate already takes ~10 minutes |
| A separate "synthetic-world" microservice in docker-compose | not now | static generation + a local server cover every current scenario; a compose service only if a real need appears |

## 8. Command registry (state after every stage)

```powershell
python scripts/synthetic_data.py validate                          # validate the world configs
python scripts/synthetic_data.py plan --profile crisis --seed 42017
python scripts/synthetic_data.py generate --seed 42017             # the world + documents + SQL + sites + a package
python scripts/synthetic_data.py generate --scale small            # a smaller, faster dataset
python scripts/synthetic_data.py render-web --dataset <id>         # rebuild just the sites
python scripts/synthetic_data.py serve --dataset <id> --port 8080  # a local "internet" + file downloads
python scripts/synthetic_data.py bootstrap-app --dataset <id>      # migrations + SQL + indexes + read models
python scripts/synthetic_data.py list / diff / prune / package / translate / cii-preview
python scripts/synthetic_data.py load-sql / cleanup-sql --dataset <id> --confirm   # APP_ENV=local only

python dev_tools_scripts_runner.py synthetic-data <any command>    # the same, via the orchestrator
python dev_tools_scripts_runner.py --with-synthetic                # the gate + a synthetic smoke test (off by default)
```

## 9. Definition of Done (end to end)

- [+] Stage 0: the package lives in `utils/synthetic_data/`, the entry point
      is `scripts/synthetic_data.py`, `docs/synthetic_data/` is removed,
      the runner knows the `synthetic-data` command, the full gate is green.
- [+] Stage 1: `generate --formats web` / `render-web` produce browsable
      sites; links are validated (`web/validation.py`); anomalies are
      controlled by `web_config.json`; `serve` serves sites and files with
      the correct HTTP status codes (404/500/302) per anomaly kind; "the
      source's live page" resolves through
      `websites/source_pages.json` (not by mutating `SyntheticSource.url`
      — see the "Status" note on Stage 1 above).
- [+] Stage 2: `bootstrap-app` brings up the app on synthetic data in one
      command, including users in the database (content is deliberately
      JSON-only, see the "Status" note on Stage 2 above). A live e2e login
      was confirmed.
- [ ] Stage 3 (pending approval): `database/fixtures/` contains no real
      country data; e2e and smokes are green on the synthetic set.
- [ ] Stage 4: documentation is consistent, a clean clone passes the gate.

Every stage additionally requires: tests added/updated, ruff/mypy clean, a
full green gate, `task-checklist.md` filled with `+`/`-`, a final report
written.

## 10. Risks

| Risk | Mitigation |
| --- | --- |
| The move (Stage 0) breaks hidden references to old paths | `git grep` for `scripts/synthetic_data` and `docs/synthetic_data` as a mandatory verification step; a full gate before and after |
| The web layer starts inventing its own facts and drifts from the world | an architectural rule: the web layer renders `SyntheticWorld`, with no entity generators of its own; links are validated against the manifest |
| Replacing the demo fixtures breaks e2e/smokes | Stage 3 is phased: first "alongside," then a flag switch, rollback = a git revert |
| Mapping articles/comments onto real tables turns out ambiguous | a mandatory analytical spike; ambiguity is resolved by the owner |
| Datasets balloon in size and slow things down | `--scale small/medium/large` already exists; the gate's smoke test uses only `small`, behind a flag; `prune --keep-last` |
| Windows-specific quirks (console encoding, long paths) | already handled in the package (UTF-8 everywhere, embedded fonts); tests run on Windows locally and on ubuntu in CI |
