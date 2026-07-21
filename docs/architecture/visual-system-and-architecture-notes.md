> Founding vision & architecture notes (v1.0, 2026-06-21) — written before implementation started. Kept as the original research/reasoning record; **not** a description of the current system. For what is actually built today, see [overview.md](overview.md); for the current roadmap, see [../product/roadmap.md](../product/roadmap.md). Some proposals here (WorldMap, spider chart) are still open per the roadmap's "visual tranche"; others (Metric Registry Pattern, versioned formulas, soft delete, domain separation) were adopted, in some cases with different concrete shapes than sketched below.

================================================================================
  COUNTRY DECISION ATLAS
  Visual system, architecture recommendations, and notes for the team
  Version: 1.0  |  Date: 2026-06-21
================================================================================


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SECTION 0. THE CONTEXT AND THE PROBLEM WE'RE SOLVING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Today, a user opens the app and sees: text, cards, descriptions, numbers in
tables. They have to read in order to understand. That creates a high
cognitive load and slows down decision-making.

The goal of this document is to describe a system where:

  → The user first SEES (a map, a radar chart, numbers, color)
  → Then UNDERSTANDS (comparison, dynamics, a breakdown)
  → Then, if needed, GOES DEEPER (text, sources, evidence)

This principle is called Progressive Disclosure. It runs through the entire
architecture described below.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SECTION 1. THE VISUAL CONCEPT — WHAT WE'RE BUILDING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1.1 THE HOME PAGE — "THE WORLD FROM ABOVE"
──────────────────────────────────────

The first thing a user sees is an interactive world map (a choropleth map)
where countries are colored by their overall score for the selected scenario:
green = high score, red = low score, gray = no data.

Above the map — a scenario picker: Relocation / Residency / Business / Safety,
and so on. Changing the scenario recolors the map in real time.

Below the map — three blocks:
  • TOP-5 countries for the selected scenario
  • WORST-5 countries
  • BIGGEST MOVERS — countries with the largest Country Drift over the past year

Technology: react-simple-maps + GeoJSON + D3.js for coloring.


1.2 THE COUNTRY CARD — "COUNTRY INTELLIGENCE DASHBOARD"
──────────────────────────────────────────────────────

The country card is completely rethought. Instead of text sections — a
visual dashboard split into tiers.

FIRST SCREEN (above the fold):
  ┌─────────────────────────────────────────────┐
  │  🇷🇺 RUSSIA          CII Score: 42/100       │
  │  Country Drift: ▼ -8  (Declining)           │
  ├───────────────┬─────────────────────────────┤
  │  Spider Chart │  3 key metrics:              │
  │  (8 axes)     │  Cost of living / Visa /     │
  │               │  Safety                      │
  ├───────────────┴─────────────────────────────┤
  │  Scenario Scores (horizontal bars)           │
  │  Relocation   ████████░░  68               │
  │  Residency    ████░░░░░░  42               │
  │  Budget       ██████░░░░  61               │
  │  Business     ███░░░░░░░  34               │
  │  Safety       ██░░░░░░░░  22               │
  └─────────────────────────────────────────────┘

SECOND SCREEN (after scroll):
  • Country Drift Timeline — a 5-year sparkline per dimension
  • Legal Signals — the latest 3, color-coded 🔴🟡🟢
  • Evidence Summary — a short summary of the evidence base

THIRD SCREEN (behind "Read more"):
  • The full text profile
  • Every source and piece of evidence
  • User stories
  • The full list of legal signals


1.3 THE DECISION PAGE — "REAL-TIME COMPARISON"
──────────────────────────────────────────────────────

The decision page stops being a form with a result.
It becomes a live comparative dashboard:

  • Two spider charts overlaid (blue vs. orange)
  • A grouped bar chart across every dimension, side by side for two countries
  • A colored winner badge per dimension
  • A Strengths / Weaknesses / Risk Warnings block
  • Sources behind every conclusion (clickable)

Adding a third country to compare — a P2 priority.


1.4 LEGAL SIGNALS — "THE POLICY TIMELINE"
──────────────────────────────────────

