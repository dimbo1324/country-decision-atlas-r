# Task: Interface re-audit + magic-value cleanup (frontend + backend)

Owner request (2026-07-19, follow-up to the completed
`feat/i18n-three-language-interface` work): on the same branch —

1. Re-verify the public interface has zero remaining hardcoded strings —
   labels, phrases, names, anything user-facing must be dynamic/reactive,
   driven by the message catalog, not baked into the code.
2. Sweep the whole project (backend `apps/api` + frontend `apps/web` +
   `packages/ui`) for magic values — numbers, strings, arrays used inline
   without a name — and eliminate the ones that are genuinely magic
   (unexplained, duplicated, or meaningfully named business constants).
   Leave alone values that are obviously fine as literals (CSS/layout
   numbers, trivial loop bounds, single-use self-explanatory constants) —
   owner's own instruction: don't touch necessary literals, only real
   magic values.

Work style: careful, unhurried, professional. Intermediate commits are
explicitly fine — one commit per logical group of fixes rather than one
giant diff.

## Stage 1 — Survey (done, delegated to 3 parallel research agents)

- [+] Frontend hardcoded-string re-audit — done. **9 confirmed genuine
      bugs**, all real hardcoded/untranslated UI text or `aria-label`
      leaks still reaching a real page in the public `[locale]` tree:
      1. `packages/ui/Breadcrumbs.tsx` `ariaLabel` default
         (`"Хлебные крошки"`) never overridden by `AppBreadcrumbs.tsx` at
         its 4 call sites (`routes/[id]`, `trips/[id]`,
         `migration-board/[id]`, `decision/passports/[token]`) — known
         gap, still open.
      2. `packages/ui/DossierRail.tsx` `ariaLabel` default
         (`"Разделы досье"`) never overridden by `CountryDossier.tsx`'s 2
         call sites.
      3. `packages/ui/LegalSignalTimeline.tsx` `ariaLabel` default never
         overridden by `LegalSignalsRegistryView.tsx`.
      4. `packages/ui/Drawer.tsx` `closeLabel` default (`"Закрыть"`, used
         as the close button's `aria-label`) never overridden by
         `SourceEvidenceDrawer.tsx`/`LegalSignalEvidenceDrawer.tsx`.
      5. `packages/ui/ChartFrame.tsx` — several strings hardcoded with
         **no override prop at all** (verified-date label, confidence
         label map, "Online", expand/collapse `aria-label`, expanded-state
         placeholder) — reachable via `LegalSignalsRegistryView.tsx`.
      6. `CountryLegalSignals.tsx` — 3 raw hardcoded Russian strings, no
         `t()`/dict at all (empty state, "Published:", "In effect from:").
      7. `CountrySources.tsx` — 4 raw hardcoded Russian strings, same
         pattern (empty state, "Verified:", "Published:", "Open source").
      8. `adaptTimelineEvents.ts`'s `IMPACT_LABELS` — plain
         `Record<string,string>` (Russian-only), not locale-aware, feeds
         the timeline SVG tooltip title on every locale.
      9. `app/layout.tsx`'s `metadata.description` — static Russian
         `<meta name="description">`, no per-locale `generateMetadata` in
         `[locale]/**`, so `/en`/`/es` visitors get a Russian SEO
         description.
      Checked and confirmed fine (not bugs): every enum-dict/`t()`-driven
      file from Stages 1–10, `Pagination`/`HorizontalPager` (defaults but
      all real call sites override them), date/number formatting (all
      locale-keyed), `not-found.tsx`/root `error.tsx` (deliberate,
      documented tradeoff — outside `NextIntlClientProvider` by
      necessity, revisited in Stage 2 below for a possible `[locale]`-
      scoped override), design-system-only `packages/ui` chart components
      never imported by `apps/web` (`PassportCard`, `DriftBoard`,
      `DivergingMeter`, `Heatmap`, `RankFlow`, `SparklineChart` —
      Storybook-only, same "confirmed dead from a real user's
      perspective" precedent as Stage 2's original `PassportCard`
      finding; left untouched, noted here rather than silently skipped),
      backend content data (unchanged scope boundary).
- [+] Frontend magic-value audit — done. Findings, high→low priority:
      1. `RouteFilters.tsx`'s `ROUTE_TYPE_VALUES` array duplicates the
         keys already in `route-labels.ts`'s `ROUTE_TYPE_LABELS`.
      2. `SearchFilters.tsx`'s `ENTITY_TYPE_VALUES` array duplicates the
         keys already in `entity-type-labels.ts`'s `ENTITY_TYPE_LABELS`.
      3. `Confidence` union type (`"low"|"medium"|"high"`) re-declared in
         5 places instead of importing the existing export from
         `@country-decision-atlas/ui`.
      4. `limit: 100` "fetch all countries" cap duplicated in
         `LegalSignalsRegistryView.tsx` (×2) and `SourcesView.tsx` instead
         of reusing `allCountriesQuery()`.
      5. Score→label/color threshold bands duplicated with *inconsistent*
         cut points across `CountryCiiBlock.tsx`, `CountryScores.tsx`,
         `packages/ui/PassportCard.tsx` (dead component, see above) — name
         them without changing values (behavior-preserving); flag the
         inconsistency for the owner rather than silently unifying.
      6. `maxLength={2000}` duplicated twice in `CommunityCountryBlock.tsx`
         — low priority, name it.
      Reviewed and confirmed fine: `SEARCH_DEBOUNCE_MS`/`PALETTE_RESULT_LIMIT`,
      per-query `staleTime`/`retry` (intentionally vary per resource),
      session/cookie constants, decorative chart animation intervals.
- [+] Backend magic-value audit — done (read `02_Реестр_инвариантов.md`
      first; core CII/scoring math and `methodology_config.py` correctly
      excluded as locked/already-centralized). Findings:
      1. `INTERVAL '30 days'` staleness window hardcoded verbatim in raw
         SQL across 6 files (`author_metrics/reputation.py`,
         `data_quality/ai.py`, `data_quality/platform_metrics.py`,
         `trust.py`, `data_quality/decision_passports.py`,
         `data_quality/trust.py`) — all currently the *same* value, so
         centralizing is behavior-preserving; plus `ai_context.py`'s
         `INTERVAL '365 days'` repeated 3× within one file (same
         underlying issue).
      2. `confidence_rank` ordinal dict (`{"low":1,"medium":2,"high":3}`)
         duplicated verbatim 3× across `decision_engine/helpers.py` and
         `decision_engine/decision_runner.py` (×2).
      3. `trust_score.py`'s `compute_confidence()`/`compute_trust_label()`
         use fully inline thresholds in a file that *already* names its
         other thresholds at the top (`MIN_SOURCES_FOR_SCORE`,
         `FRESHNESS_FRESH_DAYS`, etc.) — internal inconsistency with the
         file's own established pattern.
      4. Feature-flag keys `"community_enabled"`/`"community_qna_enabled"`
         hardcoded as bare strings across 4 files, no `Literal`/`Enum`
         backing — typo-prone, and per invariant #14 (deny-by-default) a
         silent typo here masks the mistake rather than catching it.
      5. Redis `socket_connect_timeout=0.2`/`socket_timeout=0.2` duplicated
         verbatim in `cache.py` and `rate_limiter.py`, the one timeout not
         already centralized in `Settings` (every other timeout/TTL is).
      Explicitly skipped (invariant/config-protected): all
      `methodology_config.py`/`cii_matrix.py`/`cii.py` weights and
      tier-cutoffs, `ScoreLabelThresholds`/`ConfidenceThresholds` (already
      injected config), per-endpoint pagination `limit`/`offset` bounds
      (intentional per-endpoint variance, not a bug).
      **Open question for the owner, not resolved by the audit**: whether
      the 30-day staleness window is meant to be one global policy or
      allowed to drift per-domain — since all 6 sites currently agree,
      centralizing to one constant changes nothing behaviorally today, so
      proceeding with that safe interpretation; flagging here in case the
      intent was actually "allowed to diverge later."

## Stage 2 — Fixes (incremental commits, one group at a time)

- [+] Frontend: wired all 9 confirmed hardcoded-string bugs into the
      message catalog (en/ru/es, parity-checked at every step:
      1023→1038→1045 keys/locale across 3 commits `9f8bbfd`/`0c3fa0b`,
      then `08e5a1e` for the error-boundary fix below).
      - `9f8bbfd`: `AppBreadcrumbs`/`DossierRail`/`LegalSignalTimeline`
        `ariaLabel` props now wired (new `breadcrumbs` namespace,
        `countryDossier.dossierRailAriaLabel`, `legalSignalsTimeline`
        additions); both evidence drawers' `closeLabel` wired (new
        `close` key in each namespace); `ChartFrame` gained a `labels`
        prop (Stage 2-of-the-i18n-task's `DriftBoard` pattern) since it
        previously had **no override mechanism at all** for several
        strings, wired at its one real call site.
      - `0c3fa0b`: `CountryLegalSignals.tsx`/`CountrySources.tsx` had raw
        hardcoded Russian JSX text with zero `useTranslations()` —
        fully wired (new `countryLegalSignals`/`countrySources`
        namespaces, reused the existing `evidenceCard.openSource` key
        rather than duplicating it). `adaptTimelineEvents.ts`'s
        `IMPACT_LABELS` was a Russian-only plain `Record`, not
        locale-aware — extracted `TimelineFilters.tsx`'s *already
        correct* `Record<SupportedLocale,...>` version into a shared
        `impact-direction-labels.ts` (de-duplicating a second inline
        copy in the same motion) and threaded `locale` through the
        function's signature and its one call site.
        `[locale]/layout.tsx` gained a `generateMetadata()` so the
        `<meta name="description">` is locale-aware (new `metadata`
        namespace) instead of permanently inheriting the root layout's
        static Russian description for every locale.
      - `08e5a1e`: found a **previously orphaned message-catalog
        namespace** (`error` — title/message/retry, present in the
        catalog since Stage 1 but never wired to anything) while
        investigating the audit's flagged "deliberately non-i18n"
        root `error.tsx`/`not-found.tsx`. Added a segment-local
        `[locale]/error.tsx` using that namespace — root `error.tsx`
        stays deliberately non-i18n (still needed for `/internal/**`
        and truly locale-less paths) but a real error inside the public
        `[locale]` tree now shows correctly translated text. **Verified
        live**, not just by reading the framework docs: temporarily
        forced a `throw` in the home page, confirmed `/en` renders
        "Something went wrong" and `/ru` renders "Что-то пошло не так"
        via the new nested boundary, then reverted the test throw
        immediately (`git status` confirmed clean before and after).
        Also tried a matching `[locale]/not-found.tsx` using the
        similarly-orphaned `notFound` namespace — **verified live that
        it does NOT work**: Next.js's App Router falls through to the
        root `not-found.tsx` for any genuinely unmatched path
        regardless of a nested `not-found.tsx` file (tested both a
        garbage path and an invalid `[locale]` segment); unlike
        `error.tsx`, this isn't a real React error-boundary mechanism.
        Reverted that file rather than ship dead code — a working fix
        needs a catch-all route explicitly calling `notFound()`, a
        larger change out of scope for this cleanup pass, noted here
        for the record rather than silently dropped.
      Deliberately left untouched (documented, not silently skipped):
      `packages/ui`'s Storybook-only chart components confirmed never
      imported by `apps/web` (`PassportCard`, `DriftBoard`,
      `DivergingMeter`, `Heatmap`, `RankFlow`, `SparklineChart`) — same
      "dead from a real user's perspective" precedent as the original
      i18n task's `PassportCard` finding.
- [+] Frontend: extract/name real magic values found in Stage 1 (`b563244`).
      `ROUTE_TYPE_VALUES`/`ENTITY_TYPE_VALUES` now derived from
      `ROUTE_TYPE_LABELS`/`ENTITY_TYPE_LABELS` via `Object.keys()` instead
      of a second hand-maintained array; the `Confidence` union imported
      from `@country-decision-atlas/ui` at all 4 real duplicate sites
      (left `decision-wizard-labels.ts`'s `Level` type alone — same
      literal values by coincidence, different domain concept, aliasing
      it would be a misleading merge); `LegalSignalsRegistryView.tsx`/
      `SourcesView.tsx` now reuse `allCountriesQuery()` instead of
      re-passing `{ limit: 100 }`; `CountryCiiBlock.tsx`/
      `CountryScores.tsx`'s score-band thresholds named without changing
      values (documented the pre-existing divergence in a comment rather
      than silently unifying two independently-tuned visual scales);
      `CommunityCountryBlock.tsx`'s duplicated `maxLength={2000}` named
      `COMMUNITY_TEXT_MAX_LENGTH`.
- [+] Backend: extract/name real magic values found in Stage 1 (`9d66c3e`).
      New `app/repositories/staleness.py` centralizes the 30-day
      "needs recompute" window (6 files, all already agreed on the same
      value) and `ai_context.py`'s separate 365-day freshness window (3x
      in one file) — also found `platform_metrics.py`'s own
      `STALE_DAYS_THRESHOLD=30` was defined but never actually wired to
      its query, a second, dead near-miss of the same fix. `helpers.py`'s
      `confidence_rank` dict named `CONFIDENCE_RANK`, referenced from
      `decision_runner.py` via the existing qualified-module-import
      convention. `trust_score.py`'s `compute_trust_label`/
      `compute_confidence` thresholds named to match the file's own
      already-established pattern. The `"community_enabled"` feature-flag
      key (5 call sites, 3 files) named `FEATURE_KEY_COMMUNITY`. The
      duplicated 0.2s Redis timeout promoted to
      `Settings.redis_connect_timeout_seconds`, documented in
      `.env.example`. Explicitly left untouched: all
      `methodology_config.py`/`cii_matrix.py`/`cii.py` weights and
      tier-cutoffs (invariant-locked), `ScoreLabelThresholds`/
      `ConfidenceThresholds` (already injected config), per-endpoint
      pagination bounds (intentional variance, not a bug).
- [+] Re-ran `i18n_parity_check.py` (1045/1045 final), typecheck/lint/
      format for both `apps/web` and `packages/ui`, full Vitest
      (`web` 86/86, `ui` 8/8), and the full backend `pytest` suite
      (2248 passed, 58 skipped, 0 failures) after every group — all
      green throughout, no regressions introduced by any fix.

## Stage 3 — Verification

- [ ] Full quality gate (`python dev_tools_scripts_runner.py full-check
      --profile full`).
- [ ] Browser walkthrough of any UI area touched, in all 3 locales.

## Completion

- [ ] Checklist filled (`+`/`-`).
- [ ] Final report: what was fixed, what was deliberately left alone and
      why, commits made.
