# utils/synthetic_data

Generates a self-contained, fully fictional "world" — countries, users,
authors, articles, comments, sources, legal signals, documents, SQL
fixtures, and manual-test scenarios — for local development, manual
testing, and demos of Country Decision Atlas. Everything one run produces
refers to the same fictional facts: a country's metrics, its PDF brief,
its SQL row, and its test scenario never disagree with each other.

This file is the canonical reference for the pipeline (architecture, data
model, safety rules, CLI, testing). It replaces the original project ТЗ,
which described the plan before implementation; all 7 stages of that plan
are now implemented and merged, so this document describes the system as
it actually is. The package itself moved from `scripts/synthetic_data` /
`docs/synthetic_data` to `scripts/synthetic_data.py` (thin entry point) +
`utils/synthetic_data/` (full implementation) — see
`docs/_arch_/SYNTHETIC_DATA_PLAN.md` Stage 0.

## Safety rules and non-goals

These are invariants, not suggestions — every layer of the pipeline is
built to enforce them automatically:

- **No real countries, people, or documents.** All country names, codes,
  slugs, personal names, and institutions come from closed fictional word
  lists (`utils/synthetic_data/input_data/world_config.json`) and are
  checked against a deny-list of real country names/codes during
  validation (`core/world_validation.py`).
- **No network calls.** The generator never contacts a government site,
  LLM, news API, or any external service.
  `tests/test_no_network_imports.py` statically forbids importing
  `requests`/`httpx`/`urllib.request`/`socket`/`aiohttp` anywhere in
  `utils/synthetic_data`, and restricts `psycopg` usage to
  `sql_fixture.py`/`sql_loader.py`.
- **Never production.** `load-sql`/`cleanup-sql` refuse to run unless
  `APP_ENV=local` is set explicitly — an unset `APP_ENV` is treated as
  production (fail-closed, same policy as `app/core/config.py`) — and
  always require `--confirm` before touching a database.
- **Not an identity-document generator.** The pipeline must never be used
  to produce anything that could pass as a real ID, visa, bank document,
  or government certificate.
- **Every artifact is marked.** `SYNTHETIC TEST DATA - NOT REAL` (English,
  always present) plus a localized variant appear in every JSON payload,
  SQL comment, document header/footer, and the manifest.
- **Migrations are never touched.** The SQL fixture is a separate,
  idempotent script applied *after* `scripts/apply_migrations.py`; it
  never edits, renames, or replaces a migration file.
- **Generated output never goes into git by default** — only the input
  configuration, code, and small committed test samples are tracked.
  `.synthetic_data/` is git-ignored.

## Architecture: one canonical world

A single run first builds one canonical, in-memory `SyntheticWorld`
(`core/world_models.py`) from a seed and a profile. Every output format is
then rendered *only* from that already-validated world — nothing is
allowed to invent its own facts:

```text
world_config.json + seed
        |
        v
  WorldGenerator (core/world_generator.py)
        |
        v
  SyntheticWorld  --validate_world()-->  core/world_validation.py
        |
        +-------------+-------------+--------------------+--------------+
        |             |             |                     |              |
        v             v             v                     v              v
  canonical JSON   SQL fixture   document renderers    manifest/ZIP   website graph
  (json_renderer)  (sql_fixture)  (document_rendering/)  (packaging)  (web/graph.py)
```

