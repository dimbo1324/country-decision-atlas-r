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

- [+] `pnpm install`: lockfile was already consistent post-merge ("up to
      date, resolution step skipped") — the 3-way merge of
      `pnpm-lock.yaml` resolved cleanly on its own, nothing to regenerate.
- [+] Full typecheck/lint clean: `ui` and `web` both.
- [+] `pnpm format:check` clean — confirmed the glob now covers
      `packages/**/*.tsx` (was `{ts,json}`, now `{ts,tsx,json}`).
- [+] `next build` clean (45 routes); `check_js_budgets.py`: worst route
      297.0 kB, ceiling 330 kB, OK.
- [+] Full Vitest: `apps/web` 77/77, `packages/ui` 8/8.
- [+] `packages/ui` `storybook build` clean; spot-checked
      `Tabs.stories.tsx` directly — both the reformatted `Default` story
      and Stage 5's new `ControlledFiveTabs` story are present together,
      confirming the auto-merge combined both branches' changes correctly
      rather than one silently clobbering the other.
- [+] Full Playwright e2e suite: **330/330 passed, 0 flaky** (Docker
      stack healthy throughout this run — no repeat of the earlier
      Docker-daemon-crash artifact from Stage 5's own verification).
- [+] Visual regression suite: 5/5 passed, no baseline changes needed.
- [+] Contrast audit: all tokens pass. i18n-parity: 90/90 keys match.
- [+] Confirmed zero problematic `web-prototype` references remain (only
      the one intentional historical mention, see above); confirmed
      `RadioCards.tsx`'s roving-tabindex a11y fix and the new
      `apps/web/src/test-utils/render.tsx` test infrastructure are both
      present in the merged tree.
- [+] No fixes were needed on `main` after merging — everything was
      already green on the integration branch before the fast-forward.

## Completion

- [+] Checklist filled (`+`/`-`).
- [+] `git merge --ff-only` this integration branch onto `main`.
- [+] Deleted all four now-fully-merged branches (local + remote):
      `fix/packages-tsx-format-check-glob`,
      `feat/frontend-redesign-stage-5-consolidation`,
      `chore/remove-web-prototype`,
      `integration/stage5-formatfix-protoremoval` — plus the orphaned
      local-only `claude/gallant-dubinsky-f97d5e` (zero unique commits,
      sat exactly at old `main`'s tip). Only `main` remains.
- [+] Pushed `main` to `origin`.
- [+] Final report.
