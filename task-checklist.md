# Task: Integrate three sibling branches into `main`

Owner request: three independent branches had accumulated off the same
`main` commit (`4335b46`) — `fix/packages-tsx-format-check-glob`,
`feat/frontend-redesign-stage-5-consolidation`, `chore/remove-web-prototype`
— and asked to land them all on `main` together. Each branch's own
`task-checklist.md` history (with its own detailed `+`/`-` completion
record) is preserved in git log on that branch's commits; this file
documents the integration itself, done on `integration/stage5-formatfix-protoremoval`
before a fast-forward merge into `main`.

## Merge order (chosen to minimize rework)

1. `fix/packages-tsx-format-check-glob` (smallest, most isolated —
   formatting only) — clean merge, no conflicts.
2. `feat/frontend-redesign-stage-5-consolidation` — one conflict:
   `task-checklist.md` (expected, each branch recreates it per the
   project's own protocol); `Tabs.stories.tsx` auto-merged cleanly
   (format-glob-fix's reformatting composed with Stage 5's added
   `ControlledFiveTabs` story without manual intervention).
3. `chore/remove-web-prototype` — conflicts expected on
   `task-checklist.md`, `.claude/launch.json` (Stage 5 added `APP_ENV` to
   the `web-prod` entry; this branch removed the neighboring
   `web-prototype` entry entirely — different parts of the same array),
   and `pnpm-lock.yaml` (regenerated fresh via `pnpm install` after the
   merge rather than trusting a 3-way lockfile merge).

## Verification (after all three merged)

- [ ] `pnpm install` to regenerate `pnpm-lock.yaml` cleanly.
- [ ] Full typecheck/lint (`ui` + `web`), `pnpm format:check`.
- [ ] `next build` clean, JS-budget script passes.
- [ ] Full Vitest (`apps/web` + `packages/ui`).
- [ ] `packages/ui` `storybook build` clean.
- [ ] Full Playwright e2e suite.
- [ ] Visual regression suite.
- [ ] Contrast + i18n-parity audits.
- [ ] Confirm zero `web-prototype` references remain, confirm the format
      glob covers `packages/**/*.tsx`, confirm Stage 5's test
      infrastructure and RadioCards a11y fix are present.

## Completion

- [ ] Checklist filled (`+`/`-`).
- [ ] `git merge --ff-only` this integration branch onto `main`.
- [ ] Push `main` to `origin`.
- [ ] Final report.
