# MVP Blueprint and Stronger Product Format

## 1. Product concept

The product should be designed as a **country decision-support system**, not just a content website.

### Proposed product name category

- Country Decision OS
- Relocation Intelligence Platform
- Migration Evidence Atlas
- Country Fit & Legal Direction Platform
- Global Mobility Decision Platform

## 2. Core object model

### Main entities

1. **Country**
   - name;
   - region;
   - cities;
   - basic indicators;
   - country direction;
   - data confidence.

2. **City**
   - cost;
   - safety;
   - housing;
   - internet;
   - climate;
   - community;
   - work/business relevance.

3. **Route**
   - visa/residence type;
   - eligibility;
   - documents;
   - fees;
   - duration;
   - renewal;
   - family;
   - work;
   - PR/citizenship path.

4. **LegalSignal**
   - law/news/policy change;
   - source;
   - effective date;
   - affected routes;
   - affected personas;
   - before/after;
   - severity;
   - confidence.

5. **Source**
   - URL;
   - source type;
   - publication date;
   - last checked;
   - authority level;
   - language;
   - reliability score.

6. **EvidenceItem**
   - quote/summary;
   - source;
   - related country;
   - related route;
   - related claim.

7. **Persona**
   - skilled worker;
   - digital nomad;
   - entrepreneur;
   - investor;
   - student;
   - family;
   - retiree;
   - safety-seeker.

8. **ScenarioRun**
   - user inputs;
   - country scores;
   - route scores;
   - warnings;
   - next steps.

9. **UserStory**
   - anonymised case;
   - country/city;
   - route;
   - timeline;
   - budget;
   - documents;
   - outcome;
   - verification status.

## 3. MVP feature bundle

### Feature 1 — Country Cards

Each country card should include:

- “Best for” labels;
- route highlights;
- recent legal changes;
- affordability;
- family suitability;
- work/business suitability;
- citizenship path;
- risk flags;
- data confidence;
- last checked date.

### Feature 2 — Compare Countries

Minimum comparison fields:

- main routes;
- entry difficulty;
- residence difficulty;
- work rights;
- family rights;
- PR path;
- citizenship path;
- cost baseline;
- housing pressure;
- tax-risk flag;
- legal-change volatility;
- country-direction trend;
- data confidence.

### Feature 3 — Route Explorer

For each route:

- purpose;
- eligibility;
- income/salary;
- documents;
- stay period;
- renewal;
- family;
- work rights;
- tax warning;
- path to PR/citizenship;
- official source;
- last checked;
- common mistakes.

### Feature 4 — Law Impact Feed

For each legal signal:

- title;
- country;
- route/persona affected;
- effective date;
- before/after;
- practical impact;
- severity;
- official source;
- editor status.

### Feature 5 — Scenario Simulator

Input fields:

- nationality/passport group;
- income;
- income source;
- profession;
- family status;
- age range;
- target timeline;
- citizenship goal;
- business/investment goal;
- budget;
- language tolerance;
- risk tolerance.

Output:

- top countries;
- why;
- route options;
- red flags;
- missing data;
- next steps;
- sources.

### Feature 6 — Source Confidence System

Source levels:

- Level A: official government / law / regulator.
- Level B: international institution / official statistical body.
- Level C: recognised law firm / accounting firm / corporate mobility report.
- Level D: structured survey / platform database.
- Level E: community anecdote / forum / YouTube / Telegram.

Claim confidence:

- High: official + recent + cross-checked.
- Medium: reputable but not official / or older but still plausible.
- Low: anecdotal / old / unverified.
- Unknown: source insufficient.

## 4. MVP roadmap

### Phase 0 — Research and schema

- Define country schema.
- Define route schema.
- Define legal signal schema.
- Define source reliability model.
- Define scoring methodology.
- Select 10 countries.
- Create editorial workflow.

### Phase 1 — Static MVP

- Country cards.
- Compare page.
- Route explorer.
- Source index.
- Basic scoring.
- Manual country updates.

### Phase 2 — AI-assisted research

- AI extraction from official sources.
- AI summary drafts.
- AI contradiction detection.
- Editor approval queue.

### Phase 3 — User scenario engine

- Profile questionnaire.
- Scenario result page.
- Saved shortlists.
- Risk flags.
- Checklist generation.

### Phase 4 — Community evidence

- Structured user stories.
- Moderation.
- Route tagging.
- Case timelines.
- Verification badges.

### Phase 5 — Commercial layer

- Premium reports.
- Expert review.
- Lawyer/tax referral.
- Business relocation package.
- API / B2B country-risk feed.

## 5. Scoring methodology draft

### Country Fit Score

Suggested dimensions:

1. Legal feasibility — 25%
2. Economic feasibility — 20%
3. Long-term stability — 15%
4. Lifestyle fit — 15%
5. Family/social fit — 10%
6. Business/work opportunity — 10%
7. Data confidence — 5%

Weights should change by persona.

### Example: digital nomad weights

- Legal remote-work route — 25%
- Tax risk — 20%
- Cost of living — 20%
- Internet/work infrastructure — 10%
- Safety/lifestyle — 10%
- Healthcare/insurance — 5%
- Renewal/long-term option — 5%
- Community evidence — 5%

### Example: family weights

- Residence stability — 20%
- Healthcare — 15%
- Education/childcare — 15%
- Safety — 15%
- Cost/housing — 15%
- Spouse rights — 10%
- Citizenship path — 5%
- Data confidence — 5%

## 6. Competitive positioning

### Avoid

- “Best countries to move to” generic blog.
- Pure visa database.
- Pure expat forum.
- Pure AI chatbot.
- Pure ranking index.
- Pure cost calculator.

### Aim for

- evidence-backed;
- transparent;
- personal;
- dynamic;
- updated;
- practical;
- cautious;
- decision-oriented.

## 7. Product north star

The user should leave the platform with:

1. a shortlist;
2. a reasoned comparison;
3. legal route options;
4. risk warnings;
5. source links;
6. a first-step checklist;
7. clear “must verify with expert” items.