| Layer | Responsibility | Key modules |
| --- | --- | --- |
| `input` | Load/validate world config, locale corpus, recipes | `core/world_input.py`, `core/locale_corpus.py`, `core/input_data.py` |
| `domain` | Canonical world models | `core/world_models.py` |
| `generation` | Deterministic entity creation from seed + profile | `core/world_generator.py`, `core/seed.py` |
| `validation` | Structural + semantic + safety checks | `core/world_validation.py` |
| `renderers` | JSON/TXT/XLSX/DOCX/PDF from canonical world + recipes | `core/document_rendering/`, `core/document_recipes.py` |
| `packaging` | Manifest, checksums, ZIP, validation report | `core/dataset_packager.py`, `core/manifest.py`, `archive/zip_archiver.py` |
| `sql` | Safe, idempotent, isolated DB fixtures | `core/sql_fixture.py`, `core/sql_loader.py` |
| `web` | Browsable synthetic web (sites, pages, anomalies, a local server) | `web/graph.py`, `web/html_renderer.py`, `web/server.py`, see below |
| `cli` | Commands, dry-run, discovery, pruning | `cli.py`, `core/dataset_discovery.py`, `core/dataset_prune.py` |

A second, independent code path (`generators/`, invoked by the legacy
CLI mode described below) generates domain-agnostic placeholder files
(random PDF/DOCX/XLSX/Markdown/JSON with no connection to countries). It
predates the world pipeline, is still used for structural format
smoke-testing, and is deliberately kept separate — mixing locale/RTL/font
logic into it would risk regressing that independent, already-tested mode
for no benefit.

## Domain model

`core/world_models.py` defines the canonical entities. Every entity below
is deterministically derived from the master seed plus a stable per-entity
context (`derived_seed = hash(master_seed, "country", country_id,
"metrics")`, see `core/seed.py`), so adding one document recipe never
changes another country's metrics.

| Entity | Notes |
| --- | --- |
| `SyntheticCountry` | Stable UUID, fictional code/slug/name, archetype, metric history (multiple time snapshots), strengths, risks, uncertainties, events, sources. |
| `MetricSnapshot` / `SyntheticEvent` | A dated set of metric values, and the synthetic event (rule change, service improvement, cost rise, ...) that explains a change between snapshots. |
| `SyntheticSource` | One per country event: title, URL placeholder, confidence. |
| `SyntheticUser` / `SyntheticAuthor` | Fictional names/emails on reserved domains (`example.test`), roles, reputation, specialization. |
| `SyntheticArticle` / `SyntheticComment` | Country-linked content with moderation status; comments reference an article + user. |
| `SyntheticLegalSignal` | Event, effective date, affected countries, impact, confidence — always tied to an existing event/source. |
| `SyntheticDocumentRecipe` | A locale + document type + ordered content blocks resolved from `document_blocks`/`document_recipes` in `world_config.json` — never independent prose. |
| `SyntheticScenario` | A machine-readable manual-test story: initial state, steps, expected results, related artifacts, risk labels. |
| `WorldMetadata` | `dataset_id`, `schema_version`, `generator_version`, `seed`, `profile`, `supported_locales`, `source_config_checksum`, `generated_on`, `fictional_notice`. |

Countries are assigned one of 5 archetypes (not independently randomized
metrics) so the result stays plausible — e.g. a "wealthy, restricted"
country never looks identical to a "recovering" one:

| Archetype slug | Character |
| --- | --- |
| `stable_technical_expensive` | Stable, technologically strong, expensive. |
| `affordable_unstable` | Affordable but institutionally unstable. |
| `free_small_market` | Free and safe, small labor market. |
| `wealthy_restricted` | Economically strong, restricted civil freedoms. |
| `recovering_country` | Recovering from (or declining after) a notable event. |

Each archetype defines a `[minimum, maximum]` range for 8 metric
dimensions (`economy`, `cost_of_living`, `safety`, `civil_freedoms`,
`institutional_stability`, `digital_infrastructure`,
`migration_openness`, `data_confidence`) in
`utils/synthetic_data/input_data/world_config.json`. No profile ever makes
one country strictly best on every dimension.

## Profiles

| Profile | Effect |
| --- | --- |
| `balanced` | Baseline: varied trade-offs, no bias. The reference profile for reproducibility tests. |
| `crisis` | ~90% chance of a negative metric direction per country (except `recovering_country`, which is already framed as recovering). |
| `optimistic` | Metrics biased toward the upper third of the archetype's range. |
| `data_quality` | `data_confidence` biased toward the lower half of the archetype's range — incomplete/conflicting/stale data on purpose. |
| `moderation` | 5 comments per article instead of 3 — more moderation-status variety. |

