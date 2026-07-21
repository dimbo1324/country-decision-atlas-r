# Deep-Dive Research: Product Insights and the Data Model

A consolidated overview of five deep-dive research packages (Additional Deep Dive Research): product opportunity (Q14–Q15), global migration, competitors and user pain (Q5–Q8), country direction (Q09–Q13), and a final gap-closing pass. This gathers the findings that directly bear on the platform's architecture.

## Headline finding

The relocation-information market's problem isn't a lack of volume — it's **verifiability**. Thousands of blogs, rankings, videos, and forum threads are easy to find; hard to find is a single, trusted, continuously updated system that answers: what rule applies today; when it was last checked; whether it's official, commercial, expert, community, or anecdotal; whether it applies to my scenario; what's changed recently and what's changing next; what real migrants report after relocating; which data is solid and which is uncertain and locally variable.

That's the space for a platform built around **evidence quality**, **timestamping**, **scenario modeling**, **country direction**, and **real post-arrival experience**.

## The competitors' data-source pattern

1. **Official/public datasets** — macro indicators: migration flows, GDP, unemployment, crime, taxes, governance, education, health, climate, infrastructure.
2. **Crowdsourcing** — local cost of living, neighborhood feel, internet quality, rent, prices, bureaucracy, perceived safety.
3. **Editorial research** — visa summaries, destination guides, rankings.
4. **Commercial affiliate content** — banking, insurance, taxes, relocation services, legal advice, investment migration.
5. **User/community data** — reviews, comments, forums, city pages, expense reports, profiles.

Strong consumer products are good at discovery and UX; their weak spot is source transparency (they often don't show a last-verified date, a source hierarchy, a methodology, or the gap between law and actual administrative practice).

## The object data model

- **Country** — a country: region, cities, baseline indicators, direction, data confidence.
- **City** — a city: cost, safety, housing, internet, climate, community, relevance to work/business.
- **Route** — a visa/residency route: type, eligibility, documents, fees, duration, renewal, family, work rights, the path to permanent residency/citizenship.
- **LegalSignal** — a legal signal: a law/policy change, its source, effective date, affected routes and personas, before/after, severity, confidence.
- **Source** — a source: URL, type, publish date, verification date, an authority level, language, a reliability score.
- **EvidenceItem** — a unit of evidence: a quote/summary, its source, the country/route/claim it's tied to.
- **Persona** — a persona: a skilled worker, a nomad, an entrepreneur, an investor, a student, a family, a retiree, someone seeking safety.
- **ScenarioRun** — a scenario run: user inputs, country and route scores, warnings, next steps.
- **UserStory** — a real story: an anonymized case, country/city, route, timeline, budget, documents, outcome, a verification level.

## The Country Direction / Drift Index

The goal isn't to say a country is "good" or "bad," but to measure whether it's becoming more or less fit for a given scenario. Two axes: **current state** (how attractive/risky it is today) and **direction/drift** (improving, declining, or growing more uncertain).

### Dimensions

| Dimension | Description | Example sources |
|---|---|---|
| Migration openness | Ease of entry, stay, renewal, naturalization | Immigration authorities, visa portals, legal updates |
| Citizenship pathway | Clarity and speed of the path to citizenship | Citizenship law, official clarifications, lawyers |
| Legal stability | Predictability of rules and institutions | Rule-of-law indices, WJP, official changes |
| Political direction | Liberalizing vs. authoritarianizing, stability | V-Dem, Freedom House, the EIU, news/legal signals |
| Business friendliness | Company registration, taxes, bureaucracy, property rights | Tax authorities, the World Bank/OECD, Heritage/Fraser |
| Cost pressure | Inflation, rent pressure, cost of living | Numbeo, official inflation data, housing portals |
| Social acceptance | Attitudes toward migrants, discrimination, integration | Surveys, community reports, hate-crime statistics |
| Safety/security | Crime, conflict, unrest, travel risk | Travel warnings, crime statistics, Crisis24/Riskline |
| Human infrastructure | Healthcare, schools, banking, transport, digital services | Official data, user reports, OECD/UN |
| Data confidence | Freshness and verifiability of the evidence | Source metadata, verification date, source count |

### The signal model

Every update becomes a signal. Types: legal, political, economic, social, a safety signal, a community signal, a market signal, a search-demand signal. Signal fields: `signal_id`, `country`, `date_detected`, `effective_date`, `source_url`, `source_type` (official / media / legal expert / community / data), `scenario_affected` (migration / business / investment / family / study / nomad / citizenship), `impact_direction` (positive / negative / mixed / uncertain).

> This model maps directly onto the project's architecture: legal signals and their timeline (`legal_signals`, events), the Country Direction Index (Drift, computed from `legal_signal_events`), and per-field data confidence. See [../../architecture/](../../architecture/overview.md) and [../../architecture/cii-methodology-notes.md](../../architecture/cii-methodology-notes.md).

## The MVP readiness decision

The research archive is ready to inform MVP planning; the broad general research phase can wrap up in favor of product strategy and technical design. The MVP doesn't need to cover every country and every user — it needs to prove one working flow:

`A user's goal → a country shortlist → comparing objective data → reviewing legal signals → reading structured human experience → a scenario recommendation.`

### Recommended first countries (12–15)

Uruguay, Argentina, Paraguay, Portugal, Spain, Serbia, Georgia, Armenia, Turkey, the UAE, Mexico, Chile, Canada, the Netherlands; the US or the UK as benchmark countries. (The project's actual MVP started with Uruguay, Argentina, and Russia.)

### Recommended first scenarios

1. A fast path to residency/citizenship.
2. Affordable long-term living.
3. Remote-worker/digital-nomad relocation.
4. Company registration / entrepreneur relocation.
5. Family relocation focused on safety, healthcare, and education.

## Product modules (a capability map)

- **Country Cards** — country profiles: a profile, routes, recent legal changes, accessibility, family/business fit, the citizenship path, risk flags, data confidence, a verification date.
- **Persona-based comparison** — the same country ranks differently for different personas.
- **Scenario Simulator** — a feasibility score, a cost estimate, legal blockers, tax flags, a timeline, a document checklist, backup countries, a confidence level.
- **Legal Signal Tracker** — legal-signal tracking with a status (proposed / adopted / effective / revoked), affected groups, severity, verification.
- **Evidence Map** — a map of evidence: every important claim is tied to an official source, expert opinion, a community signal, a last-verified date, and a confidence level.
- **Community Stories** — structured user stories (not free-form forum posts).
- **Country Direction / Drift Index** — tracking whether a country is becoming more open/closed, business-friendly, tax-aggressive, stable, or accessible.

## The source reliability model (A–F)

A — official (government/law/court/statistics); B — an international organization (OECD/UN/IOM/World Bank/ILO); C — a recognized legal/tax/mobility firm, dated and attributed; D — a commercial platform with a methodology; E — lived community experience; F — an unverified rumor/anonymous claim/old post. Community content can't be equated with law, but it's valuable for surfacing hidden friction.

## Unique deliverables from the packages

- **The Top-50 Competitor Feature Matrix** — a 50-competitor feature matrix (also available as a CSV — see [../competitive-analysis/feature-matrix-50-competitors.csv](../competitive-analysis/feature-matrix-50-competitors.csv)).
- **A Legal Source Map (15 priority countries)** — a map of official legal sources across 15 priority countries.
- **Search Demand Methodology and Query Bank** — a search-demand methodology and a query bank.
- **A User Research Interview and Survey Pack** — an interview and survey pack.
- **A Monetization Benchmark and Pricing Signals** — a monetization benchmark and pricing signals.
