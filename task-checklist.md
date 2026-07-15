# Task: Stage 13 streams 7-8 — MSW/Storybook play-tests + Playwright visual regression

Source: Stage 13 handoff list —
"MSW + Storybook interaction-тесты. Storybook уже есть в packages/ui,
MSW — нет. Добавить msw + msw-storybook-addon, написать несколько
play-историй для ключевых компонентов." и
"Визуальная регрессия. Playwright screenshot-тесты минимум для: главная,
каталог, досье страны, результат решения, паспорт. Снимать baseline нужно
на текущем состоянии (после потоков 1-4)."
Branch: `feat/frontend-stage13-msw-visual-regression`, off
`feat/frontend-stage13-vitest` (not yet merged to `main`) per owner
instruction — both branches merge to `main` together once this stream is
done.

## Preparation

- [ ] Confirm no existing `msw`/`msw-storybook-addon` dependency anywhere.
- [ ] Survey `packages/ui/src/**/*.stories.tsx` for components with real
      interactive/async behavior worth a `play` function (form inputs,
      dialogs/drawers with open-close state, anything that fetches).
      Most existing stories are static presentational snapshots with no
      data-fetching — MSW's value is specifically for components that
      call `fetch`, so the target set is narrow.
- [ ] Confirm local dev stack (`docker compose up api redis`, migrations,
      demo countries, search index) is up so Playwright can hit a real
      running `apps/web` + API for baseline screenshots.
- [ ] Read `playwright.config.ts` and an existing spec to match existing
      conventions (`e2eRoutes`, `expectNoAppCrash`, testids).

## Design decisions

- [ ] MSW + play-stories are additive to `packages/ui`'s existing
      Storybook setup (`msw-storybook-addon` registers a service worker
      via `initialize()` in `.storybook/preview.tsx`, `mswLoader` +
      per-story `parameters.msw.handlers`).
- [ ] Visual regression is a **separate Playwright project/config**, not
      added into `tests/e2e/` — `scripts/dev_tools/full_check.py`'s E2E
      phase runs `pnpm web:mvp:check` → bare `playwright test` against
      `playwright.config.ts`'s `testDir: "tests/e2e"`, which would sweep
      up screenshot specs automatically. Pixel-level screenshot diffing
      is OS/font-rendering-dependent (this repo's own docs already flag
      the analogous Windows-vs-Linux-CI gap for `-race`/cgo); baselines
      captured locally on Windows would spuriously fail in a Linux CI
      runner. Keeping visual regression in its own `tests/visual/` +
      `playwright.visual.config.ts`, run only via an explicit new
      `web:mvp:visual` script, avoids silently making the existing gate
      OS-fragile. This is a deliberate scope/risk call, documented here
      and in the final report, not a silent omission.
- [ ] `prefers-reduced-motion` is already respected repo-wide (Stage 13
      stream 4) — visual regression sets `reducedMotion: "reduce"` at
      the context/project level so chart count-up animations etc. don't
      introduce nondeterminism.
- [ ] 5 target pages/states, minimum per the ask: home (`/ru`), catalog
      (`/ru/countries`), country dossier (`/ru/countries/russia`),
      decision result (`/ru/decision` after running a decision), and a
      decision passport (`/ru/decision/passports/[token]`).

## Implementation

- [+] Added `msw`, `msw-storybook-addon`, `@storybook/test` as
      devDependencies to `packages/ui` (pinned `@storybook/test` to the
      exact `@storybook/react`/`react-vite` version to clear a peer-dep
      mismatch warning pnpm surfaced).
- [+] Ran `npx msw init public/ --save` to generate the MSW service
      worker (`packages/ui/public/mockServiceWorker.js`); wired
      `staticDirs: ["../public"]` into `.storybook/main.ts` and
      `initialize()` + `mswLoader` into `.storybook/preview.tsx`.
