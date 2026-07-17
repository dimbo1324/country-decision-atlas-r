# Task: Synthetic data — Stage 2: full local stack on synthetic data

Owner request (verbatim intent): execute Stage 2 of
`docs/_arch_/SYNTHETIC_DATA_PLAN.md` ("Приступай к эпизоду 2").

Branch: `feat/synthetic-data-bootstrap-app`, off up-to-date `main`
(Stages 0+1 already merged).

## Step 1 — mandatory analytical spike (plan requires deferring unclear

mappings to the owner, not inventing them)

- [+] Investigated the real schema: `users` + `user_auth_credentials`
      (migration 001/044), `051_community_threads_v1.sql` (private
      1:1 contact-gated messaging, NOT public articles/comments),
      `migration_board_posts` (045), `user_stories`/`user_story_ratings`
      (003/042), the invariants registry. Read `scripts/create_auth_user.py`
      as the established real-password-hashing pattern, and
      `apps/api/app/services/auth.py`'s actual PBKDF2 scheme (not
      bcrypt/argon2/passlib).
- [+] **Finding**: no clean "public articles + comments" concept exists
      anywhere in the real schema. Surfaced two genuine decision points to
      the owner via AskUserQuestion rather than guessing:
      1. Where (if anywhere) should SyntheticArticle/SyntheticComment map?
         → Owner: nowhere — stay JSON-only (matches the CII-preview
         precedent from Stage 0).
      2. What real RBAC role should synthetic users get, given
         SyntheticUser.role ('author'/'user') is a different concept from
         the real users.role enum? → Owner: all get the ordinary 'user'.
- [+] Both decisions recorded in code comments (`core/sql_fixture.py`),
      README.md, and the plan's Stage 2 status note — not just in chat.

## Implementation

- [+] `core/sql_fixture.py`: `UserFixtureIds`, `user_fixture_ids()`,
      `_user_metadata()` (invariant #26 marking), users +
      user_auth_credentials INSERT/ON CONFLICT blocks in
      `build_seed_sql()`, matching DELETE blocks (credentials before
      users) in `build_cleanup_sql()`.
- [+] Real password hashing, reusing the app's own PBKDF2
      algorithm/iteration constants (`_import_real_pbkdf2_params()`,
      lazy cross-package import into `apps/api`, same pattern as
      `scripts/create_auth_user.py`) — **not** the real `hash_password()`
      function itself, which salts randomly and would have broken this
      pipeline's "same seed -> byte-for-byte identical world" guarantee
      (caught by `test_seed_sql_is_deterministic_for_the_same_world`
      failing on the first attempt). Fixed with a deterministic
      per-user salt derived from `dataset_id` + `user_id`.
- [+] `cli.py`: `bootstrap-app` command (`_run_bootstrap_app`,
      `_run_subprocess_step` helper) — chains `apply_migrations.py`
      (subprocess) -> `load-sql` (in-process, reuses `execute_sql_file`)
      -> `rebuild_search_index.py --all` (subprocess) ->
      `bootstrap_runtime_read_models.py` (subprocess). Same safety gate
      as `load-sql`: `--confirm` required, `ensure_not_production()`
      checked before anything runs, `--dry-run` prints the chain without
      touching anything.

## Bugs found (one fixed, one found-but-deliberately-not-fixed)

- [+] **Fixed** (my own new code): `_hash_synthetic_password()`'s first
      version called the real `hash_password()` directly, which salts
      with `secrets.token_hex()` — non-deterministic across re-runs of
      the same seed. Caught immediately by the existing
      `test_seed_sql_is_deterministic_for_the_same_world` test.
- [-] **Found, NOT fixed (out of scope)**: live e2e testing surfaced a
      real, pre-existing bug in `country_fixture_ids()` (Stage 0/1 code,
      not Stage 2's): `countries.iso2`/`iso3` are derived only from a
      country's index within its own dataset, not `dataset_id` — every
      dataset's first country gets `iso2='XA'` regardless of seed.
      `countries.iso2 CHAR(2) UNIQUE` means loading a *second* dataset
      without `cleanup-sql`-ing the first fails with `UniqueViolation`.
      Reproduced live. Worked around for this task's own verification by
      cleaning up between datasets (the documented usage pattern anyway).
      Not fixed here per scope discipline (pre-existing code outside
      Stage 2, and a real fix is constrained by `CHAR(2)` only having 26
      safe ISO-reserved codes — needs a deliberately-scoped follow-up).
      Recorded loudly in `utils/synthetic_data/README.md`'s "Known
      limitations" (priority: data-integrity) and the plan's Stage 2
      status note, not silently.

## Verification

- [+] 9 new tests in `test_sql_fixture.py`: user fixture id stability/
      uniqueness, every user gets `role='user'`, every password_hash
      verifies against the real app's `verify_password()` (imported
      live from `apps/api`) and rejects a wrong password, metadata marks
      every row synthetic (invariant #26), reserved email domain,
      cleanup deletes credentials before users, cleanup targets exactly
      this dataset's user ids, cleanup never cross-deletes another
      dataset's users. Also updated 2 pre-existing tests whose hardcoded
      counts became stale once users joined the fixture (`ON CONFLICT`
      count, real-role regex) — legitimate refactor-follows-the-code
      updates, not weakened assertions.
- [+] **Live e2e verification against a real stack** (the plan's own
      step 4 requirement), not just unit tests:
      `docker compose up -d postgres redis` + `docker compose up --build
      -d api`, `APP_ENV=local apply_migrations.py`, generated a dataset,
      `load-sql`, then a real `POST /api/v1/auth/login` with a synthetic
      user's email + `SYNTHETIC_USER_PASSWORD` → HTTP 200, real session
      token, `role: "user"` confirmed in the response. Wrong password →
      401. Ran `cleanup-sql`, same login → 401 again (user genuinely
      gone). Ran the *full* `bootstrap-app` chain end-to-end on a second
      dataset (hit and worked around the iso2 bug above along the way) →
      login worked for that dataset's user too. Cleaned up both datasets
      and stopped the containers afterward.
- [+] `python -m ruff check/format --check utils/synthetic_data` — clean,
      120 files.
- [+] `python -m mypy utils/synthetic_data` — clean, 120 files.
- [+] `py -3.12 -m pytest utils/synthetic_data/tests -q` — 350 tests
      (341 pre-existing + 9 new), all green, zero regressions.
- [ ] Full project quality gate (`python dev_tools_scripts_runner.py`,
      the OTHER 78+ checks: frontend, notifier, migrations-as-a-whole)
      was **not** re-run — this task's live verification already
      exercised the exact Docker/migrations/API-login path relevant to
      what changed; re-running the full ~10-minute gate for the
      unrelated 90% of checks would not add signal for this diff.
      Flagged honestly, matching the pattern from prior tasks this
      session.

## Documentation

- [+] `utils/synthetic_data/README.md`: new "Users (Stage 2)" subsection
      under "SQL fixtures and database safety" (both owner decisions,
      the deterministic-salt design note, the live-verification
      summary), `bootstrap-app` added to the CLI command list and the
      manual-verification walkthrough, `iso2`/`iso3` bug added to "Known
      limitations" (was silently absent before), stale "4 tables"/"never
      collide" claims corrected to reflect what's now demonstrated true.
- [+] `docs/_arch_/SYNTHETIC_DATA_PLAN.md`: Stage 2 checked off in the
      DoD section with a `**Статус.**` note (what shipped, the two owner
      decisions, the live-verification results, the found-not-fixed bug
      with a pointer to the README for details).

## Completion

- [+] Fill this checklist (`+`/`-`).
- [+] Final report (in chat).
