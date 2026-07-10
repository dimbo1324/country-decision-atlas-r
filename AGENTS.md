<!--
GENERATED FILE - DO NOT EDIT.
Source of truth: .ai/universal/*.md and .ai/project/*.md.
Edit a module, then run: python dev_tools_scripts_runner.py sync-agents
-->

# Country Decision Atlas - working notes for Codex

This file is the Codex entry point. It is assembled from the shared rule
modules in `.ai/` so Codex and Claude Code always follow identical rules.
Later sections override earlier ones; an explicit owner instruction in the
current conversation overrides everything.


---

<!-- module: .ai/universal/01-workflow.md -->

# Workflow: Git, Branches, Commits

Purpose: every task follows one predictable git cycle. No exceptions without
an explicit owner instruction in the current conversation.

## Branch discipline

- NEVER develop directly on `main`.
- Start every task from up-to-date `main`:
  `git checkout main` → `git pull --ff-only origin main` → `git checkout -b <branch>`.
- Branch name format: `type/short-task-description`
  (types: `feat`, `fix`, `refactor`, `test`, `chore`, `docs`, `ci`, `perf`, `security`).
- Uninformative branch names (`test`, `fix`, `work`, `final`, `new`) are forbidden.
- Merge into `main` only fast-forward (`git merge --ff-only`) and only after
  the project's full quality gate is green.
- Push to `origin/main` only when the owner explicitly asked for a
  publish/push within the current task. Work-in-progress branch pushes are
  allowed (e.g. to publish the task checklist before starting work).
- Delete the task branch after it is merged.

## Commits

- Message format: `type: short description of what and why`.
- One commit = one logically complete unit. Do not mix a bug fix, a refactor,
  formatting, and new features in a single commit unless they are one
  inseparable task.
- Forbidden messages: `fix`, `update`, `wip`, `changes`, `final`, `123`.

## Quality gate before merge

- Run the project's checks (see the project commands module) before merging.
- If mandatory checks fail, merging into `main` is forbidden until fixed or
  the owner explicitly decides otherwise.
- Before merging, self-review the diff: changes match the task, no stray
  files, no debug leftovers, no secrets, no accidental unrelated edits.

When unsure whether an action counts as "explicitly requested": ask, or stop
after the branch commit and report instead of pushing.

---

<!-- module: .ai/universal/02-task-checklist.md -->

# Task Checklist and Definition of Done

Purpose: every task is planned before it starts and honestly accounted for
after it ends, in a file any reviewer can read without the conversation.

## task-checklist.md protocol

A file named `task-checklist.md` lives in the repository root and is always
tracked by git (never in `.gitignore`).

Before starting a task:

1. Clear or recreate `task-checklist.md` for the new task.
2. Write the main stages, checks, and expected outcomes as `[ ]` items,
   grouped into short sections (preparation / implementation / verification /
   completion). Moderate detail — stages, not keystrokes.
3. Commit and push the checklist BEFORE doing the main work.

After finishing the task:

4. Mark every item: `+` done, `-` not done or partially done.
5. Commit the filled checklist together with the completed work.
6. Never hide unfinished items — a `-` with an honest note is correct;
   a silently ignored item is a violation.

## Definition of Done

A task is complete only when ALL of the following hold:

- code written and matching the task, without unrequested scope
- code formatted; lint/type checks pass
- tests added or updated where reasonable; existing tests pass
- project builds; no obvious errors in logs
- no secrets, no temp files, no accidental changes in unrelated files
- architecture docs updated if the task changed architecture
- task checklist filled with `+`/`-`
- final report written

## Final report

The final report is ALWAYS the last step of a task. It states: what was done;
which files/areas changed; which checks ran and their results; dependency,
API, DB, or config changes; security/performance/compatibility risks; and —
explicitly and honestly — anything that was not done or failed.

---

<!-- module: .ai/universal/03-scope-and-code-style.md -->

# Scope Control and Code Style

Purpose: change only what the task requires, and keep code readable without
decoration.

## Minimal changes

- Touch only what the current task needs. Forbidden without necessity:
  mass-reformatting other files, renaming things outside the task, changing
  architecture "while at it", rewriting working code without cause, changing
  UI when the task is not frontend, deleting existing functionality without
  a direct requirement.
- If you discover an unrelated problem, record it separately (report it,
  or file it per the project's process) — do not mix it into the current diff.
- Do not create new documentation (README, .md, .txt) unless directly
  required by the task. Exception: the project's designated architecture
  docs area, which must be kept current when architecture changes.

## Comments

- No comments unless genuinely necessary. Code must be clear through
  structure and naming.
- A comment is allowed only when the task demands it or when important logic
  stays non-obvious even with good naming. It must explain the non-obvious
  "why", never restate the code.
- Stale, false, or misleading comments are forbidden. No docstrings that
  merely repeat a function name.

## File size

- Regular code files: keep under ~1000 lines; split by meaning
  (API / services / repositories / schemas / config / helpers / UI) when
  approaching the limit. Projects may set a stricter limit — the stricter
  limit wins.
- Application entry points (`main`-type files): under ~100 lines; extract
  configuration, startup, route registration, service init into modules.
- Exemptions: test files, developer-tool scripts, and any files the project
  explicitly exempts.

## Frontend restraint

- No visual polish (styling, animations, decorative elements, redesign)
  unless the task is explicitly about frontend appearance.
- When a task needs an interface, build the minimum that exercises the
  business logic correctly.
- Never change visual style, interface structure, component behavior, or
  user flows without a direct requirement.

---

<!-- module: .ai/universal/04-architecture-boundaries.md -->

# Architecture Boundaries, Workarounds, Tech Debt

Purpose: respect the project's layering; make every shortcut visible.

## Boundaries

- Follow the project's existing architecture. Forbidden: business logic in
  UI or controllers when a service layer exists; SQL in API routes when a
  repository layer exists; bypassing existing services/abstractions without
  cause; circular module dependencies; dumping unrelated logic into
  catch-all files.
- If the architecture genuinely blocks the task, do not hack around it —
  propose a proper structural change and reflect it in the architecture
  docs once approved.

## Temporary solutions

- Workarounds are allowed only exceptionally, and every one must be recorded
  explicitly: why it exists, where it lives, its limits and risks, and when
  it must be replaced.
- Hidden workarounds are forbidden. Do not scatter uncontrolled
  `TODO`/`FIXME` marks; important debt gets a task or an entry in the
  project's tracking process.

## Tech debt

- Debt found during a task that cannot be fixed now is recorded explicitly
  (in the final report at minimum), never disguised as a normal solution.
- Debt touching security, data integrity, performance, or stability is
  priority debt — call it out loudly.

---

<!-- module: .ai/universal/05-security-and-secrets.md -->

# Security, Secrets, Dependencies, Portability

Purpose: nothing sensitive in the repo; every change safe within its area;
the project runs on any machine.

## Secrets — absolute ban

- NEVER put in code, git, tests, docs, or examples: passwords, API keys,
  tokens, private keys, real credentials, cookies, production `.env`,
  or personal user data.
- Secrets live only in `.env` (untracked), environment variables, secret
  managers, or CI/CD secrets. The repo may contain only a safe
  `.env.example`.
- A secret that ever reached git is compromised: rotate it; deleting the
  line in a new commit is not enough.

## Security in every task

Check within the area you touch: authorization and access rights, input
validation, SQL injection, XSS, CSRF where applicable, unsafe redirects,
file uploads, personal data handling, public endpoints, token storage and
transport, and access to admin functions. Security is part of every task,
not a future task.

## Dependencies

- No new dependency without justification: what for, can it be done without,
  is it maintained, known vulnerabilities, stack compatibility, does it
  duplicate an existing dependency, is it too heavy for the need.
- Never add a heavy library for one small function.
- After changing dependencies: update the lock file and verify the build.
- A new production dependency must be named in the final report.

## Portability

- No machine-specific values in code: local absolute paths, usernames,
  IDE settings, unconfigured local ports, anything environment-dependent.
  Environment-dependent values go to configuration.
- The project must remain runnable by someone else using the project's
  documented tools.

---

<!-- module: .ai/universal/06-quality-and-testing.md -->

# Quality: Tests, Errors, Data, Contracts, Performance

Purpose: changes are verified, honest about failure, and safe to release.

## Tests

- Cover new or changed code where reasonable: the happy path, validation
  errors, edge cases, access rights, repository/service behavior, API
  responses, and regressions for fixed bugs.
- NEVER delete, disable, or weaken tests just to make a build green.
- If tests were not added, say why in the final report.
- Prefer the project's designated check runner over ad-hoc command
  sequences, and keep that runner updated when the task adds an important
  new part of the system.

## Errors and logging

- Handle errors explicitly. Forbidden: silently swallowed errors, empty
  catch/except blocks, debug logs left after the task, secrets or personal
  data in logs, `console.log`-style debugging instead of real handling.
- Logs must say where it broke, which component, what context matters, and
  how critical it is. Useful, not noisy.

## Database migrations

- Schema changes happen ONLY through migrations.
- Never edit or rename an already-applied migration; never delete migrations
  without a separate decision; never make irreversible changes without risk
  analysis; never hand-edit production data without an agreed plan.
- Verify each migration on a clean database, on an existing database when
  applicable, and together with the code that uses the new structure.

## API contracts

- When a task changes an API, update the contract and generated types.
- Never silently change field names, data types, response structure, error
  codes, parameter requiredness, endpoint behavior, pagination, or filters.
- Any breaking change must be named explicitly in the final report.

## Performance

- No premature optimization, but no obviously wasteful patterns: N+1
  queries, heavy per-request computation, render loops, unpaginated large
  reads, redundant network calls, blocking operations in hot paths.
- If a change may affect performance, say so in the final report.

## Releases and feature flags

- Every change should be revertible; for risky changes plan the rollback
  before merging.
- Large new features ship behind a feature flag where the project supports
  them; unfinished functionality must not be reachable by accident; stale
  flags get removed after stabilization.

---

<!-- module: .ai/universal/07-multi-assistant.md -->

# Multi-Assistant Collaboration

Purpose: several AI assistants (and humans) work on this repo in separate
sessions; git is the coordination surface and the rule modules are shared.

## Coordination through git

- Before non-trivial work, check `git log --oneline -10` and
  `git status --short --branch`: recent commits may be another assistant's
  finished work — not yours to redo or second-guess.
- Never rewrite history on another assistant's in-flight branch. Build on
  top of it or ask first.
- Keep commits attributable: include the assistant identity trailer the
  project already uses (see recent `git log` for the convention).

## Shared rule modules

- All assistants obey the same rules from `.ai/universal/` and
  `.ai/project/`. There is exactly one source of truth.
- `CLAUDE.md` imports the modules natively; `AGENTS.md` is GENERATED from
  them. Never hand-edit `AGENTS.md`; edit the module and regenerate
  (see the project commands module for the sync command).
- When a task changes shared behavior (workflow, gates, style, guardrails),
  change the module once — both assistants pick it up. Mirror-maintained
  per-assistant files (`.claude/` skills/agents vs their Codex equivalents)
  still need the same edit on both sides in the same task.

## Session hygiene for any model

- Re-read plans and rule files from disk instead of trusting memory of a
  previous session — files change between sessions.
- When context is shaky or the task is large, restate the task's acceptance
  criteria in the checklist before coding, and verify against files, not
  recollection.
- If two rules appear to conflict: the project module wins over the
  universal module; an explicit owner instruction in the current
  conversation wins over both. Say out loud which rule you chose and why.

---

<!-- module: .ai/project/10-project-map.md -->

# Project: Country Decision Atlas

Full-stack decision-support platform that helps a person choose a country for
a specific goal: relocation, residency/citizenship, remote work, low-budget
living, business, or safety. Output is structured, sourced, confidence-rated.
It is NOT a country-ranking blog or listicle product.

## Repository map

- `apps/api` — FastAPI backend. Routers thin in `app/api/v1/*`; business
  logic in `app/services/*`; SQL only in `app/repositories/*`.
- `apps/web` — Next.js frontend.
- `apps/notifier` — Go gRPC notifier service (Kafka consumer → Telegram;
  Mongo for derived state).
- `contracts/openapi.yaml` — source contract; `packages/contracts/generated`
  is generated by `pnpm contracts:generate` — never hand-edit.
- `database/migrations` — numbered SQL migrations tracked by filename +
  checksum in `schema_migrations`.
- `scripts/dev_tools` + `dev_tools_scripts_runner.py` — developer
  automation; the main way to verify the project.
- `docs/_arch_` — architecture, product model, and plan (Russian). Keep
  current when architecture changes.
- `.ai/` — assistant rule modules (this system).
- `.claude/`, `.codex/` — per-assistant workspaces (agents, skills, config),
  maintained as mirrors of each other.

## Documentation policy (hard rules)

- `docs/_ideas_and_concepts_/` — owner's private folder. NEVER read, edit,
  delete, or use it. It stays in git untouched.
- New documentation files are created only on direct request. Exception:
  `docs/_arch_` must be kept accurate when code changes affect architecture,
  structure, or the plan.

## Product guardrails

- Decision-support with sources, confidence, freshness, transparent
  tradeoffs — never a generic ranking product.
- Prefer read-model overlays and existing domain services to per-field
  branching.
- When unsure about domain intent, read `docs/_arch_` before coding.
- The invariants registry (`docs/_arch_/02_План/02_Реестр_инвариантов.md`)
  is binding: core scoring math is locked, derived metrics never mix into
  CII, reputation never auto-grants rights, moderator access to private data
  only via a filed report, money never buys rights or ranking.
- Autonomous development mode: no real external service integrations until
  the integration tranche; everything must work offline through
  fake-by-default provider seams (e.g. `TELEGRAM_MODE=fake`).

---

<!-- module: .ai/project/11-commands.md -->

# Project Commands and Quality Gates

All commands run from the repository root (Windows, PowerShell or Git Bash).

## Main entry point — dev tools runner

```powershell
python dev_tools_scripts_runner.py                  # full quality gate (default)
python dev_tools_scripts_runner.py --profile quick  # quick gate (pre-push minimum)
python dev_tools_scripts_runner.py format-code      # auto-format Python/frontend/Go
python dev_tools_scripts_runner.py --doctor         # read-only diagnostics
python dev_tools_scripts_runner.py sync-agents      # regenerate AGENTS.md from .ai/
python dev_tools_scripts_runner.py sync-agents --check  # verify AGENTS.md is in sync
python dev_tools_scripts_runner.py dispatch-trip-reminders  # due reminders -> outbox
python dev_tools_scripts_runner.py ship-main --message "type: why"  # guided publish
```

`ship-main` is only for an explicitly requested publish of already-validated
work; the default path is branch → gate → ff-merge → push.

## Direct commands (when targeting one layer)

```powershell
python -m pytest <targeted tests> -q
python -m ruff check apps packages scripts tests
python -m ruff format --check apps packages scripts tests
python -m mypy apps packages scripts tests
python -m sqlfluff lint database --dialect postgres
corepack pnpm@9.12.0 install --frozen-lockfile
corepack pnpm@9.12.0 contracts:generate
corepack pnpm@9.12.0 --filter @country-decision-atlas/web typecheck
corepack pnpm@9.12.0 --filter @country-decision-atlas/web lint
cd apps/notifier; go vet ./...; go test ./...
```

## Postgres observability (dev)

`docker-compose.yml`'s `postgres` service preloads `pg_stat_statements`
(P2-1, Аудит-эпизод 7). It still needs to be registered once per database
after the stack is up — `apply_migrations.py` doesn't do this, since a
`CREATE EXTENSION` here would fail in CI's plain `postgres:16-alpine`
service (no `shared_preload_libraries` override there), so it stays a
manual dev-only step:

```sql
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
```

Top-N slowest queries by total time:

```sql
SELECT
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    rows
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;
```

`/metrics` (the FastAPI app's own endpoint) exposes request counts,
latency, and DB pool gauges separately — `pg_stat_statements` is for
diagnosing *which queries* are slow, not request-level metrics.

## Gate policy

- Before merge to `main`: full gate
  (`python dev_tools_scripts_runner.py`) must be green — it covers static
  checks, pytest, Go, Docker stack + migrations + runtime smokes, E2E,
  pre-commit.
- Quick gate (`--profile quick`) is the minimum for intermediate pushes.
- Config-only or docs-only changes still go through pre-commit hooks
  (they run automatically on commit).
- Windows note: pytest may need
  `-p no:cacheprovider --basetemp=<temp dir>` when temp-dir cleanup fights
  antivirus; the runner handles this itself.

---

<!-- module: .ai/project/12-domain-rules.md -->

# Domain Rules and House Style (Country Decision Atlas)

These sharpen the universal rules for this codebase. Stricter wins.

## Code structure

- Services or repositories over ~800 lines (stricter than the universal
  1000) become a package: `__init__.py` re-exports the full previous public
  surface so external imports keep working.
- Monkeypatch safety when splitting modules: cross-cutting private helpers
  (audit, feature-flag checks, shared validators) go into one sibling
  `helpers.py`, and submodules call them by qualified module access
  (`helpers.thing(...)`), never `from .helpers import thing` — otherwise
  `monkeypatch.setattr` in tests silently stops intercepting. Run the full
  test suite immediately after any split.
- Test files use the established collision-safe abbreviations: `_repo`,
  `_dq`, `_mig`.

## Domain constraints

- Do NOT add countries or languages unless the owner explicitly asks.
- Do NOT use AI-driven translation unless the owner explicitly asks.
- Localization reads go through `app/services/localization.py`
  (`overlay_localized_fields`), never per-field branching.
- Keep legacy DB columns in place after superseding migrations.
- Feature gating via `ensure_feature_enabled(connection, key, message)`;
  new user-facing surfaces launch behind flags, disabled until acceptance.
- Missing config or an invariant violation must fail loudly — never create
  a second silent source of truth (pattern: `methodology_config.py`).

## Migrations

- Next sequential number, `NNN_short_name.sql`, one-line header comment
  (`-- Migration NNN: ...`), idempotent (`IF NOT EXISTS`,
  `ON CONFLICT DO ...`), sqlfluff-clean.
- An applied migration file is immutable: `schema_migrations` tracks exact
  filename + content checksum. Renaming/editing one is allowed only if the
  owner explicitly accepts the local database reset cost.

## Contracts

- After any API schema change: update `contracts/openapi.yaml`, run
  `pnpm contracts:generate`, commit the regenerated
  `packages/contracts/generated/types.ts`, and keep contract tests green.

## Assistant workspaces

- `.claude/agents|skills` and `.codex/agents|skills` are name-for-name
  mirrors; when one side changes, apply the equivalent change to the other
  in the same task.
- `.claude/settings.json` allowlists routine read-only commands and denies
  destructive git/Docker operations. Extend the allowlist rather than
  routing around it; never remove a deny entry without explicit owner
  approval.

---

<!-- module: .ai/project/13-progress-tracking.md -->

# Project Progress Tracking

Purpose: any assistant, in any session, with any model, can locate exactly
where the project is and where it is going — from files, not from memory.

## Where the truth lives

| Question | File |
|---|---|
| How do we work (process, gates, layers) | `docs/_arch_/00_Рабочий_стандарт.md` |
| What is built and how it is shaped | `docs/_arch_/01_Продукт/02_Текущее_состояние_системы.md` |
| What is planned, in what order, what is DONE | `docs/_arch_/02_План/01_План_реализации.md` |
| What must never break | `docs/_arch_/02_План/02_Реестр_инвариантов.md` |
| Owner decisions and open questions | `docs/_arch_/08_Открытые_вопросы.md` |
| What the current/last task was | `task-checklist.md` (repo root) |
| What actually happened recently | `git log --oneline -10` |

## Orientation ritual — at the start of every task

1. `git status --short --branch` and `git log --oneline -10`.
2. Read the episode table in `01_План_реализации.md` §1 and the `**Статус.**`
   lines under each episode: episodes with a Статус line are done; the first
   episode without one is next.
3. Read `task-checklist.md` to see what the previous task was and whether it
   finished cleanly.
4. Only then plan the new task.

## Update duties — when finishing work

- Completed an episode (or a significant slice): add/refresh the
  `**Статус.**` line under that episode in `01_План_реализации.md`
  (what shipped: migration numbers, key modules, endpoints).
- Changed the system's shape (new domain, new service package, new
  operational job): update `02_Текущее_состояние_системы.md` in the
  matching section.
- Made or received an owner decision that constrains the future: it belongs
  in `08_Открытые_вопросы.md` / the plan header, not only in the chat.
- The episode order is binding: 1→2→3→4→5→6→7, then the visual tranche,
  then the integration tranche. Do not start a later episode before its
  dependencies without an explicit owner decision.

## Drift guard

If the plan, the current-state doc, and the code disagree, the code is the
fact, the plan is the intent — reconcile them in the same task or report the
mismatch explicitly. Never let the docs silently rot: stale docs are worse
than no docs.
