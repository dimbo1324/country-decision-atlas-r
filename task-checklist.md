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
3. `chore/remove-web-prototype` — `.claude/launch.json` and
   `pnpm-lock.yaml` both auto-merged cleanly (Stage 5's `APP_ENV` addition
   to the `web-prod` entry and this branch's removal of the neighboring
   `web-prototype` entry were different parts of the same array/file);
   only `task-checklist.md` conflicted again, resolved the same way.

`chore/remove-web-prototype`'s own completion record (preserved here since
it documents real verification work, not just merge mechanics): confirmed
scope via a repo-wide grep (9 files with real mentions plus the directory
itself, zero hits in `.codex/`, `.claude/agents|skills`, `AGENTS.md`,
`CLAUDE.md`, `.ai/`); removed the `apps/web-prototype` workspace entry,
`.claude/launch.json` dev-server block, README table row; reworded
comments in `fonts.ts`, the decision-passport page, `.storybook/main.ts`,
and `theme.css` that referenced the prototype (the `theme.css` one needed
a real edit, not just deletion — confirmed Storybook's
`preview-head.html` loads the same font families via a Google Fonts
`<link>`, i.e. it was always the *other* real consumer this comment
described, `web-prototype` was just the named example); removed the
`docs/_arch_` section describing the prototype and renumbered the
following section; reworded the implementation plan's "tranche prep
already done" paragraph to past tense. `git rm -r` removed all 61 tracked
files.

## Verification (after all three merged, on the integration branch)

- [ ] `pnpm install` to regenerate `pnpm-lock.yaml` cleanly.
- [ ] Full typecheck/lint (`ui` + `web`), `pnpm format:check`.
- [ ] `next build` clean, JS-budget script passes.
- [ ] Full Vitest (`apps/web` + `packages/ui`).
- [ ] `packages/ui` `storybook build` clean.
- [ ] Full Playwright e2e suite.
- [ ] Visual regression suite.
- [ ] Contrast + i18n-parity audits.
- [ ] Confirm zero `web-prototype` references remain (except the one
      intentional historical mention), confirm the format glob covers
      `packages/**/*.tsx`, confirm Stage 5's test infrastructure and
      RadioCards a11y fix are present.

## Completion

- [ ] Checklist filled (`+`/`-`).
- [ ] `git merge --ff-only` this integration branch onto `main`.
- [ ] Push `main` to `origin`.
- [ ] Final report.
