# Task: Interface re-audit + magic-value cleanup (frontend + backend)

Owner request (2026-07-19, follow-up to the completed
`feat/i18n-three-language-interface` work): on the same branch —

1. Re-verify the public interface has zero remaining hardcoded strings —
   labels, phrases, names, anything user-facing must be dynamic/reactive,
   driven by the message catalog, not baked into the code.
2. Sweep the whole project (backend `apps/api` + frontend `apps/web` +
   `packages/ui`) for magic values — numbers, strings, arrays used inline
   without a name — and eliminate the ones that are genuinely magic
   (unexplained, duplicated, or meaningfully named business constants).
   Leave alone values that are obviously fine as literals (CSS/layout
   numbers, trivial loop bounds, single-use self-explanatory constants) —
   owner's own instruction: don't touch necessary literals, only real
   magic values.

Work style: careful, unhurried, professional. Intermediate commits are
explicitly fine — one commit per logical group of fixes rather than one
giant diff.

## Stage 1 — Survey (read-only, no edits)

- [ ] Frontend hardcoded-string re-audit: grep the public route tree
      (`apps/web/src/app/[locale]/**` and the feature/shared components it
      renders) for literal Cyrillic/English UI text outside `t()`/
      `useTranslations`/enum-dict calls. Cross-check the known gap already
      on record (`packages/ui` `Breadcrumbs` `ariaLabel` default) and look
      for any others like it.
- [ ] Frontend magic-value audit: `apps/web/src`, `packages/ui/src` —
      inline numeric thresholds/timeouts/retry counts/pagination sizes,
      repeated literal strings that should be a shared constant/enum,
      unexplained magic numbers in business logic (not layout/CSS).
- [ ] Backend magic-value audit: `apps/api/app` — inline numeric
      thresholds/cutoffs/retry limits/time windows, repeated literal
      strings (status codes, event types, etc.) that should be named
      constants or enums, unexplained magic numbers in scoring/business
      logic.
- [ ] Consolidate findings into a concrete fix list here, grouped by area,
      each entry: file, what's magic, proposed fix (name it / extract
      constant / wire real translation), and whether it's in scope
      (skip anything that's a deliberate, already-documented value from
      the invariants registry or locked scoring math — those are
      explicitly off-limits per `.ai/project/10-project-map.md`'s
      invariant list).

## Stage 2 — Fixes (incremental commits, one group at a time)

- [ ] Frontend: wire any remaining hardcoded UI strings into the message
      catalog (en/ru/es, parity-checked).
- [ ] Frontend: extract/name real magic values found in Stage 1.
- [ ] Backend: extract/name real magic values found in Stage 1 (constants
      module or local named constant, whichever fits the existing
      architecture pattern in that area).
- [ ] Re-run `i18n_parity_check.py`, typecheck/lint/format, relevant test
      suites after each group.

## Stage 3 — Verification

- [ ] Full quality gate (`python dev_tools_scripts_runner.py full-check
      --profile full`).
- [ ] Browser walkthrough of any UI area touched, in all 3 locales.

## Completion

- [ ] Checklist filled (`+`/`-`).
- [ ] Final report: what was fixed, what was deliberately left alone and
      why, commits made.
