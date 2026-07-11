# scripts/synthetic_data — quickstart

Generates a self-contained, fully fictional "world" (countries, users,
articles, legal signals, documents, SQL fixtures) for local manual testing.
See `docs/synthetic_data/synthetic_data_pipeline_technical_specification.md`
for the full design; this file only covers the four things you'll do most.

**Generate a world:**

```powershell
python -m scripts.synthetic_data.cli generate --profile balanced --seed 42017
```

Prints the `dataset_id`. Profiles: `balanced`, `crisis`, `optimistic`,
`data_quality`, `moderation`. Omit `--seed` for a random one (always
printed). `--dry-run` builds and validates without writing files.

**See what's on disk:**

```powershell
python -m scripts.synthetic_data.cli list
```

Open `docs/synthetic_data/output_data/<dataset_id>/manifest.json` for every
artifact's path/format/locale/checksum, or `documents/<locale>/...` for the
rendered files directly.

**Load into a local test database, then clean it up:**

```powershell
$env:APP_ENV = "local"
$env:DATABASE_URL = "postgresql://country_atlas:change-me@localhost:5433/country_atlas"
python -m scripts.synthetic_data.cli load-sql --dataset <dataset_id> --confirm
python -m scripts.synthetic_data.cli cleanup-sql --dataset <dataset_id> --confirm
```

Both refuse before connecting if `APP_ENV=production` (or unset). Add
`--dry-run` to preview without connecting.

**Everything else:** `validate`/`plan` (no files written), `render`
(re-render an existing dataset's documents), `package` (rebuild
manifest/ZIP without re-rendering), `prune --keep-last N --confirm` (delete
old datasets), `schema` (dump the canonical world's JSON Schema). Pass
`--json` to any command for machine-readable output, `--quiet` to suppress
routine text.