- [+] Confirmed `packages/ui/src` has zero data-fetching code (grepped
      for `fetch(`/`useQuery`/`useMutation`/`axios` — no matches): it's a
      purely presentational design system per the project's own
      architecture doc. No existing component naturally needs MSW
      handlers, so rather than fabricate a fake data-fetching demo,
      MSW's real use in this stream is the new `ModerationQueue` story
      below, whose `onRun` prop is genuinely async and calls `fetch` in
      real call sites (`apps/web`'s admin queues).
- [+] Wrote play-function stories for 4 components:
      - `Dialog.stories.tsx` — open via trigger, assert `role="dialog"`
        appears, close via Escape, assert it's gone.
      - `Select.stories.tsx` — open, pick an option, assert the trigger
        reflects the new value.
      - `Tabs.stories.tsx` — switch tabs, assert content pane changes.
      - `ModerationQueue.stories.tsx` (new component, no prior story) —
        two stories: `RejectWithReason` drives the full reason-required
        confirm-dialog flow against an MSW-mocked `POST` endpoint, and
        `OpenDetailWithKeyboard` is a direct regression test for the
        Stage 13 stream 4 accessibility fix (focus a row, press Enter,
        confirm the detail drawer opens).
- [+] Added `tests/visual/pages.visual.spec.ts` + separate
      `playwright.visual.config.ts` (see Design decisions for why it's
      not inside `tests/e2e/`), covering the 5 requested
      pages/states: home, catalog, country dossier, decision result,
      decision passport. `reducedMotion: "reduce"` at the context level
      plus `animations: "disabled"` per screenshot call for determinism;
      `maxDiffPixelRatio: 0.02` tolerance for anti-aliasing noise.
- [+] Added `web:mvp:visual` / `web:mvp:visual:update` scripts to root
      `package.json`.
- [+] Captured baseline screenshots against the local dev stack (Docker
      Postgres/Redis/API + seeded demo countries, `next build` + `next
      start`), committed them under `tests/visual/pages.visual.spec.ts-
      snapshots/`.
- [+] Added `public` to `packages/ui/eslint.config.js`'s ignore list —
      the generated `mockServiceWorker.js` isn't hand-written source.
- [+] Extended the root `format:check`/`format:prettier` globs to cover
      `tests/visual/**/*.ts` (previously only `tests/e2e/**/*.ts` was
      covered).

## Verification

- [+] Debugged and fixed a real flake in `ModerationQueue.stories.tsx`'s
      `RejectWithReason` play function while manually verifying it in
      the browser: `userEvent.type()` on the reason textarea combined
      with MSW's service-worker round trip pushed the test past
      sonner's ~4s toast auto-dismiss window, so the final assertion on
      toast text sometimes found nothing. Confirmed the actual app
      behavior was correct (manually replayed the exact click/type/
      submit sequence via raw DOM events — the mocked `fetch` and toast
      both fired correctly). Fixed by switching to `fireEvent.change`
      (synchronous, no per-keystroke delay) and asserting on a durable
      postcondition (the confirm dialog closing) instead of the
      ephemeral toast text.
- [+] Verified all 4 play-function stories pass cleanly in a running
      Storybook instance (`ui-storybook` preview target), checked via
      DOM inspection for the Storybook error overlay after each play
      run — none present.
- [+] `pnpm --filter @country-decision-atlas/ui typecheck` / `lint` /
      `test` (vitest) — all clean after the story additions.
- [+] New visual regression spec passes 3 consecutive clean runs against
      the captured baseline (`pnpm web:mvp:visual`), proving determinism
      on this machine.
- [+] Spot-checked the existing `tests/e2e` suite (`web-mvp-pages`,
      `web-mvp-main-flow`, `web-mvp-decision-passport` — 20 tests) still
      passes unchanged against the default `playwright.config.ts`,
      confirming the new visual config doesn't interfere.
- [+] `pnpm typecheck`, `pnpm lint`, `pnpm build` (apps/web) — all green.
- [+] `pnpm format:check` — clean for every file touched in this stream
      and the prior Vitest stream; 6 pre-existing files unrelated to
      either stream (not touched by me) still fail prettier — a
      pre-existing gap on `main`, not introduced here, out of scope to
      fix silently. Named explicitly in the final report.

## Completion

- [+] Commit(s).
- [ ] Merge to `main`, push — only once explicitly confirmed, together
      with the Vitest stream this branched from.
- [+] Final report — given in the chat response accompanying this
      checklist update.
