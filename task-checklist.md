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

- [ ] Frontend: wire any remaining hardcoded UI strings into the message
      catalog (en/ru/es, parity-checked).
- [ ] Frontend: extract/name real magic values found in Stage 1.
- [ ] Backend: extract/name real magic values found in Stage 1 (constants
      module or local named constant, whichever fits the existing
      architecture pattern in that area).
- [ ] Re-run `i18n_parity_check.py`, typecheck/lint/format, relevant test
      suites after each group.

## Stage 3 — Verification

- [ ] Full quality gate (`python dev_tools_scripts_runner.py full-check
      --profile full`).
- [ ] Browser walkthrough of any UI area touched, in all 3 locales.

## Completion

- [ ] Checklist filled (`+`/`-`).
- [ ] Final report: what was fixed, what was deliberately left alone and
      why, commits made.
