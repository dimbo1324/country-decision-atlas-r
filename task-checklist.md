# Task: Frontend Stage 3 (app shell, data layer, auth)

Source plan: `docs/_arch_/FRONTEND_IMPLEMENTATION_PLAN.md`, §7 Этап 3.
Continues directly on `feat/frontend-design-system-foundation` (same branch as
Stage 1+2, per owner instruction — no new branch).

Scope note: locale-in-URL applies to **public segments only** per the plan's
own wording ("locale-in-URL для публичных сегментов") — `/internal/**`
(Stage 12's own separate shell) stays unprefixed, still env-gated by the
existing middleware check.

## Preparation

- [+] Survey current locale handling (`?locale=` query param, 23 pages),
      auth (`AuthProvider`/`session.ts`, cookie-hint mechanism), API layer
      (`shared/api/http.ts` + 31 modules), config, AppShell, error/not-found
      boundaries, and package.json — via read-only audit before any edits.

## Implementation

- [+] Add dependencies: `next-intl`, `@tanstack/react-query`,
      `openapi-fetch`, `nuqs`, `cmdk`, `vaul`, `react-hook-form`, `zod`.
- [+] next-intl routing: `i18n/routing.ts`, `i18n/navigation.ts`,
      `i18n/request.ts`, `messages/ru.json` + `en.json` (chrome strings
      only), `next.config.mjs` plugin wrapper, `middleware.ts` (locale
      detection merged with the existing `/internal` env-gate, checked
      first).
- [+] Move the 21 public `page.tsx`/`loading.tsx` files under
      `app/[locale]/**`; keep `/internal/**` (2 pages) outside with its own
      minimal layout (no shared AppShell yet — that's Stage 12's dedicated
      internal shell); fix relative imports shifted by the new directory
      level.
- [+] Root `layout.tsx`: keep fonts/background/AuthProvider/Toaster,
      dynamic `<html lang>`; new `app/[locale]/layout.tsx`: locale
      validation + `NextIntlClientProvider` + rebuilt `AppShell`.
- [+] New AppShell: TopBar (shimmer logo, letter-spacing nav, from the
      prototype's visual language), footer with `DisclaimerNotice` + REF
      marking, mobile nav via Vaul drawer, ⌘K palette shell (cmdk, static
      sections — real `/search` wiring is Stage 5).
- [+] Data layer: `QueryClientProvider` with staleTime defaults,
      `openapi-fetch` client wrapper reusing the existing error-envelope
      shape, one reference domain module (countries) demonstrating the
      `queryOptions` factory pattern usable from both RSC prefetch and
      client. The other 30 `shared/api/*` modules stay on the existing
      `http.ts` wrapper — plan explicitly calls this a gradual replacement,
      not a one-shot rewrite.
- [+] Auth: reskin `LoginForm`/`RegisterForm` on `packages/ui` `Field`
      primitives + RHF + Zod, preserving every existing `data-testid`;
      centralize the duplicated `ADMIN_ROLES`/`MODERATION_ROLES`/
      `ALLOWED_ROLES` sets into `shared/auth/roles.ts` + a `useAuthGuard`
      hook; `AuthProvider`'s documented SSR-safe effect left untouched.
- [+] Feature flags: `FeatureProvider` reading `/platform/features`,
      `<Feature flag="...">` gate component.
- [+] Analytics: `useAnalyticsEvent` hook wrapping the existing
      `trackEvent`.
- [+] Global `error.tsx` restyled with `packages/ui` `ErrorState`; new
      root `not-found.tsx` (previously absent entirely).
- [+] Update `tests/e2e/helpers/routes.ts` and every spec hardcoding
      `?locale=` to the new path-prefixed scheme.

## Verification

- [+] `packages/ui` and `apps/web` typecheck/lint/build.
- [+] Browser walkthrough: locale switch persists across navigation,
      login/register/logout still work, `/account` and `/internal`
      guards render the same notices as before, mobile nav opens, ⌘K
      shell opens/closes, branded error/not-found render.
- [+] Full Playwright e2e suite green. 284/284 pass. Fixed 7 files with a
      leftover `?locale=` query-param bug and one missing `aria-label` (see
      final report). Two tests in `web-mvp-decision-passport.spec.ts`
      additionally needed `.first()` on two assertions: confirmed via the
      raw SSR HTML in a Playwright trace that Next.js 15's streaming
      renderer leaves an orphaned `hidden` placeholder div for this route's
      Suspense boundary (its `$RC` relocation call targets a different
      boundary) — a framework-level artifact invisible to real users, not
      an app bug. One `web-mvp-analytics.spec.ts` failure during the
      full-suite run did not reproduce in isolation (resource-contention
      flake under sequential load, consistent with prior runs).

## Completion

- [+] Fill this checklist (`+`/`-`).
- [+] Final report: what shipped, what's deferred, any risks.
