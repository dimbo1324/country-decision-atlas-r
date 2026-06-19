# Data Model and Metrics for a Country-Choice Platform

This file translates the research into a possible analytical structure for a future platform.

## 1. Core entities

### Country

Fields:

- id
- name
- iso_code
- region
- population
- migrant_stock
- migrant_share
- official_language
- currency
- political_system
- source_ids
- last_checked_at

### City

Fields:

- id
- country_id
- name
- population
- cost_level
- rent_level
- safety_level
- healthcare_access
- internet_quality
- expat_density
- source_ids

### VisaRoute

Fields:

- id
- country_id
- route_type: work, student, family, startup, investor, digital_nomad, retirement, humanitarian
- eligibility_summary
- income_requirement
- salary_requirement
- savings_requirement
- family_inclusion
- work_rights
- path_to_pr
- path_to_citizenship
- dual_citizenship_allowed
- official_url
- effective_from
- last_checked_at
- change_risk

### LegalSignal

Fields:

- id
- country_id
- topic
- signal_type: tightening, opening, neutral, unclear
- law_or_policy_name
- summary
- affected_personas
- effective_date
- official_source_url
- confidence

### CommunitySignal

Fields:

- id
- country_id
- city_id
- platform
- language
- persona
- topic
- sentiment
- evidence_excerpt
- source_url_or_reference
- date_observed
- verification_status
- privacy_status

### ScenarioRun

Fields:

- id
- user_persona
- nationality
- income_type
- monthly_budget
- family_size
- target_goal: work, study, citizenship, tax, safety, business, retirement
- country_scores
- warnings
- recommended_next_steps

## 2. Core scoring dimensions

A serious platform should avoid a single universal “best country” score. Use persona-specific weighted scoring.

### Legal feasibility score

Measures whether the user can legally move and stay.

Inputs:

- visa eligibility;
- income/salary thresholds;
- document burden;
- refusal risk;
- route stability;
- family inclusion;
- renewal difficulty.

### Economic feasibility score

Measures whether the move makes financial sense.

Inputs:

- expected income;
- rent;
- taxes;
- healthcare;
- schooling;
- savings requirement;
- job-market access;
- currency risk.

### Integration score

Measures long-term adaptation difficulty.

Inputs:

- language difficulty;
- English availability;
- social openness;
- bureaucracy;
- migrant community;
- discrimination reports;
- cultural distance.

### Family suitability score

Inputs:

- safety;
- schools;
- healthcare;
- childcare;
- housing;
- spouse work rights;
- citizenship path for children.

### Business/investment score

Inputs:

- tax;
- company formation;
- banking;
- capital controls;
- rule of law;
- startup ecosystem;
- investor visa;
- IP protection.

### Direction/drift score

This is a unique product angle. Track whether a country is becoming more:

- open or closed to migrants;
- liberal or authoritarian;
- business-friendly or restrictive;
- low-tax or high-tax;
- safe or unsafe;
- expensive or affordable;
- family-friendly or difficult for families.

## 3. Confidence model

Every score should expose confidence:

- A: official, recent, clear;
- B: official but ambiguous or older;
- C: survey/market report;
- D: community signal supported by several examples;
- E: single anecdote or unverified claim.

## 4. Alert system

Users should be able to follow:

- country;
- visa route;
- tax rule;
- citizenship law;
- golden visa/investor route;
- digital nomad route;
- student route;
- family reunification;
- housing/property restrictions.

Alert examples:

- “Spain golden visa ended on 2025-04-03.”
- “Canada announced a target to reduce temporary residents to 5% of population.”
- “UK Skilled Worker route changed salary/skill requirements.”
- “New Zealand Active Investor Plus settings changed from 2025-04-01.”

## 5. MVP analytics dashboard

Minimum useful dashboard:

- Country shortlist by persona.
- Visa eligibility summary.
- Cost estimate by household type.
- Red flags.
- Official source links.
- Community pain points.
- Rule-change timeline.
- “What to verify next” checklist.

## 6. Why this matters

The strongest unmet demand is not another blog about “best countries”. It is a verified, personalised decision system that helps people avoid wrong moves, outdated rules and expensive mistakes.