Instead of a list — a chronological vertical feed:

  2026  🔴  Law restricting foreign bank accounts
            Impact: high | Affects: migrants, investors
            [Source: Tax Authority → link]

  2025  🟡  Change to the residency permit process for freelancers
            Impact: medium | Affects: digital nomads

  2024  🟢  Lower tax rate for sole proprietors
            Impact: positive | Affects: entrepreneurs

Filters: by impact direction, by affected group, by year, by signal type.


1.5 THE COMPARE PAGE — "THE COUNTRY MATRIX"
───────────────────────────────────────

A heatmap table: rows = countries, columns = scenarios.
Each cell is colored by score. Clicking a cell opens a detailed comparison.

           Relocation  Business  Budget  Safety
Russia        42          34       61      22
Uruguay       74          65       58      79
Georgia       81          88       70      65
Portugal      69          72       45      80

This lets a user take in the entire choice set in seconds.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SECTION 2. COUNTRY INTELLIGENCE INDEX (CII) — THE METRIC SYSTEM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

CII is the single numeric measurement system that feeds every visualization.
Computed per country. Every chart, the map, and every comparison pull from one
source — the metric-values table.


2.1 THE EIGHT BASELINE DIMENSIONS
──────────────────────────────

  #  Dimension                 What it measures                Range
  ─────────────────────────────────────────────────────────────────────
  1  Political Stability      Stability, conflict risk         0–100
  2  Rule of Law              Courts, corruption, rule of law  0–100
  3  Economic Freedom         Business, taxes, barriers        0–100
  4  Cost of Living Index     Cost of living (100 = baseline)  0–200
  5  Residency Friendliness   Ease of residency/visas          0–100
  6  Quality of Life          Healthcare, education, HDI       0–100
  7  Digital & Remote Work    Internet, nomad infrastructure   0–100
  8  Country Drift            Where the country is heading     -100…+100

Country Drift is the platform's flagship unique indicator.
Negative Drift = the country is getting worse (closing off, declining).
Positive Drift = the country is getting better (reforms, opening up).
No competitor has anything like it.


2.2 DATA SOURCES AND AUTO-INGESTION
──────────────────────────────────────

Every source has a public API or an open dataset:

  Dimension               Source                            Access type
  ──────────────────────────────────────────────────────────────────────
  Political Stability     World Bank WGI                    Free API
                          Global Peace Index (IEP)          CSV dataset
  Rule of Law             World Bank WGI (Rule of Law)      Free API
                          Transparency Intl CPI             Annual CSV
                          Freedom House                     Dataset
  Economic Freedom        Heritage Foundation EFI           Public CSV
                          World Bank Business Ready         Free API
  Cost of Living           Numbeo                            Paid API ~$50/mo
                          World Bank PPP                    Free API
  Residency Friendly       MIPEX                             Dataset
                          Henley Passport Index             CSV
                          Internal legal signals            The project's DB
  Quality of Life          UNDP HDI                          Free API
                          WHO Health Index                  Dataset
  Digital/Remote Work      ITU Digital Development           Dataset
                          Ookla Speedtest Global            CSV
  Country Drift             Internal calculation from WGI    A computed field
                          + legal-signal dynamics

Key API endpoints:

  World Bank:
    https://api.worldbank.org/v2/country/{iso2}/indicator/{code}?format=json

  UNDP HDI:
    https://hdrdata.org/api/composite/4

  Numbeo:
    https://www.numbeo.com/api/ (requires an API key)

RECOMMENDATION: build a DataIngestionService that pulls from these sources
quarterly, normalizes into the 0–100 range, and stores the result in the
database with versioning and source attribution.