`balanced` at a fixed seed is byte-for-byte stable across changes to this
pipeline (`test_balanced_profile_world_is_unchanged_across_this_change`)
— every other profile is a bias applied on top of the same generator.

## Scale (`--scale`)

Spec section 19's "too large and slow a dataset" risk names volume
profiles as the mitigation. `--scale` (`generate`/`plan`) controls how many
locales and scenario variants per category get built, independent of
`--countries` (still 4 or 5) and `--formats` (unchanged, still your own
choice of output formats):

| Scale | Locales | Scenario variants/category | Use |
| --- | --- | --- | --- |
| `large` (default) | all 15 | 2 | Original, full-coverage behavior — unchanged unless `--scale` is passed. |
| `medium` | 8 (`en-US`, `es-ES`, `ru-RU`, `ar-SA`, `zh-Hans-CN`, `ja-JP`, `th-TH`, `ta-IN`) | 2 | Faster local runs that still cover Latin/Cyrillic/RTL/CJK/Thai/Tamil. |
| `small` | 3 (`en-US`, `ar-SA`, `zh-Hans-CN`) | 1 | Load-testing/CI: smallest dataset that still proves RTL and CJK render. |

Locale subsets are a fixed, hand-picked list (not a blind prefix slice), so
even `small` keeps script diversity. `world.metadata.supported_locales`
always reflects exactly what a given run built, and validation checks
document-recipe coverage against that same set — a reduced-scale dataset
never claims 15-locale coverage it doesn't have.

## Translation preview (`translate`)

A derived, fake-by-default test mode (spec section 8.3, "translation test
modes"): takes an already-generated dataset's `en-US` (or other) document
recipe blocks and produces a *separate* fake-translated copy — it never
edits or replaces the canonical source text.

```powershell
python scripts/synthetic_data.py translate --dataset <dataset_id> --target-locale ar-SA
```

Writes `translations/<target_locale>.json` inside the dataset directory
(not part of `manifest.json`/the package ZIP). Each record keeps the
source locale/text, target locale, translated text, provider name+version
(`fake-shuffle-mt`), seed, generation date, a `fake_synthetic_preview`
status, and the same `SYNTHETIC TEST DATA - NOT REAL` marker as every other
artifact. The "translation" is a deterministic word-shuffle, not a real MT
call — no network, no LLM, nothing leaves the machine. Swapping in a real
provider is out of scope for this task and gated behind the project's
integration-tranche rule (`TELEGRAM_MODE=fake`-style fake-by-default
seams only, until explicitly approved).

## CII score preview (`cii-preview`)

A derived, JSON-only preview of what a CII (Country Index) card/comparison
matrix could look like for a synthetic country — for frontend/QA work
against believable numbers, without touching the real
`cii_metric_definitions`/`country_metric_values`/`country_cii_scores`
tables or `utils/synthetic_data/core/sql_fixture.py` at all.

```powershell
python scripts/synthetic_data.py cii-preview --dataset <dataset_id>
```

Writes `reports/cii_preview.json` inside the dataset directory. It uses
its own, entirely separate `syn_`-prefixed metric catalog (`syn_economy`,
`syn_cost_of_living`, `syn_safety`, `syn_civil_freedoms`,
`syn_institutional_stability`, `syn_digital_infrastructure`,
`syn_migration_openness` — 7 of the 8 archetype dimensions, made-up
weights) so a dashboard can never confuse a fake score with a real one.
`data_confidence` is deliberately excluded from the score and surfaced
only as a `confidence` (`high`/`medium`/`low`) label instead — it measures
data quality, not country quality, matching the real product's rule that
derived trust-style metrics never mix into CII. The overall score is a
geometric mean (same shape as the real formula), rounded to 2 decimals.

This was scoped deliberately as JSON-only after review: the real CII
tables have no scope/tenancy column to separate synthetic from real rows,
two of the real product's data-quality checks scan `cii_metric_definitions`
and `scenario_metric_weights` globally with no per-dataset filter, and the
trust/drift screens don't even read CII tables (they read
`sources`/`evidence_items`/`legal_signals`/`country_platform_metrics`
instead). Writing real rows into the production CII tables would require
a schema migration and changes to `apps/api` repositories — a separate,
owner-approved episode, not a change to this script.

