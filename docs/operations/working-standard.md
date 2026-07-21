# Project Working Standard

Country Decision Atlas's unified working standard. Applies to every development task. This is a standard, not a code block: it fixes how work is done — branch order, checks, implementation layers, prohibitions, and the report format — so that any developer or AI assistant works predictably and consistently.

Updated 2026-07-04 when the project's baseline was reset: references to prior episodes were removed (the current plan is [../product/roadmap.md](../product/roadmap.md)), architectural invariants were moved into their own registry ([../architecture/invariants.md](../architecture/invariants.md)), and the quality gate's composition was brought in line with the current toolchain.

---

## 1. Git workflow and discipline

Every task starts only from an up-to-date `main`:

```
git checkout main
git pull --ff-only origin main
git checkout -b <branch>
```

Mandatory rules:

- Never work directly on `main` (exception — documentation tasks by the owner's direct instruction).
- The branch name matches the task: `feat/…`, `fix/…`, `chore/…`, `refactor/…`, `test/…`, `docs/…`.
- Commit each logically complete sub-task; the message explains "why," not just "what."
- Targeted checks after major stages; the full quality gate — **before** merging.
- Merge only fast-forward (`git merge --ff-only`), only after a green gate.
- Push to `origin/main` — only with the owner's explicit confirmation within the task.
- The final state lives on `main`; the finished branch is deleted.

Task history lives in git history and final reports (section 6); no separate log file is kept.

---

## 2. The unified quality gate

The main way to run it — the orchestrator at the repo root:

```
python dev_tools_scripts_runner.py --profile full     # a full run (Docker, E2E)
python dev_tools_scripts_runner.py --profile quick    # a fast local slice
python dev_tools_scripts_runner.py --doctor           # read-only environment diagnostics
```

The equivalent manual set (also what CI runs):

```
python -m pytest
python -m mypy apps packages scripts tests
python -m ruff check apps packages scripts tests
python -m ruff format --check apps packages scripts tests
python -m sqlfluff lint database --dialect postgres
pnpm quality
pnpm web:mvp:check
python -m pre_commit run --all-files
```

`ruff format --check` specifically — before a merge, formatting needs to be proven already clean. If `pre-commit` changed anything, those changes get reviewed and committed. `pnpm web:mvp:check` needs a running stack (`docker compose up -d api`) with migrations applied.

---

## 3. Layer implementation order

Code is written strictly top-down. This is a backend/data-first project: data and the contract first, then the UI.

1. `database/migrations/NNN_*.sql` (the next number; a header comment stating its purpose)
2. the repository — data access/SQL only
3. the service — business logic (a large domain becomes a package right away, see `CLAUDE.md`)
4. the schema — Pydantic v2 contracts
5. the api/v1 router (thin) + `main.py`'s `include_router` for a new router
6. `contracts/openapi.yaml` → `pnpm contracts:generate` → verify the generated TypeScript
7. a thin frontend
8. backend tests (unit, API, migration, data quality)
9. E2E tests

Additionally, for every new domain: a feature flag (off until acceptance), a `_append_<domain>_checks` data-quality module, events only through the outbox. The full new-domain checklist is in the roadmap, part III.

---

## 4. Hard prohibitions

Always in effect:

- no comments in code, docstrings, or inline comments (exceptions: a one-line docstring in a test file stating what it checks; a migration header comment; cases where the "why" can't be derived from the code);
- no new READMEs / `.md` / `.txt` files in the working codebase;
- no changes under `docs/` as part of product tasks — documentation edits happen only in dedicated documentation tasks, by the owner's instruction;
- never touch CII math, scenario weights, or the decision-engine scoring (see the invariants registry);
- never weaken data quality or mask problems with fake data;
- migrations are sequential and idempotent only, sqlfluff-clean; applied migration files are never renamed or edited (checksum-tracked);
- travel documents, bookings, and scans of user documents are never stored.

---

## 5. Architecture invariants

The full registry: [../architecture/invariants.md](../architecture/invariants.md). Violating any entry there blocks a merge regardless of a green gate.

---

## 6. The final-report format

After every task, the person (or assistant) who did the work gives a report in this unified format:

1. Branch workflow — the starting branch, the feature branch, the final branch, whether anything was pushed.
2. Implemented — what was done.
3. Database — migration changes.
4. Backend — which layers were touched.
5. API / Contracts — OpenAPI and generated-TS changes.
6. Frontend — which elements were touched.
7. Tests — tests added.
8. Quality gates — the results of every check.
9. Data-quality impact — the effect on data quality.
10. Not changed — what was deliberately left untouched.
11. Risks / notes — risks and notes.
12. Final git state — the final status.