2.3 THE COUNTRY DRIFT FORMULA
──────────────────────────

  Drift(country, year) =
    Σ( weight_i × (metric_i(year) - metric_i(year-3)) ) / Σ(weight_i)

  year-3 is used to smooth out short-term noise.

  Default weights:
    Political Stability    0.25
    Rule of Law             0.25
    Economic Freedom       0.20
    Residency Friendliness 0.15
    Quality of Life        0.10
    Digital Infrastructure 0.05

  Interpreting the result:
    +15…+100  Actively improving      🚀 Green arrow up
    +5…+15    Moderate improvement    ↗ Light green
    -5…+5     Stagnant                → Gray
    -15…-5    Moderate decline        ↘ Yellow
    -100…-15  Actively declining      🔻 Red arrow down


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SECTION 3. ARCHITECTURE RECOMMENDATIONS — HOW TO BUILD THIS RIGHT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3.1 METRIC REGISTRY PATTERN — EXTENSIBLE METRICS WITHOUT MIGRATIONS
────────────────────────────────────────────────────────────────

THE FIXED-COLUMN PROBLEM:
  If metrics are stored as separate table columns:
    political_stability NUMERIC,
    rule_of_law         NUMERIC,
    economic_freedom    NUMERIC,
    ...
  — every new metric needs an ALTER TABLE + a DB migration + changes to
  repository code, schemas, TypeScript types. Expensive and risky.

THE CORRECT SOLUTION — two tables:

  Table 1: cii_metric_definitions (the metric registry)
  ───────────────────────────────────────────────────
  slug            VARCHAR UNIQUE    -- 'political_stability', 'rule_of_law'
  name_en         VARCHAR           -- human-readable name
  name_ru         VARCHAR
  description_en  TEXT
  category        VARCHAR           -- 'stability', 'economy', 'lifestyle'
  weight          NUMERIC           -- weight in the overall CII score
  value_min       NUMERIC           -- lower bound (usually 0)
  value_max       NUMERIC           -- upper bound (usually 100)
  higher_is_better BOOLEAN          -- for inverting (Cost of Living)
  data_source     VARCHAR           -- 'world_bank_wgi', 'undp_hdi'
  update_frequency VARCHAR          -- 'annual', 'quarterly'
  is_active       BOOLEAN DEFAULT true
  display_order   INT               -- axis order on the spider chart
  created_at      TIMESTAMPTZ
  updated_at      TIMESTAMPTZ

  Table 2: country_metric_values (the values)
  ─────────────────────────────────────────────
  id          UUID PRIMARY KEY
  country_id  UUID REFERENCES countries(id)
  metric_id   UUID REFERENCES cii_metric_definitions(id)
  year        INT
  value       NUMERIC           -- normalized value
  raw_value   NUMERIC           -- the original value from the source
  confidence  NUMERIC           -- 0.0–1.0
  source_id   UUID              -- where it came from
  ingested_at TIMESTAMPTZ
  UNIQUE(country_id, metric_id, year)

WHAT THIS BUYS US:
  + Adding a new metric = one INSERT into cii_metric_definitions
  + No ALTER TABLE, no schema migrations
  + The spider chart reads its axes dynamically from the API
  + Old data doesn't break when a new metric is added
  + Deactivating a metric = UPDATE is_active = false
  + Changing a metric's weight = UPDATE weight (scores recompute automatically)

IMPORTANT FOR THE FRONTEND:
  The spider chart, bar chart, and compare-matrix components must accept an
  array of metrics from the API response, not have hardcoded axes.
  Then adding a 9th metric updates the frontend automatically.


3.2 VERSIONING FORMULAS AND WEIGHTS
────────────────────────────────────

THE PROBLEM:
  If political_stability's weight changes from 0.25 to 0.20 in 2027,
  historical scores become incomparable to current ones. A 5-year Drift chart
  would be wrong.

THE SOLUTION — a formula-snapshot table:

  cii_formula_versions
  ─────────────────────
  id            UUID PRIMARY KEY
  version_tag   VARCHAR           -- 'v1.0', 'v1.1', 'v2.0'
  description   TEXT              -- what changed and why
  weights_json  JSONB             -- a snapshot of every weight at publish time
  effective_from DATE
  effective_to   DATE NULL        -- NULL = the current version
  created_by    VARCHAR
  created_at    TIMESTAMPTZ

  Every time scores are recomputed, always record the formula_version_id
  they were computed with.

  Then, when comparing historical data, the system knows which formula
  produced it and can either show a warning or recompute under a single
  methodology.


