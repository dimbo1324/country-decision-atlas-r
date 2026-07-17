# Task: Synthetic data — Stage 1: Synthetic Web Environment

Owner request (verbatim intent): execute Stage 1 of
`docs/_arch_/SYNTHETIC_DATA_PLAN.md` in full, without stopping to ask at
each step, working carefully and double-checking along the way ("делай не
спеша, перепроверяй себя").

Branch: `feat/synthetic-web-environment`, off `refactor/synthetic-data-relocate`
(Stage 0's branch — Stage 1 needs `utils/synthetic_data/` to already exist,
so it couldn't branch from `main` directly until Stage 0 merges).

## Investigation before writing any code

- [+] Read `core/world_models.py`, `core/seed.py`, `core/world_generator.py`,
      `core/manifest.py`, `core/dataset_packager.py`, `core/document_formats.py`,
      `core/document_rendering/context.py`, `core/artifact_validation.py`,
      `mock_server/__main__.py` + `app.py`, `core/world_input.py`,
      `core/world_validation.py`, `core/dashboard.py`, `cli.py` (argument
      parser, `_run_world` dispatch, `_render_and_package`).
- [+] **Critical finding, changed the plan**: `core/world_validation.py`
      hard-requires `SyntheticSource.url` to start with `synthetic://` —
      not a placeholder waiting for a real URL, an enforced invariant.
      A literal reading of the plan ("`SyntheticSource.url` начинает
      указывать на конкретную страницу") would have broken this invariant,
      `world_generator.py`'s byte-for-byte determinism test, and the
      committed `tests/fixtures/smoke_world_snapshot.json` golden fixture.
      Redesigned before writing code: a separate `source_id -> "/sites/..."`
      mapping (`web/graph.py`'s `source_page_urls()`,
      `websites/source_pages.json`) instead of mutating the field.
- [+] Confirmed FastAPI/uvicorn are already project dependencies (used by
      `mock_server`) — chose them for `web/server.py` over stdlib
      `http.server` (the plan left this open) for `Content-Disposition`,
      redirects, and status codes without hand-rolling HTTP.

## Implementation

- [+] `input_data/web_config.json`: 4 site archetypes (gov_portal,
      news_portal, blog, wiki), cross-site link count range, per-kind
      anomaly ratios, huge-page padding size.
- [+] `web/models.py`: `LinkEdge`, `PageAnomaly`, `SitePage`,
      `SyntheticSite`, `WebGraph` (Pydantic frozen models, matching
      `core/world_models.py`'s own style).
- [+] `web/archetypes.py`: `load_web_config()` with the same
      fail-fast-with-a-specific-path validation style as `world_input.py`.
- [+] `web/graph.py`: `build_web_graph()` — one site per country
      (archetype chosen from `seed_factory.rng()`), grounded pages for
      every source/article/legal-signal the archetype publishes (never
      invents an entity), home+about pages, cross-site links. Plus
      `source_page_urls()` (see the invariant finding above).
- [+] `web/anomalies.py`: `assign_anomalies()` — one seeded coin flip per
      site per anomaly kind; `not_found`/`server_error` never get a
      rendered file (server answers from the graph itself).
- [+] `web/html_renderer.py` + `web/assets.py`: stdlib-only rendering
      (f-strings + `html.escape`, no jinja2 — matches `core/dashboard.py`'s
      existing pattern), inline CSS/favicon/placeholder-image SVG (no
      static-asset HTTP route needed).
- [+] `web/validation.py`: link resolution, "broken"-marked links must NOT
      resolve, download links must match a real rendered document, every
      non-`not_found`/`server_error` page must have a file on disk.
- [+] `web/server.py`: one FastAPI app, `/sites/<path>` (real 404/500/302
      per anomaly kind, backed by `graph.json`) and `/files/<path>`
      (`Content-Disposition: attachment`, path-traversal guarded).
- [+] `cli.py`: `--formats web` (recognized, deliberately excluded from
      `all`), `render-web` + `serve` commands, `--host`/`--port` flags,
      `_render_website()` shared helper (used by both `generate --formats
      web` and standalone `render-web`, so they can't drift).
- [+] `core/dataset_packager.py`: `package_dataset()` gained an
      `extra_files` parameter so website artifacts fold into the existing
      manifest/ZIP machinery without inventing a parallel one.

## Bugs found by my own tests (fixed, not ignored)

- [+] `web/graph.py`'s validation for "broken" links initially checked
      against *every* graph page, including `not_found`/`server_error`
      pages themselves (which legitimately have no file) — falsely
      flagged every intentional 404/500 link as "resolves but shouldn't."
      Fixed: a separate `servable_page_paths` set excludes those two kinds.
- [+] `_render_redirect_stub()` (the meta-refresh HTML for `redirect`
      anomalies) didn't carry the `FICTIONAL_NOTICE` marker every other
      real page has — caught by `test_every_rendered_page_carries_the_fictional_notice`.
      Fixed. (`empty` anomaly pages are a deliberate, documented exception
      — carrying a notice would defeat the point of being empty.)
- [+] Download link paths were first built as page-relative
      (`../files/...`), which breaks depending on how deep the linking
      page sits. Redesigned as server-root-absolute (`/files/...`)
      before any renderer code was written, once the depth-counting math
      turned out genuinely fiddly — simpler and correct regardless of
      page depth.

## Verification

- [+] Manual, incremental verification at every layer as it was built
      (not only at the end): graph determinism across 6 seeds, all 7
      anomaly kinds confirmed appearing across a seed range, end-to-end
      HTML rendering + byte-level checks (broken_encoding genuinely fails
      UTF-8 decode, duplicate byte-identical, huge measurably larger),
      live `TestClient` HTTP checks for every anomaly's status code
      (404/500/302/200), a real download with `Content-Disposition`
      verified via actual PDF documents, path-traversal attempt on
      `/files/` rejected.
- [+] Full CLI path exercised for real (not just unit-level): `generate
      --formats web`, `render --formats pdf` then `render-web` picking up
      the newly-rendered PDFs for download links, and `serve` run as an
      actual background process with real `curl` HTTP requests against
      `http://127.0.0.1:18080` (home page 200, unknown page 404, PDF
      download with attachment header) — then cleanly killed
      (`taskkill`), confirmed no lingering process on the port afterward.
- [+] 39 new tests (`test_web_archetypes.py`, `test_web_graph.py`,
      `test_web_html_renderer.py`, `test_web_validation.py`,
      `test_web_server.py`, `test_web_cli.py`) — determinism, structural
      correctness, mutation tests for validation.py (dangling link, a
      broken-marked link that actually resolves, a missing file, a
      download link with no matching document), full HTTP-status
      coverage per anomaly kind, CLI success/dry-run/error paths.
- [+] `python -m ruff check utils/synthetic_data` — clean (fixed 10
      issues along the way: import ordering after the module rename
      pattern seen before, `RUF005`/`RUF043`/`SIM102`/`ARG001`).
- [+] `python -m ruff format --check utils/synthetic_data` — clean.
- [+] `python -m mypy utils/synthetic_data` — clean, 120 source files,
      zero issues (fixed a `del` on a `dict[str, object]`-typed value in
      a test that needed an explicit `isinstance` narrow).
- [+] `py -3.12 -m pytest utils/synthetic_data/tests -q` — 341 tests,
      all green (302 pre-existing + 39 new), confirming zero regressions
      in the pre-existing suite.
- [ ] Full project quality gate (`python dev_tools_scripts_runner.py`,
      Docker stack + E2E) was **not** re-run end-to-end — this task only
      touches files inside `utils/synthetic_data/` (plus its own docs),
      already covered by the package's dedicated pytest step and the
      checks above; re-running the ~10-minute Docker/E2E gate for a
      change with no Docker/API/frontend surface would not add signal.
      Flagged honestly rather than silently claimed.

## Documentation

- [+] `utils/synthetic_data/README.md`: new "Synthetic Web Environment"
      section (architecture diagram, anomaly table, download-link
      behavior, the `SyntheticSource.url` invariant explanation, CLI
      examples), updated architecture diagram/layer table, `Output
      layout` tree, CLI command list, test count (302 -> 341).
- [+] `docs/_arch_/SYNTHETIC_DATA_PLAN.md`: Stage 0 and Stage 1 both
      checked off in the plan's own DoD section (Stage 0 had shipped in
      the prior task but was never marked done); a `**Статус.**` line
      under Stage 1 recording what shipped and the invariant-driven
      design deviation.
- [+] `docs/_arch_/01_Продукт/02_Текущее_состояние_системы.md` §7.3:
      one sentence added noting the web layer now exists, its shape, and
      the CLI commands.

## Completion

- [+] Fill this checklist (`+`/`-`).
- [+] Final report (in chat).
