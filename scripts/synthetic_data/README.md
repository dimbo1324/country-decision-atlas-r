# scripts/synthetic_data

Generates a self-contained, fully fictional "world" — countries, users,
authors, articles, comments, sources, legal signals, documents, SQL
fixtures, and manual-test scenarios — for local development, manual
testing, and demos of Country Decision Atlas. Everything one run produces
refers to the same fictional facts: a country's metrics, its PDF brief,
its SQL row, and its test scenario never disagree with each other.

This file is the canonical reference for the pipeline (architecture, data
model, safety rules, CLI, testing). It replaces the original project ТЗ
(`docs/synthetic_data/synthetic_data_pipeline_technical_specification.md`),
which described the plan before implementation; all 7 stages of that plan
are now implemented and merged, so this document describes the system as
it actually is.

## Safety rules and non-goals

These are invariants, not suggestions — every layer of the pipeline is
built to enforce them automatically:

- **No real countries, people, or documents.** All country names, codes,
  slugs, personal names, and institutions come from closed fictional word
  lists (`docs/synthetic_data/input_data/world_config.json`) and are
  checked against a deny-list of real country names/codes during
  validation (`core/world_validation.py`).
- **No network calls.** The generator never contacts a government site,
  LLM, news API, or any external service.
  `tests/test_no_network_imports.py` statically forbids importing
  `requests`/`httpx`/`urllib.request`/`socket`/`aiohttp` anywhere in
  `scripts/synthetic_data`, and restricts `psycopg` usage to
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
  `docs/synthetic_data/output_data/` is git-ignored.

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
        +-------------+-------------+-------------------+
        |             |             |                    |
        v             v             v                    v
  canonical JSON   SQL fixture   document renderers    manifest/ZIP
  (json_renderer)  (sql_fixture)  (document_rendering/)  (packaging)
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
`docs/synthetic_data/input_data/world_config.json`. No profile ever makes
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

## Locales

All 15 locales get their own hand-written (not machine-translated) text
blocks, names, and comment templates in
`docs/synthetic_data/input_data/locale_corpus.json` — a fact never changes
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
`scripts/synthetic_data/assets/fonts/NOTICE.md`) — full CJK Noto fonts are
6-18 MB, over this repo's 1 MB/file pre-commit limit, so the CJK ones are
subsetted to the codepoints the corpus actually uses.

## Output layout

```text
docs/synthetic_data/output_data/<dataset_id>/
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
  the 8 synthetic archetype dimensions; filling it with synthetic values
  risks the product invariant that CII's core math is never touched by
  the generator. Left for a separate, owner-approved task.
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
python -m scripts.synthetic_data.cli validate --profile balanced

# Show what would be generated (countries, scenarios) without writing files
python -m scripts.synthetic_data.cli plan --profile crisis --seed 42017

# Generate a full dataset (canonical world + all documents + SQL + package)
python -m scripts.synthetic_data.cli generate --profile balanced --seed 42017

# Generate only canonical JSON + SQL fixture (skip document rendering)
python -m scripts.synthetic_data.cli generate --formats json --seed 42017

# Re-render an existing dataset's documents from its canonical JSON
python -m scripts.synthetic_data.cli render --dataset <dataset_id> --formats pdf,docx,xlsx,txt

# Rebuild manifest + ZIP from files already on disk, without re-rendering
python -m scripts.synthetic_data.cli package --dataset <dataset_id>

# List every dataset under --output-root (id, seed, profile, size, ...)
python -m scripts.synthetic_data.cli list

# Delete old datasets, keeping the N most recent by manifest mtime
python -m scripts.synthetic_data.cli prune --keep-last 5 --confirm

# Print the canonical SyntheticWorld JSON Schema
python -m scripts.synthetic_data.cli schema

# Load / clean up a dataset's SQL fixture against a local database
$env:APP_ENV = "local"
$env:DATABASE_URL = "postgresql://country_atlas:change-me@localhost:5433/country_atlas"
python -m scripts.synthetic_data.cli load-sql --dataset <dataset_id> --confirm
python -m scripts.synthetic_data.cli cleanup-sql --dataset <dataset_id> --confirm
```

Common flags: `--seed` (omit for a random one, always printed),
`--countries` (4 or 5), `--output-root` (default
`docs/synthetic_data/output_data`), `--dry-run` (builds/validates without
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
python -m scripts.synthetic_data.cli --formats pdf,docx,xlsx --count 3 --seed 42017
```

Generates neutral-content sample files unrelated to any country/domain —
used for structural format smoke-testing independent of the world
pipeline. `--formats` accepts `json`, `markdown`, `xlsx`,
`docx-copyable`/`docx-non-copyable`/`docx-mixed`/`docx` (all 3),
`pdf-copyable`/`pdf-non-copyable`/`pdf-mixed`/`pdf` (all 3), or `all`.

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
py -3.12 -m pytest scripts/synthetic_data/tests -q
```

197 tests as of this writing, covering: determinism across seeds/profiles,
referential integrity (every id resolves), the real-country/PII deny-list,
SQL fixture idempotency and cleanup isolation against a live local
Postgres (manual verification — see below), production-guard fail-closed
behavior, artifact structural validity (JSON schema, XLSX sheets,
DOCX/PDF open + copyable/non-copyable/mixed properties), Unicode
round-tripping for all 15 locales, CLI dry-run/error-path behavior, and a
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
python -m scripts.synthetic_data.cli generate --formats json --seed <any>
python -m scripts.synthetic_data.cli load-sql --dataset <dataset_id> --confirm
# ... inspect countries/sources/legal_signals, re-run load-sql to confirm no duplicates ...
python -m scripts.synthetic_data.cli cleanup-sql --dataset <dataset_id> --confirm
# ... confirm only the synthetic countries are gone, argentina/russia/uruguay remain ...
```

## Known limitations / deferred work

- **No translation-testing adapter.** All 15 locales already get
  hand-written (not machine-translated) text, which covers the core goal
  of exercising the full Unicode pipeline. A separate fake-by-default (or
  local-model) adapter that tests the app's own neural-translation layer
  against this synthetic corpus — always storing source/target text,
  provider/version, and a "synthetic, not source of truth" marker — is
  intentionally deferred to the integration tranche; it must never mutate
  canonical facts.
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
formats, the translation-testing adapter, load-volume datasets) should be
scoped as separate, individually-planned tasks rather than folded into
this pipeline silently.