3.3 VERSIONING EXTERNAL DATA
────────────────────────────────────

  external_index_snapshots
  ─────────────────────────
  id              UUID PRIMARY KEY
  source_slug     VARCHAR           -- 'world_bank_wgi', 'transparency_cpi'
  country_id      UUID
  indicator_code  VARCHAR           -- 'PV.EST', 'RL.EST', etc.
  year            INT
  raw_value       NUMERIC           -- exactly as it came from the API
  unit            VARCHAR           -- '%', 'score', 'index'
  fetched_at      TIMESTAMPTZ       -- when we pulled it
  source_url      VARCHAR           -- the exact request URL
  api_version     VARCHAR           -- the API version at request time

  IMPORTANT: never overwrite raw data — only ever INSERT new rows. This lets
  us track how official data changed over time (retroactive index revisions
  are not uncommon).


3.4 SOFT DELETE EVERYWHERE
──────────────────────

Add this field to every meaningful table:

  deleted_at TIMESTAMPTZ NULL DEFAULT NULL

  Delete = UPDATE deleted_at = NOW()
  Select = WHERE deleted_at IS NULL

WHY THIS MATTERS:
  Once external partners, a B2B API, or a marketplace show up, a hard delete
  breaks historical references. It also matters for the audit trail: we need
  to know what was deleted and when.

  Apply to: countries, legal_signals, sources, evidence_items,
  user_stories, metric_definitions, country_profiles.


3.5 EVENT SOURCING FOR LEGAL SIGNALS
──────────────────────────────────────

THE PROBLEM:
  Legal signals change over time. A law is passed → amended → repealed.
  If we update one row via UPDATE, the history is lost.

THE SOLUTION:
  Store the change history as an event chain:

  legal_signal_events
  ────────────────────
  id              UUID PRIMARY KEY
  signal_id       UUID REFERENCES legal_signals(id)
  event_type      VARCHAR     -- 'created', 'amended', 'repealed', 'superseded'
  event_date      DATE        -- when the change happened in the real world
  description     TEXT        -- exactly what changed
  source_id       UUID        -- the source confirming the change
  recorded_at     TIMESTAMPTZ -- when we recorded it
  recorded_by     VARCHAR

  The legal_signals table holds the CURRENT state.
  The legal_signal_events table holds the FULL HISTORY.

  This lets us build a Policy Timeline with a real change history, not just
  a current status.


3.6 DOMAIN SEPARATION — DON'T MIX DOMAINS
─────────────────────────────────────────────

As new features appear, it's important to keep them as separate domains:

  /apps/api/app/domains/
    countries/          -- countries, profiles, cards
    metrics/            -- CII, metrics, external indices
    decisions/          -- the decision engine, scenarios, runs
    legal/              -- legal signals, events, the timeline
    content/             -- sources, evidence, user stories
    translations/       -- translation units, jobs, variants
    users/               -- accounts (once they exist)
    watchlist/           -- subscriptions and alerts (its own domain)
    marketplace/         -- consultants (its own domain)
    notifications/       -- emails, alerts (its own domain)

  RULE: domains must never import each other directly.
  Interaction happens through clear interfaces and services.
  This makes it possible to later split a domain out into its own
  microservice without rewriting everything.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SECTION 4. NUANCES WORTH KEEPING IN MIND
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4.1 DATA AND CONTENT
─────────────────────

• CONTENT STALENESS
  Legal data goes stale. Add to the tables:
    reviewed_at   TIMESTAMPTZ   -- last reviewed
    expires_at    TIMESTAMPTZ   -- recommended next-review date
    staleness_level VARCHAR     -- 'fresh', 'aging', 'stale', 'critical'
  We need an automated reminder system for editors.
  Legal content older than 12 months = critically stale.

• THE SOURCE'S ORIGINAL LANGUAGE
  A source in Portuguese is NOT the same thing as a machine translation of it.
  Never replace the original with a translation. Keep both.
  A source_language_original field is mandatory.

