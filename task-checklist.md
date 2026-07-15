# Task: Frontend Stage 11 (AI-ассистент)

Source plan: `docs/_arch_/FRONTEND_IMPLEMENTATION_PLAN.md`, §7 Этап 11.
Branch: `feat/frontend-stage11-ai-assistant` (fresh off `main` — Stage 10
merged, `37fe48e`).

## Preparation

- [+] Research pass done (Explore agent): `features/ai-assistant/` (8
      components) confirmed legacy-style (raw `useState`/`fetch` via
      `aiApi`, plain CSS-module classnames, zero design-system
      primitives) — same pattern as every other pre-reskin feature this
      project has hit. Backend already fully implemented and fake-by-
      default (`ai_mode: "fake"` in `apps/api/app/core/config.py`,
      `FakeAIProvider` in `apps/api/app/services/ai_providers.py`) — no
      backend work needed, matches plan's "бэкенд fake-by-default —
      фронт строится полностью" framing.
- [+] Confirmed the "answer without citations must never render as
      trustworthy" UI invariant is NOT currently enforced:
      `AIAnswerCard.tsx` renders `response.answer` as plain trustworthy
      prose whenever `!response.refused`, regardless of whether
      `citations` is empty. This is a real gap to fix, not a redesign.
- [+] Confirmed integration points already exist and just need reskin:
      `AIExplainNumberButton` is already wired into `CountryCiiBlock.tsx`
      (CII score) with `numberType="cii_score"`; `AIDecisionIntentHelper`
      is already wired into `DecisionRunForm.tsx` via
      `onApply={handleAiDecisionApply}` which maps the response onto the
      decision wizard's scenario/persona/candidate state. No new
      integration wiring needed, only visual/UX layer.
- [+] `ChartFrame` (packages/ui) has no actions slot in its header today
      — only title/badges/live-indicator/expand-button. Plan explicitly
      calls for an explain button "интеграция в ChartFrame", so an
      `actions?: ReactNode` prop is added there. Actual usage stays
      scoped to where score numbers already live (`CountryCiiBlock`,
      `DecisionResults` winner card) — `ChartFrame` itself is only used
      once in the app today (`LegalSignalsChartView`), so the slot is
      infrastructure for future reuse, not itself the CII/decision-score
      host (those aren't in a ChartFrame, they're in `Card`).
- [+] Existing Playwright coverage inventoried:
      `web-mvp-ai-assistant.spec.ts` (2 tests, page/mobile),
      `web-mvp-ai-decision-helper.spec.ts` (2 tests, decision-helper +
      explain-number-on-CII). All testids referenced
      (`ai-assistant-page`, `ai-question-input`, `ai-country-input`,
      `ai-submit`, `ai-answer-card`, `ai-refusal`, `ai-error`,
      `ai-disclaimer`, `ai-decision-helper`, `ai-decision-intent-input`,
      `ai-decision-intent-submit`, `ai-decision-result`,
      `ai-decision-error`, `cii-block`, `ai-explain-number-button`,
      `ai-explain-number-panel`) must survive the reskin unchanged.
- [+] `Popover`/`PopoverTrigger`/`PopoverContent` (packages/ui) confirmed
      as the right host for explain-number content, precedent:
      `GlossaryTerm.tsx`. `useReducedMotion` hook confirmed exported from
      `@country-decision-atlas/ui` for the moderate typing-animation
      opt-out.

## Design decisions

- [+] `entities/ai-assistant/api.ts` (new, Pattern A) wraps
      `shared/api/ai.ts`'s `aiApi` in TanStack `useMutation` hooks
      (`useAskAIMutation`, `useExplainNumberMutation`,
      `useParseDecisionIntentMutation`) — the shared/api layer itself
      doesn't need changes, only a Query wrapper, matching every prior
      stage's Pattern A precedent.
