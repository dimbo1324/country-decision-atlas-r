# Task: Stage 13 stream 6 — Vitest unit tests for apps/web and packages/ui

Source: Stage 13 handoff note — "Vitest. В репозитории пока нет вообще
(ни конфига, ни зависимости). Поставить vitest для apps/web и packages/ui,
начать с тестов на shared/lib/* и entities/*/api.ts."
Branch: `feat/frontend-stage13-vitest` (fresh off `main`, after i18n-parity
merge).

## Preparation

- [+] Confirmed no vitest config/dependency exists anywhere in the repo.
- [+] Surveyed `apps/web/src/shared/lib/*.ts` for pure-function candidates:
      `features.ts`, `flagEmoji.ts`, `format.ts`, `locale.ts`,
      `localization-labels.ts`, function-valued entries of `routes.ts` are
      good candidates. `glossary-labels.ts` (static lookup) and
      `useAppLocale.ts` (React hook) are out of scope for this pass.
- [+] Surveyed `packages/ui/src/lib/*.ts`: `cn.ts`, `color.ts`
      (`withAlpha`), `scoreLabel.ts` are good pure candidates.
      `confidence.ts` is a type-only file (nothing to test). `accents.ts`
      is a static lookup table (low value, skipped).
- [+] Surveyed `apps/web/src/entities/*/api.ts` (29 subdirs): most are thin
      Pattern-A wrappers whose only pure/testable surface is `queryKey`/
      `enabled`/`staleTime` construction on the `*Query()` option builders
      (not the `useXxxMutation` hooks themselves, which need React
      rendering and are out of scope for this first pass). Picked a
      representative subset: `decision/api.ts` (multi-query module with
      `enabled` branching) and `admin-country-proposals/api.ts` (status
      filter in queryKey).

## Design decisions

- [+] One `vitest.config.ts` per workspace package (`apps/web`,
      `packages/ui`), not a single root config — matches the existing
      per-package `tsconfig`/lint setup, keeps each package's test run
      independent and filterable via pnpm `--filter`.
- [+] Test environment: `node` for pure `shared/lib`/`packages/ui/lib`
      functions; `apps/web` config additionally needs React/JSX support
      (via `@vitejs/plugin-react`) for future component tests, `packages/ui`
      too since it's a component library, even though this first pass only
      exercises plain functions.
- [+] `entities/*/api.ts` tests call the exported `*Query()` builder
      functions directly and assert on the returned plain object
      (`queryKey`, `enabled`, `staleTime`) — no `QueryClient`/React
      Testing Library involved, keeping this pass dependency-light.
- [+] Not adding `msw`/component-render tests in this stream — that is
      explicitly its own separate remaining stream ("MSW + Storybook
      interaction-тесты") per the Stage 13 handoff list.
- [+] `pnpm test` script added per-package; not wired into the quick/full
      quality gate in this stream (scope is "add vitest + initial tests",
      gate wiring is a natural follow-up but not asked for here — will
      call this out explicitly in the final report as a gap, not silently
      skip it).

## Implementation

- [+] Added `vitest`, `@vitejs/plugin-react`, `jsdom` as devDependencies
      to `apps/web`; added `vitest`, `jsdom` to `packages/ui` (it already
      had `@vitejs/plugin-react`/`vite` for Storybook).
- [+] Added `vitest.config.ts` to both packages (jsdom environment, React
      plugin, `src/**/*.test.{ts,tsx}` include glob).
- [+] Added `test`/`test:watch` scripts to both `package.json`.
- [+] Wrote tests: `apps/web/src/shared/lib/{features,flagEmoji,format,
      locale,localization-labels,routes}.test.ts` (49 tests total across
      `apps/web`, including the 2 entities suites below).
- [+] Wrote tests: `apps/web/src/entities/decision/api.test.ts`,
      `apps/web/src/entities/admin-country-proposals/api.test.ts` —
      mock the underlying `shared/api/*` client modules with `vi.mock`
      and assert on the plain `queryKey`/`enabled`/`retry` fields
      returned by each `*Query()` builder, plus that `queryFn` delegates
      to the mocked client with the right arguments. Deliberately not
      testing the `useXxxMutation` hooks — those need a `QueryClient` +
      React rendering, out of scope for this pass.
- [+] Wrote tests: `packages/ui/src/lib/{cn,color,scoreLabel}.test.ts`
      (8 tests).
- [+] `pnpm install` at repo root updated the lockfile (ran implicitly by
      each `pnpm add -D`).

## Verification

- [+] `pnpm --filter @country-decision-atlas/web test` — 8 files, 49
      tests, all green.
- [+] `pnpm --filter @country-decision-atlas/ui test` — 3 files, 8 tests,
      all green.
- [+] `pnpm typecheck` (web) and `pnpm --filter @country-decision-atlas/ui
      typecheck` — both clean. Found and fixed one real issue during
      verification: the `isFeatureEnabled` test fixtures used partial
      `FeatureFlag`/`FeatureFlagListResponse` object literals that failed
      strict structural typing against the generated contract types;
      fixed with a `flag()` fixture factory building fully-shaped
      `FeatureFlag` objects instead of loosening the test's type
      strictness.
- [+] `pnpm lint` (web) and `pnpm --filter @country-decision-atlas/ui
      lint` — both clean.
- [+] `pnpm build` — clean, all 44 routes compiled, no regression in
      bundle sizes vs the Stage 13 stream 3 baseline.
- [-] Did not run the full Python/Docker/E2E quality gate
      (`python dev_tools_scripts_runner.py`) — this stream is
      frontend-only (new devDependencies + `.test.ts` files under
      `apps/web`/`packages/ui`), doesn't touch backend, migrations, or
      E2E specs, so it isn't expected to affect that gate; noting as an
      explicit gap rather than silently skipping.

## Completion

- [+] Commit(s).
- [ ] Merge to `main`, push — only once explicitly confirmed complete.
- [+] Final report — given in the chat response accompanying this
      checklist update.

## Not done in this stream (deliberately out of scope)

- Vitest is not wired into `dev_tools_scripts_runner.py` or the
  quick/full quality gate — the ask was "add vitest + initial tests,"
  gate wiring is a natural follow-up but wasn't requested here.
- No MSW/component-render/Storybook interaction tests — that is its own
  separate remaining Stage 13 stream.
- Not all 29 `entities/*/api.ts` modules got coverage, only the 2
  representative ones named above (`decision`, `admin-country-proposals`).