• RETROACTIVE INDEX REVISIONS
  World Bank and other providers sometimes revise historical data
  retroactively. We can't just overwrite raw values — we need to keep the
  data's fetch date (fetched_at) and the full request history.

• AGGREGATE-LEVEL CONFIDENCE
  If one of CII's eight dimensions has low confidence, the overall CII score
  must reflect that. Never average confidence values: the overall confidence
  = min(confidence across dimensions) or a weighted formula.

• SYNTHETIC-DATA MARKING
  User stories are currently marked is_synthetic. Going forward this matters
  for other data kinds too: AI-generated summaries, estimated values,
  interpolated data. Never mix synthetic and verified content without
  explicit marking.


4.2 USERS AND PERSONALIZATION
───────────────────────────────────

• USER CONTEXT AFFECTS EVERYTHING
  Once accounts exist, data relevance changes dramatically. The right country
  for a single freelancer and for a family with children are completely
  different. Build this into the architecture: the decision engine should
  accept user_context as a parameter (citizenship, family status, income,
  profession), not just scenario and locale.

• COLLECT REQUEST HISTORY FROM DAY ONE
  Which scenarios a user ran, which countries they viewed, what they
  compared. This is fuel for personalization and product analytics.
  If we don't collect it now, we can't get it back later.
  Even without accounts, we can collect it anonymously via session_id.

  decision_run_log (or analytics_events)
  ─────────────────────────────────────────
  session_id    VARCHAR
  scenario_slug VARCHAR
  countries     JSONB
  locale        VARCHAR
  result_hash   VARCHAR   -- for de-personalized tracking
  created_at    TIMESTAMPTZ

• WATCHLIST AND ALERTS — THEIR OWN DOMAIN
  Don't bolt this onto existing tables. A watchlist is:
    user_id + country_id + alert_conditions + delivery_method
  This is its own service with its own logic and infrastructure.


4.3 TRANSLATION AND MULTILINGUAL SUPPORT
────────────────────────────────────

• A TRANSLATION GLOSSARY
  Once 5–10 languages exist, the same terms will get translated
  inconsistently across the interface. We need a single glossary of approved
  translations:
    glossary_terms: term_en, term_ru, term_es, context, domain
  Especially critical for legal terms:
  residency permit, permanent residency, tax residency, beneficial owner —
  these must translate the same way everywhere in the app.

• TRANSLATION MEMORY
  If a source string changes, its translation goes stale. We need a
  source_hash mechanism: store a hash of the original text. When the original
  changes, recompute the hash, compare, mark the translation stale. This is
  already partially implemented — don't break it.

• LOCALE IN THE URL
  Right now: /countries/russia
  Think about this now: /ru/countries/russia  or  /countries/russia?locale=ru
  Reworking routing after launch is expensive and affects SEO.
  Decide BEFORE scaling to more languages.

• LEGALLY SENSITIVE CONTENT
  Machine translation → published truth — NOT ALLOWED.
  For legal signals, country profiles, legal descriptions, this pipeline is
  mandatory:
    original source → summary → machine draft → human review → published
  A machine translation of legal text must never be auto-published.


4.4 SCALING AND INFRASTRUCTURE
──────────────────────────────────────

• DATA CACHING
  Country data changes rarely — quarterly or less. At 50+ countries and
  20+ languages, serving it from PostgreSQL on every request is expensive and
  slow. We need a caching strategy:
    - Redis for hot data (country card, scores)
    - a CDN for statically generated pages
  Important: cache invalidation on data updates must be correct, or users
  will see stale data.

• SEARCH — DON'T EMBED IT DEEPLY
  There's no search today. Once there are 50+ countries and thousands of
  legal signals, we'll need full-text search. PostgreSQL FTS is enough for
  MVP. BUT: don't embed search logic deep inside business code. Search is a
  separate, replaceable layer that could later become Elasticsearch or
  Typesense without rewriting domain logic.

• RATE LIMITING FOR THE API
  Once B2B access exists, we'll need rate limiting. Build the abstraction now:
  every request goes through a single API Gateway where throttling can be
  attached without touching business logic.