## Synthetic Web Environment (`web/`)

A browsable, deterministic web of fictional sites rendered *over* an
already-built `SyntheticWorld` — one site per country, real pages for the
country's own source/article/legal-signal, cross-site links between homes,
and deliberately broken pages for link-handling tests. Never invents world
facts: every non-anomaly page is grounded in an entity the world already
contains (spec-equivalent principle to the document renderers above).

```text
SyntheticWorld + already-rendered documents + web_config.json
        |
        v
  build_web_graph()  (web/graph.py)  ---uses seed_factory.rng()--->  deterministic
        |                                                             site/page/link
        v                                                             assignment
  assign_anomalies()  (web/anomalies.py)
        |
        v
  WebGraph  --validate_web_graph()-->  web/validation.py
        |
        +----------------------+
        |                      |
        v                      v
  render_web_graph()      create_app()
  (web/html_renderer.py)  (web/server.py)
  writes .html files      serves /sites/... and /files/...
```

**Site archetypes** (`input_data/web_config.json`): `gov_portal`,
`news_portal`, `blog`, `wiki` — each declares which page kinds it
publishes (`source`/`article`/`notice`) and a title template. A country's
archetype is chosen deterministically from the seed, same mechanism as
country archetypes in `world_config.json`.

**Anomalies** (`web/anomalies.py`): for every site and every anomaly kind,
one seeded coin flip (probability = `anomaly_ratios.<kind>` in
`web_config.json`) decides whether that site gets one instance, linked
from its home page:

| Kind | HTTP behavior | Has a rendered file? |
| --- | --- | --- |
| `not_found` | 404 | No — the page never exists on disk. |
| `server_error` | 500 | No — `web/server.py` recognizes the path from the graph and answers 500 without touching disk. |
| `redirect` | 302 to a real page (plus a `<meta http-equiv="refresh">` fallback in the file itself, for non-HTTP access) | Yes. |
| `duplicate` | 200, byte-identical to another page | Yes. |
| `empty` | 200, near-zero content | Yes — the one page deliberately exempt from carrying the fictional-data notice, since being empty is the whole point. |
| `huge` | 200, padded to `huge_page_padding_paragraphs` filler paragraphs | Yes. |
| `broken_encoding` | 200, body bytes are latin-1 while the page declares `charset=utf-8` (genuine mojibake, not a bug) | Yes. |

