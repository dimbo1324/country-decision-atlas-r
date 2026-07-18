# Task: Fix `format:check`/`format:prettier` glob missing `.tsx` under `packages/**`

Root `package.json`'s `format:check` / `format:prettier` scripts glob
`"packages/**/*.{ts,json}"` — `.tsx` is excluded entirely under `packages/**`,
so `packages/ui/src/**/*.tsx` has never been covered by CI or local
`format:check`, only by manual/ad-hoc prettier runs. Pre-existing debt,
unrelated to the current frontend-redesign branch. Fix scope is
formatting-only, no behavior changes.

## Preparation

- [ ] Confirm current drift: `pnpm exec prettier --check "packages/**/*.tsx"`
      and record the affected file list.

## Implementation

- [ ] Add `.tsx` to the `packages/**/*` glob in `format:prettier` and
      `format:check` in root `package.json`.
- [ ] Run `pnpm exec prettier --write` on the newly-covered `packages/**/*.tsx`
      files to bring them in line. Formatting only — no refactors.

## Verification

- [ ] `pnpm format:check` passes clean.
- [ ] `packages/ui` typecheck passes.
- [ ] `packages/ui` lint passes (if a dedicated lint target exists).
- [ ] `pnpm --filter @country-decision-atlas/web typecheck` and `lint` still
      pass (sanity check nothing downstream broke).
- [ ] Diff review: only formatting changes (whitespace/quotes/etc.), no
      logic/behavior edits.

## Completion

- [ ] Checklist filled (`+`/`-`).
- [ ] Final report delivered to the owner.
