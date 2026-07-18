# Task: Fix `format:check`/`format:prettier` glob missing `.tsx` under `packages/**`

Root `package.json`'s `format:check` / `format:prettier` scripts glob
`"packages/**/*.{ts,json}"` — `.tsx` is excluded entirely under `packages/**`,
so `packages/ui/src/**/*.tsx` has never been covered by CI or local
`format:check`, only by manual/ad-hoc prettier runs. Pre-existing debt,
unrelated to the current frontend-redesign branch. Fix scope is
formatting-only, no behavior changes.

## Preparation

- [+] Confirmed current drift: `pnpm exec prettier --check "packages/**/*.tsx"`
      found 25 files with drift (Accordion.stories, BoardGrid, Breadcrumbs,
      Card.stories, Dialog.stories, Drawer(+stories), ErrorState(+stories),
      Field(+stories), Icon, LoadingState, MetricCard,
      ModerationQueue(+stories), Pagination, RadioCards.stories,
      Select(+stories), Slider, Tabs.stories, Toast.stories, Toggle,
      Tooltip.stories — all under `packages/ui/src/primitives/`).

## Implementation

- [+] Added `.tsx` to the `packages/**/*` glob in `format:prettier` and
      `format:check` in root `package.json` (`{ts,json}` -> `{ts,tsx,json}`).
- [+] Ran `pnpm exec prettier --write "packages/**/*.tsx"` to reformat the 25
      drifted files. Formatting only — no refactors.

## Verification

- [+] `pnpm format:check` passes clean.
- [+] `packages/ui` typecheck (`tsc --noEmit`) passes clean.
- [+] `packages/ui` lint (`eslint .`) passes clean.
- [+] `apps/web` typecheck and lint pass clean (downstream sanity check).
- [+] Diff review: all 25 reformatted files are pure prettier re-wrapping
      (line-width/indentation/quote-style), spot-checked `Slider.tsx` and
      `Breadcrumbs.tsx` in full — no logic/behavior edits.

## Completion

- [+] Checklist filled (`+`/`-`).
- [+] Final report delivered to the owner.