**Downloads**: a source/article/notice page links to up to 3 of its
country's already-rendered documents (`documents/<locale>/...`) as
`/files/<relative path>`, served by `web/server.py` with
`Content-Disposition: attachment`. If no documents were rendered in the
same run (`--formats web` alone, with no `pdf`/`docx`/etc.), pages simply
have no download links — `render-web` on an existing dataset instead
discovers whatever documents are already on disk
(`core/dataset_packager.py`'s `discover_existing_documents`), so it can
add real download links retroactively.

**`SyntheticSource.url` is never touched.** `core/world_validation.py`
requires it to always start with `synthetic://` — a hard invariant, not
a placeholder waiting to be filled in. Instead, `web/graph.py`'s
`source_page_urls()` produces a separate `source_id -> "/sites/..."`
mapping, written to `<dataset>/websites/source_pages.json` and folded into
`manifest.json` — "the real page for this source" is resolved through
that mapping, not by mutating the canonical world.

**One server, path-based routing** — `/sites/<site-slug>/...` and
`/files/<relative document path>`, no nginx, no per-site container, no
virtual hosts. `web/server.py` is a small FastAPI app (the project's
existing `fastapi`/`uvicorn` dependencies, not new ones); `web/html_renderer.py`
uses only stdlib string templating (no jinja2 or other new dependency).

```powershell
# Render a website alongside the usual document formats
python scripts/synthetic_data.py generate --formats web,pdf --seed 42017

# Re-render only the website layer for an existing dataset (picks up
# whatever documents already exist on disk for download links)
python scripts/synthetic_data.py render-web --dataset <dataset_id>

# Browse it
python scripts/synthetic_data.py serve --dataset <dataset_id> --port 8080
# -> http://127.0.0.1:8080/sites/<site-slug>/index.html
```

`--formats web` is deliberately excluded from the `all` alias — building
the site graph adds real time to every `generate` call, so it stays
opt-in.

## Locales

All 15 locales get their own hand-written (not machine-translated) text
blocks, names, and comment templates in
`utils/synthetic_data/input_data/locale_corpus.json` — a fact never changes
meaning across locales, only its rendered text does.

| Locale | Language / script | Tests |
| --- | --- | --- |
| `en-US` | English, Latin | Baseline Latin text. |
| `es-ES` | Spanish, Latin | Diacritics, inverted punctuation. |
| `ru-RU` | Russian, Cyrillic | Non-Latin alphabet. |
| `hi-IN` | Hindi, Devanagari | Complex Indic graphemes. |
| `fa-IR` | Persian, Arabic script | RTL, joined letterforms. |
| `ar-SA` | Arabic, Arabic script | RTL, digits, mixed direction. |
| `zh-Hans-CN` | Chinese, simplified Han | Unspaced ideographs. |
| `ja-JP` | Japanese, kanji/kana | Multiple mixed scripts. |
| `ko-KR` | Korean, Hangul | Hangul syllable blocks. |
| `tr-TR` | Turkish, Latin | Special Latin letters/casing. |
| `id-ID` | Indonesian, Latin | Non-Latin language family on Latin script. |
| `sw-KE` | Swahili, Latin | Independent (Bantu) language family. |
| `vi-VN` | Vietnamese, Latin + tones | Dense diacritics, Unicode normalization. |
| `th-TH` | Thai, Thai script | Word segmentation, unusual line breaks. |
| `ta-IN` | Tamil, Tamil script | Another Indic script. |

Region subtags are technical locale identifiers only — they don't imply
any synthetic country corresponds to a real one.

**Unicode/RTL handling** (`core/text_shaping.py`, `core/font_registry.py`):
UTF-8 everywhere, real Unicode characters in JSON (not `\uXXXX` escapes),
explicit RTL paragraph direction for Arabic/Persian with mixed
number/Latin-identifier/URL runs in the same line, embedded fonts for
PDF/DOCX (not relying on an OS-installed font). Fonts are subsetted static
Noto Sans instances (OFL-licensed, see
`utils/synthetic_data/assets/fonts/NOTICE.md`) — full CJK Noto fonts are
6-18 MB, over this repo's 1 MB/file pre-commit limit, so the CJK ones are
subsetted to the codepoints the corpus actually uses.

## Output layout

```text
.synthetic_data/<dataset_id>/
  manifest.json                     # every artifact: path, format, locale, checksum
  canonical/
    synthetic_world.json            # the one source of truth
  sql/
    seed_synthetic_world.sql        # idempotent fixture (see below)
    cleanup_synthetic_world.sql     # deletes only this dataset_id
  documents/<locale>/
    txt/  xlsx/
    docx/copyable/  docx/non_copyable/  docx/mixed/
    pdf/copyable/   pdf/non_copyable/   pdf/mixed/
  websites/                            # only when --formats includes web
    graph.json                         # the WebGraph, reloaded by `serve`
    source_pages.json                  # source_id -> "/sites/..." mapping
    <site-slug>/
      index.html  about.html
      sources/<source_id>.html
      articles/<article_id>.html
      notices/<signal_id>.html
      anomalies/<kind>.html            # not_found/server_error: no file
  reports/
    validation_report.json
    generation_summary.md
  package/
    synthetic_dataset_<dataset_id>.zip
```

`copyable` documents have an extractable text layer; `non_copyable` ones
render text as an image (simulating a scan); `mixed` documents contain
both a real text layer and an image fragment in the same file.

## SQL fixtures and database safety

`core/sql_fixture.py` covers the minimal first set of tables: `countries`,
`country_profiles`, `sources`, `legal_signals`. Deliberately **not**
covered (documented gaps, not oversights):

- Users/authors/articles/comments — these have no matching real DB
  tables; they exist only in the JSON/document layer.
- Manual-test `scenarios` — the real `scenarios`/`scenario_criteria`
  tables serve a different concept (decision-methodology weights), not
  manual test scripts.
- `country_metric_values`/`cii_metric_definitions` — the real CII
  calculation uses a fixed global metric set that doesn't map 1:1 onto
  the 8 synthetic archetype dimensions, and those tables have no scope
  column to separate synthetic from real rows. See "CII score preview"
  above for the JSON-only alternative that ships instead; writing real
  rows into these tables is left for a separate, owner-approved task.
- Search indexing (`search_documents`) — a separate existing dev-tools
  step (`rebuild_search_index.py --all`), not part of the fixture.

Guarantees, all enforced in code (not just convention):

- Values are only ones the pipeline itself created; strings/identifiers
  are escaped through `psycopg.sql`, never string concatenation.
- Every row carries a `syn_<dataset_id>`-scoped identity so datasets never
  collide.
- `INSERT ... ON CONFLICT (id) DO UPDATE` makes `load-sql` idempotent —
  re-running it never duplicates rows.
- `cleanup-sql` deletes only rows matching the dataset's own IDs, with an
  extra `AND is_demo = FALSE` guard on the `countries` delete so the
  conserved demo dataset (`argentina`/`russia`/`uruguay`) can never be
  touched even by a bug.
- `ensure_not_production()` in `core/sql_loader.py` runs before any
  `psycopg.connect` — a missing or `production` `APP_ENV` is rejected
  before a connection is ever opened.

## CLI

### World commands (the current interface)

```powershell
# Validate the world configuration without generating anything
python scripts/synthetic_data.py validate --profile balanced

# Show what would be generated (countries, scenarios) without writing files
python scripts/synthetic_data.py plan --profile crisis --seed 42017

# Generate a full dataset (canonical world + all documents + SQL + package)
python scripts/synthetic_data.py generate --profile balanced --seed 42017

# Generate only canonical JSON + SQL fixture (skip document rendering)
python scripts/synthetic_data.py generate --formats json --seed 42017

# Re-render an existing dataset's documents from its canonical JSON
python scripts/synthetic_data.py render --dataset <dataset_id> --formats pdf,docx,xlsx,txt

# Re-render only the website layer (see Synthetic Web Environment above)
python scripts/synthetic_data.py render-web --dataset <dataset_id>

# Serve an already-generated website locally
python scripts/synthetic_data.py serve --dataset <dataset_id> --port 8080

# Rebuild manifest + ZIP from files already on disk, without re-rendering
python scripts/synthetic_data.py package --dataset <dataset_id>

# List every dataset under --output-root (id, seed, profile, size, ...)
python scripts/synthetic_data.py list

# Delete old datasets, keeping the N most recent by manifest mtime
python scripts/synthetic_data.py prune --keep-last 5 --confirm

# Print the canonical SyntheticWorld JSON Schema
python scripts/synthetic_data.py schema

# Generate a smaller, faster dataset for load-testing/CI (see Scale below)
python scripts/synthetic_data.py generate --scale small --seed 42017

# Compare two datasets (countries/metrics/scenario mix)
python scripts/synthetic_data.py diff --dataset-a <id-a> --dataset-b <id-b>

# Build a fake-translated preview of a dataset's en-US text (see below)
python scripts/synthetic_data.py translate --dataset <dataset_id> --target-locale ar-SA

# Build a fake CII score preview for a dataset (JSON-only, see below)
python scripts/synthetic_data.py cii-preview --dataset <dataset_id>

# Load / clean up a dataset's SQL fixture against a local database
$env:APP_ENV = "local"
$env:DATABASE_URL = "postgresql://country_atlas:change-me@localhost:5433/country_atlas"
python scripts/synthetic_data.py load-sql --dataset <dataset_id> --confirm
python scripts/synthetic_data.py cleanup-sql --dataset <dataset_id> --confirm
```

Common flags: `--seed` (omit for a random one, always printed),
`--countries` (4 or 5), `--output-root` (default
`.synthetic_data`), `--dry-run` (builds/validates without
writing, or previews `load-sql`/`cleanup-sql`/`prune` without
connecting/deleting), `--json` (single structured JSON object instead of
text), `--quiet` (suppress routine text; errors still go to stderr).
`validate`/`plan`/`list`/`prune`/`schema` never import
reportlab/python-docx/openpyxl/psycopg — those are lazily imported only
inside `generate`/`render`/`package`/`load-sql`/`cleanup-sql`, so the
lighter commands work without those libraries installed.

Errors are actionable by design: an unknown `--dataset` reports the
searched `--output-root`, the id you passed, and the list of dataset ids
that *were* found there.

### Legacy command (domain-agnostic placeholder files)

```powershell
python scripts/synthetic_data.py --formats pdf,docx,xlsx --count 3 --seed 42017
```

Generates neutral-content sample files unrelated to any country/domain —
used for structural format smoke-testing independent of the world
pipeline. `--formats` accepts `json`, `markdown`, `xlsx`,
`docx-copyable`/`docx-non-copyable`/`docx-mixed`/`docx` (all 3),
`pdf-copyable`/`pdf-non-copyable`/`pdf-mixed`/`pdf` (all 3), or `all`.

## Mock HTTP server (`mock_server`)

A local FastAPI server that serves an already-generated dataset over HTTP,
mimicking the shape of `apps/api`'s public read endpoints closely enough
that `apps/web` can run entirely on synthetic data with no database at all
— point `NEXT_PUBLIC_API_BASE_URL` at it instead of the real backend.

```powershell
python scripts/synthetic_data.py generate --seed 42017
python -m utils.synthetic_data.mock_server --dataset <dataset_id> --port 8000
```

| Endpoint | Notes |
| --- | --- |
| `GET /api/v1/countries` | Paginated list. |
| `GET /api/v1/countries/{slug}` | Country detail. |
| `GET /api/v1/countries/{slug}/profile` | Backed by the country's generated article summary. |
| `GET /api/v1/countries/{slug}/trust` | Fake trust score — reuses the `data_confidence` archetype metric. |
| `GET /api/v1/countries/{slug}/cii` | Backed directly by `core/cii_preview.py`. |
| `GET /api/v1/countries/compare?countries=a,b&scenario=<slug>` | Two-country CII comparison. |
| `GET /api/v1/countries/{slug}/sources` | The country's own generated source(s). |
| `GET /api/v1/search?q=` | Substring match over country names/articles/sources. |

Every response carries an `X-Synthetic-Data: true` header, and the same
`{"error": {"code","message","details"}}` error envelope as the real API
(404 for an unknown country slug, 422 for a malformed `compare` request).
CORS defaults to allowing `http://localhost:3000` (Next.js's dev port);
override with repeatable `--cors-origin` flags.

**Scoped deliberately** — endpoints without a faithful synthetic model
behind them are left out rather than half-faked: `drift` and the
aggregated `/card` read-model (no synthetic drift-snapshot data),
`/scenarios`/`/methodology` (static real methodology content, not
per-country synthetic data — mixing it in here risked exactly the kind of
blurring the safety rules above forbid), `community`, `country-pairs`,
`routes`, `evidence-items` (no matching synthetic entities). Response
shapes are hand-mirrored from `packages/contracts/generated/types.ts` and
`apps/api/app/schemas/*.py`, not regenerated automatically — if the real
contract changes shape, this mock's schemas need a manual follow-up pass.

## Reproducibility

The same `world_config.json` + `seed` + `profile` always produce the same
logical world (countries, metrics, content, scenarios) — verified by
`test_world_generator.py`. Only `generated_on` (a timestamp) and file
mtimes are excluded from that comparison; every derived seed comes from
`hash(master_seed, entity_kind, entity_id, purpose)`
(`core/seed.py`), not from dict iteration order, wall-clock time, or a
UUID generated after the fact.

## Testing

```powershell
py -3.12 -m pytest utils/synthetic_data/tests -q
```

341 tests as of this writing, covering: determinism across seeds/profiles,
referential integrity (every id resolves), the real-country/PII deny-list,
SQL fixture idempotency and cleanup isolation against a live local
Postgres (manual verification — see below), production-guard fail-closed
behavior, artifact structural validity (JSON schema, XLSX sheets,
DOCX/PDF open + copyable/non-copyable/mixed properties), Unicode
round-tripping for all 15 locales, CLI dry-run/error-path behavior, the
website graph's determinism/link-resolution/anomaly-HTTP-status behavior
(`test_web_*.py`), and a
Stage-7 smoke test that bounds a full `generate --formats all` run's time
(<120s) and package size (<25MB).

`pyproject.toml` scopes `testpaths` to `tests/`, so this suite does **not**
run as part of a bare `pytest` invocation. It is wired into the project
quality gate as its own explicit step in
`scripts/dev_tools/full_check.py` (`phase_static_quality`) — it always
runs alongside the main suite, on every profile.

SQL fixture load/idempotency/cleanup/production-guard behavior against a
real database is verified manually against a live local Postgres rather
than through an automated pytest+DB integration test, since the project
has no other pytest tests requiring a live database (DB-dependent
behavior is otherwise verified via the quality gate's Docker-stack curl
smokes, not pytest). To re-verify by hand:

```powershell
docker compose up -d postgres
$env:APP_ENV = "local"
python scripts/apply_migrations.py
python scripts/synthetic_data.py generate --formats json --seed <any>
python scripts/synthetic_data.py load-sql --dataset <dataset_id> --confirm
# ... inspect countries/sources/legal_signals, re-run load-sql to confirm no duplicates ...
python scripts/synthetic_data.py cleanup-sql --dataset <dataset_id> --confirm
# ... confirm only the synthetic countries are gone, argentina/russia/uruguay remain ...
```

## Known limitations / deferred work

- **Translation preview is fake-by-default only.** `translate` proves the
  derived-artifact pipeline (source/target text, provider/version, seed,
  status, marking — see above) but its "translation" is a deterministic
  word-shuffle, not a real machine-translation call. Wiring in an actual
  neural-translation provider (local model or external) is out of scope
  here and gated behind the project's integration-tranche rule.
- **No full-text search integration.** Unicode normalization (NFC/NFD) is
  covered at the unit-test level for Vietnamese text; there is no
  synthetic-corpus-backed test against the application's real search
  index.
- **SQL fixtures cover 4 tables**, not the full domain — see "Known gaps"
  above for exactly which entities are JSON/document-only for now.
- **New countries, languages, or AI-driven translation are out of scope**
  for this generator, matching the project-wide rule against adding real
  countries/languages or using AI translation without an explicit owner
  decision.

Further work (new domain entities, new world profiles, new document
formats, a real translation provider, a plugin registry for
archetypes/locales/document types) should be scoped as separate,
individually-planned tasks rather than folded into this pipeline silently.