- [+] `AIAnswerCard` fixed to enforce the invariant: when
      `!refused && citations.length === 0`, the answer no longer renders
      as plain trustworthy prose — it's shown inside a `warning`-variant
      `Badge`-flagged block ("Без подтверждающих источников — не
      проверено") instead of the normal answer styling. Refused and
      cited-and-trustworthy paths keep their own distinct visual
      treatment.
- [+] `AICitationsList` reskinned onto `Card`/`Badge`/`Kicker`, reused
      unchanged by both `AIAnswerCard` and the explain-number popover.
- [+] `AIRefusalState` reskinned as a polite "archive" notice matching
      the existing terracotta-callout convention
      (`border-terra2/60 text-terra3`) already used for warnings
      elsewhere (`DecisionResults` fallback banner).
- [+] `AIDisclaimer` reskinned reusing the existing `disclaimer-notice`
      CSS convention (`DisclaimerNotice.tsx` precedent) since the text is
      dynamic (API-provided), not the shared component itself.
- [+] `AIExplainNumberButton` reskinned into a small icon "?" trigger +
      `Popover` (matching `GlossaryTerm.tsx` precedent) instead of a
      plain text link + inline panel.
- [+] `AIAskForm` and `AIDecisionIntentHelper` reskinned onto
      `Field`/`FieldLabel`/`Button` from the design system; kept as plain
      controlled state (not RHF+Zod) since there's no client-side
      validation beyond non-empty — matches the low-ceremony precedent
      already used for `AIDecisionIntentHelper`'s sibling
      `DecisionRunForm` inline fields.
- [+] `AIAssistantView` reskinned onto `Card`/`Kicker` two-column layout;
      a moderate "typing" loading indicator (three pulsing dots) shown
      while `isPending`, respecting `useReducedMotion` (falls back to a
      static "Готовим ответ…" label, no animation, when reduced motion is
      requested).
- [+] `/assistant` route page reskinned onto the `Kicker`+`h1` pattern
      used by every other Stage 9/10 route shell.
- [+] `ChartFrame` gets an optional `actions?: ReactNode` prop rendered
      in the existing header actions row, next to the expand/collapse
      button — additive, not a breaking change to the one existing
      caller (`LegalSignalsChartView`).

## Implementation

1. `packages/ui/src/primitives/ChartFrame.tsx` — added `actions?: ReactNode`
   prop, rendered in `FrameHeader`'s actions row.
2. `apps/web/src/entities/ai-assistant/api.ts` (new) — Pattern A mutation
   wrappers for ask/explain-number/decision-intent.
3. `apps/web/src/features/ai-assistant/*` — all 8 components reskinned:
   `AIAnswerCard`, `AIAskForm`, `AIAssistantView`, `AICitationsList`,
   `AIDecisionIntentHelper`, `AIDisclaimer`, `AIExplainNumberButton`,
   `AIRefusalState`.
4. `apps/web/src/features/country-card/CountryCiiBlock.tsx` — no changes
   needed; `AIExplainNumberButton`'s public props are unchanged, only its
   internals moved from a text link + inline panel to an icon trigger +
   `Popover`.
5. `apps/web/src/features/decision-run/DecisionResults.tsx` — added an
   `AIExplainNumberButton` (`numberType="decision_score"`) next to the
   winner's score, the plan's second explicit "минимум для CII и скоров
   сценариев" surface.
6. `apps/web/src/app/[locale]/assistant/page.tsx` — reskinned route shell.
7. `tests/e2e/web-mvp-ai-invariants.spec.ts` (new) — structural check that
   a non-refused answer is always either cited or explicitly flagged
   unverified (never plain trustworthy prose with neither), plus coverage
   for the new decision-score explain button.

## Verification

- [+] `pnpm --filter web typecheck` — clean, no errors.
- [+] `pnpm --filter web lint` — clean, no errors.
- [+] `pnpm --filter web build` — clean; `/assistant` route compiles
      (7.04 kB, up from 2.72 kB pre-reskin, expected given the added
      DS primitives and TanStack Query wiring).
- [+] Manual verification against the live Docker stack via Playwright
      (Docker Desktop and `.env` had reset between sessions — Docker
      Desktop restarted, `.env` recreated from the tracked, secret-free
      `.env.example` since local dev secrets are gitignored by design,
      migrations/seed/search-index re-run).
- [+] Existing `web-mvp-ai-assistant.spec.ts` (2 tests) and
      `web-mvp-ai-decision-helper.spec.ts` (2 tests) stay green with
      unchanged testids. New `web-mvp-ai-invariants.spec.ts` (2 tests)
      covers the no-citations-not-trustworthy invariant and the
      decision-score explain button. `web-mvp-main-flow.spec.ts` (which
      exercises the decision run end-to-end) also re-run clean. **7/7
      passed.**
- [+] `python dev_tools_scripts_runner.py --profile quick` — clean except
      the pre-existing `arabic_reshaper` venv gap (same known baseline
      issue documented since Stage 9/10, not a regression). One
      self-inflicted false failure along the way: recreating a local
      `.env` (needed for the seed scripts, from the tracked
      `.env.example`, no real secrets) made `pytest tests/config.py`
      pick it up via `BaseSettings`' cwd-relative `.env` loading and
      break `test_production_with_all_defaults_lists_every_unsafe_field`
      — removed `.env` after seeding finished (Docker itself sets its
      own env directly, doesn't need the repo-root file) and confirmed
      the gate goes clean.

## Completion

- [+] Commit(s)
- [ ] Merge to `main`, push — only once explicitly confirmed complete.
- [+] Final report
