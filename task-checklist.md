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

- [ ] Add `msw`, `msw-storybook-addon` as devDependencies to
      `packages/ui`.
- [ ] Wire `msw-storybook-addon` into `.storybook/preview.tsx` /
      `.storybook/main.ts`, generate the MSW service worker file.
- [ ] Write play-function stories for a handful of key interactive
      components (final list depends on the survey above).
- [ ] Add `tests/visual/` + `playwright.visual.config.ts`, write
      screenshot specs for the 5 target pages/states.
- [ ] Add a `web:mvp:visual` script to root `package.json`.
- [ ] Capture baseline screenshots (`--update-snapshots`), commit them.

## Verification

- [ ] `pnpm --filter @country-decision-atlas/ui storybook` interaction
      tests pass (via Storybook's test runner or manual play verification).
- [ ] New visual regression spec passes against the freshly captured
      baseline on a clean re-run (proves determinism on this machine).
- [ ] `pnpm typecheck`, `pnpm lint`, `pnpm build` still green.
- [ ] Existing `pnpm web:mvp:check` / `tests/e2e` suite unaffected
      (spot-check a subset, not the full 40+ spec suite, given time cost).

## Completion

- [ ] Commit(s).
- [ ] Merge to `main`, push — only once explicitly confirmed, together
      with the Vitest stream this branched from.
- [ ] Final report.