• LOCALIZED URLS FOR SEO
  /countries/russia ranks poorly for Russian-speaking search. Down the road:
  /ru/страны/россия is a real SEO win. Solution: use slug-based routing with a
  locale prefix now, easy to configure in Next.js via internationalized
  routing.


4.5 MONETIZATION AND B2B
──────────────────────

• FEATURE FLAGS FROM DAY ONE
  What's free, what's paid — that decision shapes the architecture. Add a
  FeatureFlag or AccessTier abstraction as early as possible. Don't hardcode
  "show or don't show" logic in components. An example of the right shape:
    can_access(user, feature='country_drift') → boolean
  The logic inside that function can be anything — freemium, subscription,
  trial — with zero frontend component changes.

• A SEPARATE B2B API CONTRACT
  The platform's internal API and an external B2B API must be different. The
  internal one can change fast. The external one needs stability,
  versioning, and an SLA. Never expose the internal API to partners directly.

• MARKETPLACE AS ITS OWN DOMAIN
  Once a consultant marketplace exists, it's entirely different business
  logic: reputation, transactions, reviews, escrow, disputes. Don't mix it
  with country data. A separate domain, separate tables, possibly a separate
  application.

• AUDIT FOR MONETIZATION
  Every money-related action must be immutable. Financial audit logs — a
  separate table, INSERT-only, never UPDATE.


4.6 DATA QUALITY AND TRUST
───────────────────────────────

• THE CONTRADICTION DETECTOR — A UNIQUE FEATURE
  When an official source says one thing and practice says another, the
  system should detect and surface that to the user. Build this into the
  evidence model:
    contradicts_evidence_id UUID NULL
    contradiction_note TEXT NULL
  This lays the groundwork for automatic contradiction detection later.

• CONFIDENCE AT EVERY LEVEL
  Confidence should exist not only at the source level, but also for:
    - individual claims in evidence
    - a legal signal as a whole
    - a scenario score
    - the overall CII score
  And it should aggregate bottom-up — the overall score can't carry high
  confidence if even one dimension has low confidence.

• DATA FRESHNESS INDICATORS
  A user should always be able to see how fresh the data is. Don't hide
  stale content — show it with an explicit warning. last_verified_at is
  mandatory on all public data.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SECTION 5. THE IMPLEMENTATION PLAN — WHAT AND WHEN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PHASE 1 — THE VISUAL FOUNDATION (2–3 weeks)
  ✦ Agree on the final list of CII dimensions with the team
  ✦ Create the cii_metric_definitions and country_metric_values tables
  ✦ Fill in data for Russia and Uruguay by hand (from open sources)
  ✦ Build the API endpoint GET /api/v1/countries/{slug}/cii
  ✦ Build SpiderChart on the country card (recharts RadarChart)
  ✦ Build ScenarioBarChart on the country card
  ✦ Add a DriftBadge to the card and to decision results
  ✦ Build CountryDriftCalculator

PHASE 2 — COMPARISON AND THE MAP (2–3 weeks)
  ✦ WorldMap (choropleth) on the home page
  ✦ CompareMatrix (heatmap) on the /compare page
  ✦ DriftTimeline (a 5-year sparkline) on the country card
  ✦ LegalSignalTimeline instead of a list on /legal-signals
  ✦ API endpoint GET /api/v1/countries/compare (the matrix)
  ✦ API endpoint GET /api/v1/world-map (map data)

PHASE 3 — AUTO-INGESTION (as the project grows)
  ✦ A DataIngestionService wired to the World Bank API
  ✦ Add UNDP HDI
  ✦ Add Transparency International CPI
  ✦ A quarterly cron job for data refreshes
  ✦ Log every ingestion run into external_index_snapshots

PHASE 4 — USERS AND PERSONALIZATION (post-MVP)
  ✦ Auth, accounts, user profiles
  ✦ user_context in the decision engine
  ✦ Request history
  ✦ Watchlist and alerts

