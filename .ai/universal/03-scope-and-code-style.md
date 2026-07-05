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
