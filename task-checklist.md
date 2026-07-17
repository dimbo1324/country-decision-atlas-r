# Task: Total project check + fix errors on the spot (main)

Owner request (verbatim intent): "теперь сделай тотльную и плную проверку
самого проекта, скриптов и т.д. ошипки устраняй прямо на месте в ветке main."
(Do a total/full check of the project and scripts; fix errors directly on
the spot on the `main` branch.) Working directly on `main`, no new branch,
per explicit owner instruction.

## Full project quality gate

- [+] Ran `python dev_tools_scripts_runner.py full-check` (full gate: static
      checks, pytest main + `utils/synthetic_data`, `pnpm quality`, Go
      vet/test, Docker stack + migrations + runtime smokes, Playwright E2E,
      pre-commit).
- [+] Result: 80 OK, 1 WARN, 1 FAIL, 1 SKIP, ~11.7 min.
- [+] WARN: stale `.tmp/full-check` cache dir — confirmed gitignored
      (`.gitignore` line 199), removed (`rm -rf .tmp/full-check`).
- [+] FAIL: `go test -race` — `-race requires cgo; enable cgo by setting
      CGO_ENABLED=1` (no C compiler on this Windows machine). Confirmed via
      transcript grep this is the exact same, already-known limitation the
      owner explicitly accepted in an earlier session (real `-race` gate is
      CI's `ubuntu-latest`). Not a regression — no action taken.
- [+] `pytest (utils/synthetic_data)` passed (confirms the `arabic-reshaper`
      dependency fix from earlier in this session still holds).

## Bug found during the gate review and fixed on the spot

- [+] Revisited the pre-existing, previously-documented-but-deliberately-
      deferred bug from Stage 2's live verification: `country_fixture_ids()`
      (Stage 0/1 code) derived `countries.iso2`/`iso3` only from a country's
      index within its own dataset, not `dataset_id` — every dataset's Nth
      country got the identical code, so a second dataset loaded without
      `cleanup-sql`-ing the first always failed with `UniqueViolation` on
      `countries_iso2_key`.
- [+] Fixed in `utils/synthetic_data/core/sql_fixture.py`: added
      `_iso2_letter_permutation()` / `_iso3_suffix_permutation()`, each a
      `dataset_id`-seeded deterministic shuffle (`hashlib.sha256` ->
      `random.Random(seed).shuffle`) of the 26 safe iso2 letters / 676 safe
      iso3 suffixes. `country_fixture_ids()` now indexes into the
      per-dataset permutation instead of a fixed `chr(ord("A") + index)`
      mapping. Guarantees zero collision within one dataset; reduces (does
      not eliminate — `CHAR(2)` only has 26 safe combinations total) cross-
      dataset collision risk.
- [+] Tests: extended `test_country_fixture_ids_use_reserved_iso_codes()` to
      also assert iso3 uniqueness; added
      `test_different_datasets_usually_get_different_iso_codes()` (explicit
      regression test for the found bug, seeds 1-20) and
      `test_country_fixture_ids_iso_codes_are_stable_for_the_same_dataset()`
      (determinism check). `py -3.12 -m pytest utils/synthetic_data/tests -q`
      — all tests green. `ruff check`/`format --check` and `mypy` on
      `utils/synthetic_data` — clean.
- [+] **Live re-verification against a real stack**: generated two datasets
      (seeds 5001, 5002), loaded both via `load-sql` back-to-back with NO
      `cleanup-sql` in between — the exact scenario that previously failed.
      Both loads succeeded this time.
- [+] Docker containers and temp test artifacts from the live verification
      cleaned up afterward.

## Documentation

- [+] `utils/synthetic_data/README.md`: "Known limitations" bullet rewritten
      (bug -> fix -> live re-verification -> honest remaining caveat about
      the 26-code ceiling); "Guarantees" bullet in the SQL-fixtures section
      updated to match.
- [+] `docs/_arch_/SYNTHETIC_DATA_PLAN.md`: Stage 2 status note's
      "Найден и НЕ исправлен" paragraph rewritten to "Найден и позже
      исправлен" with the fix approach and re-verification result.

## Completion

- [+] Fill this checklist (`+`/`-`).
- [+] Commit the fix + docs directly on `main` (owner explicitly authorized
      working on `main` for this task).
- [ ] Push to `origin/main` — not yet requested separately for this specific
      commit; will report readiness and let the owner decide, matching the
      pattern where pushes have been requested explicitly and separately
      from the "do the work" instruction each time so far this session.
- [+] Final report (in chat).
