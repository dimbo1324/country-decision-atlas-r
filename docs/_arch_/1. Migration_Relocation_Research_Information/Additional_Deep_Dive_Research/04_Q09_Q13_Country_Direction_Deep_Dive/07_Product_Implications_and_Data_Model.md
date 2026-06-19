# 7. Product Implications and Data Model

## 7.1. Strategic product implication

The platform should not compete only as a content site. It should compete as a **data-verification and decision-support infrastructure**.

Core positioning:

> A source-linked, timestamped, AI-assisted country decision platform that helps migrants, remote workers, families, students, specialists, entrepreneurs and investors compare countries by legal feasibility, cost, risk, quality of life and country direction.

## 7.2. Minimum data entities

Recommended canonical entities:

### Country

- country_id
- iso2 / iso3
- region
- income_level
- official_languages
- currency
- population
- migrant_stock
- government_type
- source_refs
- last_checked_at

### City

- city_id
- country_id
- population
- rent_range
- cost_living_estimate
- safety_signals
- expat_community_signals
- source_refs
- data_confidence

### LegalSignal

- signal_id
- country_id
- domain: visa / residence / PR / citizenship / tax / property / labour / family / business
- title
- summary
- legal_effect
- affected_personas
- effective_date
- published_date
- source_url
- source_type
- status: bill / adopted / in_force / suspended / court_blocked / amended / expired
- confidence
- last_checked_at

### VisaRoute

- route_id
- country_id
- route_type
- eligibility
- income_threshold
- proof_of_funds
- family_rights
- work_rights
- renewal
- PR_path
- citizenship_path
- tax_notes
- official_source_url
- last_checked_at

### Persona

- persona_id
- label
- budget_level
- income_type
- family_status
- profession
- passport_constraints
- target_timeline
- risk_tolerance
- important_dimensions

### ScenarioRun

- scenario_id
- user_inputs
- eligible_countries
- excluded_countries
- risk_flags
- cost_projection
- legal_path_projection
- country_direction_summary
- recommended_next_checks
- generated_at

### Source

- source_id
- title
- url
- publisher
- source_type
- jurisdiction
- reliability_tier
- update_frequency
- retrieved_at
- last_verified_at

### UserExperienceItem

- item_id
- country_id
- city_id
- persona_tags
- topic_tags
- text_summary
- source_type: interview / forum / review / survey
- date
- confidence
- moderation_status

## 7.3. Source reliability tiers

Recommended tiers:

| Tier | Source type | Use |
|---|---|---|
| A | Official law, official gazette, ministry, tax authority | Legal rule, effective date, eligibility |
| B | Official statistics / intergovernmental datasets | Migration, labour, safety, macro indicators |
| C | Institutional indexes | Direction, governance, risk comparisons |
| D | Expert interpretation | Explanation and practical implications |
| E | Commercial data/API | Cost, salary, housing, travel, market signals |
| F | Community/user data | Lived experience, warnings, practical friction |
| G | Anecdote/unverified social content | Hypothesis only, never legal source |

## 7.4. Confidence model

Each claim should receive a confidence label:

- **High confidence:** official source, current, direct, unambiguous.
- **Medium confidence:** reliable secondary source or official source requiring interpretation.
- **Low confidence:** community signal, anecdote, old source, unclear applicability.
- **Contradictory:** sources disagree or local practice differs from official rule.
- **Expired risk:** source older than threshold for that data type.

## 7.5. Update cadence

Recommended automatic review cycle:

| Field type | Review frequency |
|---|---:|
| visa eligibility | monthly for priority countries, quarterly otherwise |
| salary thresholds | monthly around policy windows, quarterly otherwise |
| tax regimes | monthly around budget season, quarterly otherwise |
| citizenship law | monthly if reform active, quarterly otherwise |
| property restrictions | quarterly; immediate on major housing reform |
| cost of living | monthly/quarterly depending on data source |
| rent data | weekly/monthly if listing-integrated |
| indexes | annual on new release |
| user experiences | continuous moderation |
| source health | automated link check weekly/monthly |

## 7.6. Feature priorities

### High priority MVP features

1. Source-linked country cards.
2. Visa/residence route table by persona.
3. Country comparison by user scenario.
4. Legal change tracker.
5. Cost after rent/tax estimate.
6. Source freshness labels.
7. Risk flags: tax, housing, processing, policy-change risk.
8. Community warnings by persona.
9. Official-source links.
10. Decision report export.

### Medium priority

1. AI chat with source references.
2. Timeline simulator for PR/citizenship.
3. Dynamic country-direction index.
4. Alerts for selected countries/routes.
5. User-submitted cost reports.
6. Expert marketplace / consultation referrals.
7. City-level expansion.

### Low priority at first

1. Generic travel content.
2. Beautiful but shallow rankings.
3. Social feed without evidence structure.
4. Unmoderated forums.
5. Lifestyle quiz without legal filtering.
6. News feed without legal classification.

## 7.7. What to learn next

To push this project toward a serious product, the next research layer should be:

1. Build a 30-country source map: official immigration, tax, property, citizenship, labour and law databases.
2. Create 8 persona profiles and assign weightings.
3. Run primary user interviews.
4. Test whether people trust source-linked AI summaries.
5. Prototype a country-card schema.
6. Build a legal-change ingestion workflow.
7. Validate willingness to pay for personal country reports.
8. Decide whether initial product should target one segment first: digital nomads, skilled workers, families, or investors.