PHASE 5 — B2B AND MONETIZATION (a separate roadmap)
  ✦ Feature flags and access tiers
  ✦ A B2B API with its own contract
  ✦ A consultant marketplace
  ✦ Paywall and freemium logic


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SECTION 6. WHAT NOT TO DO (ANTI-PATTERNS)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ✗ Don't store metrics as fixed table columns
    → Use the Metric Registry Pattern (section 3.1)

  ✗ Don't overwrite raw data from external sources
    → Only INSERT new rows with fetched_at

  ✗ Don't hard-delete records
    → Only soft delete via deleted_at

  ✗ Don't auto-publish machine translations of legal content
    → Human review is mandatory for legal content

  ✗ Don't embed search logic in business code
    → Search is a separate, replaceable layer

  ✗ Don't mix domains: countries + marketplace + notifications
    → Separate domains with clear boundaries

  ✗ Don't hardcode the spider chart's axes on the frontend
    → Read metrics dynamically from the API

  ✗ Don't expose the internal API to partners directly
    → A separate B2B API contract

  ✗ Don't average confidence carelessly
    → The overall confidence = a weighted minimum, not an average

  ✗ Don't start the marketplace before the core product is stable
    → It's a separate product, needs its own resources


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SECTION 7. OPEN QUESTIONS FOR THE TEAM
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  1. CII DIMENSION WEIGHTS
     Set editorially (fixed by the team) or set by the user
     ("safety matters more to me than cost")?
     The second option is a powerful UX feature, but harder to build.

  2. COUNTRY DRIFT — WHO COMPUTES IT?
     Automatically from external data (a World Bank delta), or
     edited manually through admin with a justification?
     Recommendation: automatic + an editorial-override option.

  3. NUMBEO — PAID OR NOT?
     The Numbeo API costs ~$50/mo. Alternatives: World Bank PPP (free,
     less detailed) or manual data entry at the start.

  4. THE WORLD MAP — EVERY COUNTRY OR ONLY THOSE WITH DATA?
     Show every country gray and gradually color them in as data is added?
     Or only the ones with data?

  5. SPIDER CHART — 8 AXES OR 6?
     8 axes = the full picture, but reads worse on mobile.
     6 axes = reads better, but less information.
     Recommendation: 6 on mobile, 8 on desktop.

  6. LOCALE IN THE URL — DECIDE NOW
     /countries/russia  vs  /ru/countries/russia
     This affects SEO and routing. Reworking it after launch is expensive.
     Recommendation: Next.js internationalized routing with a locale prefix.

  7. FIRST-SCREEN PRIORITY
     A spider chart on the country card, or a WorldMap on the home page?
     Which matters more for the first visual release?


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SECTION 8. A SHORT SUMMARY FOR QUICK READING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

WHAT WE'RE BUILDING:
  A single visual CII system built on 8 numeric dimensions that runs through
  every page of the app — the world map, the spider chart, timelines, the
  comparison heatmap. The user sees first, reads second.

THE MAIN UNIQUE FEATURE:
  The Country Drift Index — a numeric expression of where a country is
  heading. No direct competitor has anything like it.

THE UX PRINCIPLE:
  Progressive Disclosure — three levels of depth. Visual → understanding →
  text. Every transition is explicit, triggered by a user click.

KEY ARCHITECTURE DECISIONS:
  • The Metric Registry Pattern — metrics in two tables, not columns
  • Soft delete everywhere
  • Event sourcing for legal signals
  • Versioned formulas and raw data
  • Domain separation — marketplace, watchlist, notifications = separate domains
  • Feature flags for monetization from day one
  • Collect user request history from day one

DATA SOURCES (auto-ingestion):
  World Bank API (free) → the primary source
  UNDP HDI (free)
  Transparency International CPI (CSV, annual)
  Heritage Foundation Economic Freedom (CSV, annual)
  Numbeo (paid, ~$50/mo) — consider after MVP

TIMELINE FOR THE FIRST VISUAL RELEASE:
  4–6 weeks of focused team work.

================================================================================
  END OF DOCUMENT
  Country Decision Atlas — Architecture Vision v1.0
  Prepared: 2026-06-21
================================================================================
