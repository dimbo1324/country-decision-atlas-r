# Product Vision and Concept

> What Country Decision Atlas is after the baseline reset (2026-07), where it's headed, and why. The technical breakdown of the system is in [../architecture/overview.md](../architecture/overview.md); the work plan is in [roadmap.md](roadmap.md).

---

## 1. What the product is

Country Decision Atlas is an evidence-based platform for choosing a country and planning a relocation toward a specific goal: residency/permanent residency/citizenship, remote work, living on a limited budget, business and self-employment, safety, and long-term planning.

It is not a country ranking, a blog, or a forum. What sets the platform apart is **the verifiability of every claim**: every number has a source, a freshness date, a confidence level, and a methodology version; every conclusion comes with an explanation of how it was derived.

### The core framing shift

The system as implemented today is an excellent **reference tool**: a user arrives, studies the data, runs a scenario comparison, and leaves. A reference tool has two ceilings:

1. **Return visits.** "Which country should I choose" is a question someone asks a handful of times in their life. There's no reason to open the product daily.
2. **Content scale.** Every country, signal, and source passes through a single editorial team. The project's ceiling equals one person's throughput.

The target framing is a **workspace** where people plan a relocation and exchange verifiable migration knowledge. The formula:

> **A reference data core** (the platform's editorial team — the guarantor of quality) **+ an author layer** (users create metrics and methodologies, subscribe, fork) **+ a personal surface** (a relocation planner: waypoints, checklists, warnings, reminders) **+ AI tools on a leash** (cited, never the source of truth themselves).

### Three "openings" of closed systems

The growth strategy isn't to build something new from scratch — it's to progressively open up three systems already built internally:

| # | What's closed today | What we're opening | Roadmap episodes |
|---|---|---|---|
| 1 | Methodology (thresholds, weights) is baked into code; user settings live for one request | Versionable configuration; savable weight profiles | 1 |
| 2 | The metric system (definitions, values, weights — already in the DB) is only accessible to the platform | Author metrics: creation, moderation, publication, subscriptions, forks | 3–4 |
| 3 | The content core (countries, sources, signals) is only populated by the owner | Curated community contribution: proposing and populating countries through a formal onboarding standard | 5 |

Important: **the three current countries (Russia, Uruguay, Argentina) are a test set** for manually verifying the mechanics, not product coverage. The long-term model is many countries, populated by the community through a curated pipeline. Owner decision: the test set **is never deleted** — after Episode 5 it is hidden from public surfaces and preserved as a restorable demo dataset (fixtures + a dev restore tool).

---

## 2. Human-centeredness: the role of people vs. the role of AI

The owner's principle: the platform is a space for human work and creativity; neural networks are tools, not the core.

This principle is already honored architecturally, and locked in by invariants:

- The AI provider sits behind a seam, fake-by-default; a real model is a configuration switch.
- The assistant's answers come only from published content, with citations; with no context, it refuses.
- AI drafts land in a review queue and never touch public data without a human.
- Q&A consensus is computed as transparent statistics; AI never ranks people's answers.

Product consequence: the AI section is positioned as **"analysis tools"** (explain a number, check assumptions, draft a checklist), not "an assistant that knows the answer." Every AI output is marked and human-editable.

The kind of human creativity that matters in this niche is **analytical methodologies, routes, and structured experience**: an author metric with a "how it's computed" description, a route template with steps, a relocation story with a verification status. That's exactly the content the platform helps people create, find, and verify.

---

## 3. Audience

Six primary groups (detailed research lives in [../research/market/](../research/market/00-index.md), [../research/migration/](../research/migration/00-overview-and-sources.md)):

1. **Middle-class relocators** — where legalization is easier, cost of living, risks, the path to status.
2. **Digital nomads / remote workers** — the legal basis for staying, visas, taxes, banking, renewals.
3. **Skilled professionals** — work visas, qualification recognition, family, the trajectory to permanent residency.
4. **Families with children** — safety, healthcare, schools, rule stability.
5. **Entrepreneurs and the self-employed** — registration, taxes, banks, currency controls, stability.
6. **Investors / a second status** — investment programs, reliability, legal risks.

A key priority insight: the most motivated and underserved group is someone who has **already chosen** a country and is 3–6 months into the relocation process itself (documents, deadlines, accounts, transit). The personal surface (the planner) is built for this person — the source of daily return visits.

Two target usage cycles:

- **Consumer**: opened a plan → checked off steps → saw "what changed" for their countries → got a reminder → asked the community a question.
- **Creator**: updated their metric's values → answered a Q&A question → published a route template → checked their subscriber count.

---

## 4. Differentiation

Competitors (Nomad List, Numbeo, VisaGuide, InterNations, forums/Telegram) give either numbers with no provenance or unstructured opinions. None of them combine:

1. a source-backed core with a versioned methodology and data-quality control;
2. author methodologies with subscriptions and a fork lineage (a network effect that money can't copy);
3. a personal relocation plan tied to the core data (warnings from legal signals and country-pair compatibility);
4. a data loop: "planned → relocated → a structured story → data for the next person."

Unique core mechanics (already implemented): Country Drift (the direction a country is moving), Trust Score (data trust per country), Contradiction Score (source contradictions), Decision Passports (a decision as a reproducible document), origin-aware decisions (origin/destination country-pair compatibility).

---

## 5. Directions rejected

Locked in by an owner decision (2026-07-04), so they aren't revisited without an explicit review:

| Direction | Reason for rejection | What we do instead |
|---|---|---|
| Blockchain/cryptography | Doesn't solve a user problem; an arbiter (the platform) already exists | Audit events, sha256 hashes, methodology versions; signed passport exports if ever needed |
| A full messenger | A separate product; the moderation and safety burden is unmanageable; a scam magnet in a vulnerable niche | Lightweight threads on mutually accepted contacts + a Telegram deep link (linking already implemented) |
| Ticket/booking photo verification | Storing sensitive PII conflicts with the platform's privacy stance | Behavior-based confidence tiers (plan → activity → confirmed relocation), no documents |
| Rust/C++/PyTorch in the stack | The bottleneck is data and trust, not compute; a polyglot tax for a solo developer | "Postgres until the trigger fires" (an aggregate query stably >1s under real load); computation behind pure seams — replacing one module is a local change |

---

## 6. Moderation and autonomy (principles)

The owner doesn't plan to remain the sole editorial team; the goal is a platform minimally dependent on one person. A four-level autonomy principle has been adopted (the full model is in [rights-and-roles.md](../architecture/rights-and-roles.md)):

0. **Automation** — validation, PII scanning, rate limits, data-quality gates: filters out most problems before a human ever sees them.
1. **Community** — reports, transparent consensus, derived reputation, auto-hide thresholds.
2. **Moderators** — invited participants with limited, accountable rights; work only escalations and queues.
3. **Owner** — governance: appointing moderators, platform methodology versions, irreversible operations.

System health is measured by the share of decisions made with no human involvement, with no quality degradation.

---

## 7. Monetization (direction, not implementation)

Owner decisions (2026-07-04): operating jurisdiction — **Uruguay**; model — two-tier **donations**: (a) "support the platform" — voluntary, no privileges; (b) "thank the author" — a donation to a metric/template author with a platform fee. No paywalls on core data: trust is the product, and charging for data would destroy it. Timing is undefined and doesn't block the current line of work.

Until implementation, safety principles are locked into the invariants registry:

- money never buys rights, reputation, or search ranking;
- the payment provider connects through a seam (the same pattern as AI/Telegram), fake-by-default; integration happens in the integration tranche (§10);
- the data schema must not obstruct future donations: authorship and subscriptions (episodes 3–4) are a sufficient foundation; no separate "payment" tables are created before a provider is chosen.

User-generated content licensing (an owner decision): country data carries a non-exclusive, perpetual license to the platform; author methodologies get the author's choice at publish time (a platform license | CC BY-SA).

---

## 8. The cold start for the author surface

The owner will not be "author #1" (locked in). The launch strategy without them:

1. **Platform methodologies as a showcase of the mechanic**: the existing CII, Trust, and Drift are displayed in the same format future author metrics will use ("platform methodology, version, last updated") — a user sees a genre example before any authors exist.
2. **Templates from existing content**: published route checklists convert into the planner's first templates — author content exists from day one, with no authors.
3. **An invite-only early-author program**: invitations to active Q&A/board participants with high derived reputation; premoderation of methodologies at this stage.
4. Open author registration — after moderation has been tested and a moderator institution exists.

---

## 9. The autonomous-development period

Owner circumstances (2026-07-04): the next ~3–4 months — building out the foundation from the current location, then relocating to Uruguay, where real external connections become available. This implies an explicit development mode:

- **Everything that depends only on us happens now**: business logic, data, schemas, rights, fake modes — none of it is deferred.
- **No episode in line 1–7 depends on a real external service**: the LLM API, a live Telegram bot, email, payments, OAuth integrations are never connected. Everything is built and tested fully offline through existing fake seams.
- **Wherever a connection will eventually be needed, a seam is built now** (a provider abstraction, fake-by-default) — so that later, connecting it is a matter of configuration and keys, not development.
- Real connections are collected into a separate **integration tranche** (after the move): a real Telegram bot, a real LLM provider, a payment provider (Uruguay candidates: dLocal, Mercado Pago, PayPal), an email channel, OAuth, production hosting.

The architecture is already built for this: fake-by-default is an existing invariant, not a new idea; this mode just states explicitly that "real" mode stays off until the integration tranche.

## 10. What we're deliberately deferring (and when we'll return to it)

- **Frontend/visualization** — after the backend-line episodes, as a separate "visual tranche" (Drift, flows, infographics don't exist without a showcase — this is acknowledged debt, not forgotten work).
- **Mobile apps** — a PWA first, after the visual showcase.
- **Broad country coverage** — only through Episode 5's curated pipeline; quality over quantity.
- **OAuth integrations (Google Maps/Calendar)** — after an ICS/GeoJSON export closes the core value with no external dependency.
- **Synthetic user stories** — displaced by real ones as they accumulate (an owner decision); marking and quality control already make this safe.
- **A consultant marketplace** — the furthest horizon, a separate legal and trust model.
