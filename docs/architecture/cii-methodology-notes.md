> Founding methodology research notes (v1.0, 2026-06-21) — written before implementation started. Kept as the original research/reasoning record; **not** a description of the current system. For what is actually implemented (geometric aggregation, `cii_metric_definitions`, `scenario_metric_weights`, versioning), see [overview.md](overview.md) §3.3 and the [invariants registry](invariants.md) §1. Several specifics below (the exact dimension list, specific external providers) evolved during implementation.

================================================================================
  COUNTRY DECISION ATLAS
  Country Intelligence Index methodology:
  scientific foundations, unique metrics, implementation in the project
  Version: 1.0  |  Date: 2026-06-21
================================================================================


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  INTRODUCTION: THE FOUNDATION THE WHOLE METHODOLOGY RESTS ON
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

The primary reference we build on:

  OECD / EC Joint Research Centre
  "Handbook on Constructing Composite Indicators:
   Methodology and User Guide" (2008)
  Authors: Nardo, Saisana, Saltelli, Tarantola, et al.
  Free to access: https://www.oecd.org/sdd/42495745.pdf

This handbook is the de facto standard for every organization that builds
composite indices: the UN (HDI), the World Bank (WGI), the Economist
Intelligence Unit, the Heritage Foundation, Freedom House. All of them use
the same baseline principles described in this document.

A second key reference:

  UNDP Technical Notes — Human Development Index
  A description of HDI's methodology, including normalization and
  geometric aggregation
  https://hdr.undp.org/sites/default/files/2021-22_HDR/hdr2021-22_technical_notes.pdf

Why this matters for the project:
  When a user or partner asks "how do you compute your index" — you'll have
  a scientifically grounded answer citing UN and OECD methodology. That's
  trust. That's what sets us apart from competitors who compute things
  "intuitively."


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  PART 1. WALKING THROUGH EVERY QUESTION FROM BLOCK 0
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

──────────────────────────────────────────────────────────────────────────────
  QUESTION 1. The final list of Country Intelligence Index dimensions
──────────────────────────────────────────────────────────────────────────────

THE SCIENTIFIC APPROACH (OECD Handbook, Step 2: Selecting Variables):
  Variables must:
  • Be conceptually tied to the phenomenon being measured
  • Have adequate country coverage
  • Update regularly
  • Be reproducible (not subjective)
  • Not duplicate each other (checked via correlation analysis)

RECOMMENDED FINAL LIST (6 primary + 2 domain-specific):

  Group A: Stability and rule of law (the political foundation)
  ─────────────────────────────────────────────────────────
  1. Political Stability & Security
     Source: World Bank WGI (PV.EST)
     What it measures: the likelihood of government instability or
                   politically motivated violence, including terrorism
     Source range: -2.5 to +2.5 (normalized to 0–100)

  2. Rule of Law & Institutional Quality
     Source: World Bank WGI (RL.EST) + Transparency International CPI
     What it measures: judicial independence, contract enforcement,
                   corruption level
     Range: normalized 0–100

  Group B: Economy and livelihood
  ────────────────────────────
  3. Economic Freedom & Business Environment
     Source: Heritage Foundation Economic Freedom Index (Business Freedom)
               + World Bank Business Ready (formerly Doing Business)
     What it measures: ease of doing business, taxes, trade barriers
     Range: 0–100

  4. Affordability Index
     Source: Numbeo Cost of Living Index + World Bank PPP
     What it measures: relative cost of living (100 = world baseline,
                   lower = cheaper)
     Range: 0–200 (inverted during aggregation: lower = better)

  Group C: Quality of life
  ─────────────────────────
  5. Human Development & Quality of Life
     Source: UNDP Human Development Index (Education + Health + Income)
     What it measures: healthcare and education quality, income level
     Range: 0–1 (normalized to 0–100)

  Group D: Migrant-specific factors (a unique group)
  ──────────────────────────────────────────────────────
  6. Residency & Migration Accessibility
     Source: MIPEX + Henley Passport Index + internal legal signals
     What it measures: how easy it is to get a residency permit/permanent
                   residency, visa availability, bureaucratic barriers
     Range: 0–100 (partly filled in manually)

  Additional (add in phase 2, not MVP):
  7. Digital Infrastructure & Remote Work Readiness
     Source: ITU ICT Development Index + Ookla Speedtest
  8. Country Drift (computed from the rest — see question 7)

THE MVP SELECTION PRINCIPLE:
  Start with the 6 dimensions in groups A–D. They're covered by good sources
  and are enough for a convincing decision output. Add 7–8 later, once data
  exists.


──────────────────────────────────────────────────────────────────────────────
  QUESTION 2. 6 or 8 axes for the first spider chart
──────────────────────────────────────────────────────────────────────────────

THE SCIENTIFIC ANSWER (cognitive psychology):
  Miller's Law (1956): human working memory holds 7 ± 2 items.
  For visual items on a radar chart — even fewer, due to angular distortion.

  UI/UX research shows:
  • Up to 5 axes — reads well on any device
  • 6 axes — the optimal balance of information and readability
  • 7–8 axes — acceptable on desktop, poor on mobile
  • 9+ axes — the chart loses meaning, becomes visual noise

RECOMMENDATION:
  MVP: 6 axes (groups A–D from question 1)
  Desktop v2: 8 axes (add Digital Infrastructure + Drift)
  Mobile: always a maximum of 5–6 axes

  Technically: the component reads its axes from the API response and
  renders however many arrive. Don't hardcode the axis count in code.


──────────────────────────────────────────────────────────────────────────────
  QUESTIONS 3 AND 4. Which metrics are "higher = better," which are "higher = worse"
──────────────────────────────────────────────────────────────────────────────

THE SCIENTIFIC TERM: Polarity (indicator polarity)
Source: OECD Handbook, section 5.3, "Dealing with polarity"

THE RULE: every indicator must be brought to a single polarity BEFORE
aggregation. The standard is "higher = better." Metrics that need inverting
go through the formula: normalized_value = max - x (or 1/x for ratios).

THE POLARITY TABLE FOR OUR CII:

  Dimension                     Polarity        Reasoning
  ─────────────────────────────────────────────────────────────────────
  Political Stability          Higher = better  More stable is better
  Rule of Law                  Higher = better  Stronger institutions are better
  Economic Freedom             Higher = better  A freer economy is better
  Affordability Index          Higher = WORSE   A higher cost of living is worse
                               → INVERT during aggregation
  Human Development            Higher = better  HDI: higher is better by definition
  Residency Accessibility      Higher = better  More accessible residency is better
  Digital Infrastructure       Higher = better  Better connectivity is better
  Country Drift                Higher = better  A positive drift = improvement

HOW TO IMPLEMENT IN CODE:
  Add this field to the cii_metric_definitions table:
    higher_is_better BOOLEAN DEFAULT true

  Before aggregation:
    IF NOT higher_is_better:
      normalized_value = 100 - normalized_value
      -- or, for ratio metrics: normalized_value = 100 / raw_value


──────────────────────────────────────────────────────────────────────────────
  QUESTION 5. What default weights to use
──────────────────────────────────────────────────────────────────────────────

THE SCIENTIFIC APPROACH (OECD Handbook, chapter 6: Weighting):
  There are three standard weighting methods:

  Method 1: Equal Weighting
    Every dimension gets a weight of 1/N (for 6 dimensions, 0.167 each)
    Used by: most indices at launch
    Pros: transparent, easy to explain, no subjectivity
    Cons: assumes every dimension matters equally

  Method 2: Principal Component Analysis (PCA)
    A statistical method that derives weights itself, from the
    correlations between variables
    Used by: the Environmental Performance Index (Yale)
    Pros: the data determines the structure
    Cons: hard to explain to a user, needs data across 30+ countries

  Method 3: Analytic Hierarchy Process (AHP)
    Experts rank the pairwise importance of dimensions
    Used by: many government indices
    Pros: expert judgment made explicit
    Cons: subjective, depends on which experts are chosen

RECOMMENDATION FOR THE PROJECT:

  MVP phase: Equal Weighting (method 1)
    All 6 dimensions = weight 0.167 each
    Honest and transparent. Document it explicitly: "equal weights, v1.0"

  Phase 2: Scenario-Adjusted Weighting
    Different weights for different scenarios. This is our main UX win:

    "Relocation / Residency" scenario:
      Residency Accessibility   0.35  ← the top priority for this scenario
      Political Stability       0.20
      Affordability             0.20
      Rule of Law                0.10
      Human Development         0.10
      Economic Freedom          0.05

    "Business / Self-Employment" scenario:
      Economic Freedom           0.35  ← the top priority for this scenario
      Rule of Law                 0.25
      Political Stability        0.15
      Digital Infrastructure     0.15
      Affordability              0.05
      Residency Accessibility    0.05

    "Safety / Political Risk" scenario:
      Political Stability        0.45  ← the top priority for this scenario
      Rule of Law                 0.30
      Human Development          0.15
      Affordability               0.05
      Economic Freedom           0.03
      Residency Accessibility    0.02

    And so on for each of the 5 scenarios. Weights live in the database
    (in the scenario_metric_weights table), not in code.

  Phase 3 (future): User-Adjusted Weighting
    The user moves importance sliders themselves.
    "Safety matters more to me than cost of living."
    CII recomputes in real time.

HOW TO IMPLEMENT IN CODE:
  The scenario_metric_weights table:
    scenario_id  UUID
    metric_id    UUID
    weight       NUMERIC  -- 0 to 1, sums to 1.0 per scenario
    version      VARCHAR  -- 'v1.0', so it can change without losing history


──────────────────────────────────────────────────────────────────────────────
  QUESTION 6. How to compute a country's overall index (aggregation)
──────────────────────────────────────────────────────────────────────────────

THE SCIENTIFIC APPROACH:
  Two standard aggregation methods:

  Method 1: Linear aggregation (a weighted average)
    CII = Σ(weight_i × normalized_score_i)
    Used by: most indices
    Pro: simple, easy to understand
    Con: compensatory — a very high score on one dimension can mask a
           catastrophically low score on another.
           Example: a wealthy but extremely dangerous country could get a
           high CII from its economy despite near-zero safety.

  Method 2: Geometric aggregation
    CII = Π(normalized_score_i ^ weight_i)
    Used by: UNDP HDI (since 2010)
    Pro: NOT compensatory — a low score on any dimension pulls the whole
           index down. More honest for decision-making.
    Con: harder to explain, sensitive to zeros (needs a safeguard)

RECOMMENDATION:
  Use GEOMETRIC aggregation, the way UNDP HDI does.
  This is methodologically stronger and more honest for decisions about
  someone's life.

  Formula:
    CII(country, scenario) =
      (S1^w1 × S2^w2 × S3^w3 × S4^w4 × S5^w5 × S6^w6) ^ (1/Σwi)

  Where Si = the normalized score for dimension i (0–100)
      wi = the weight of dimension i for this scenario

  IMPORTANT: if any Si = 0, the geometric mean = 0.
  A zero safeguard is needed:
    protected_score = max(Si, 0.01)
  Or use a normalization floor of 1, not 0.

HOW TO IMPLEMENT IN CODE:
  A CIIScoreAggregator service:
    1. Fetch every dimension's normalized score for the country
    2. Apply polarity (invert where higher_is_better = false)
    3. Fetch the weights for this specific scenario
    4. Apply the geometric aggregation formula
    5. Round to 1 decimal place
    6. Write to country_cii_scores with the formula_version_id


──────────────────────────────────────────────────────────────────────────────
  QUESTION 7. How to compute Country Drift
──────────────────────────────────────────────────────────────────────────────

THE SCIENTIFIC APPROACH:
  Country Drift is the rate of change of the composite index over time.
  In financial analysis, the analogue is a momentum indicator.
  In statistics, it's the first difference of a time series.

THE FORMULA (a three-year rolling window):

  Drift(country, year) =
    CII(country, year) - CII(country, year-3)

  A three-year window was chosen because:
  • Year-over-year changes carry a lot of noise (elections, crises)
  • A five-year window reacts too slowly
  • Three years is the standard in political science for assessing a trend

NORMALIZING DRIFT:
  Drift is expressed in CII points (-100 to +100)
  Additionally, categorize it for the visual:

    > +10 points   = "Actively improving" (green 🚀)
    +3 to +10       = "Moderate improvement" (light green ↗)
    -3 to +3        = "Stagnant" (gray →)
    -10 to -3       = "Moderate decline" (yellow ↘)
    < -10 points   = "Actively declining" (red 🔻)

AN EXTENDED VERSION (Acceleration):
  You can also compute the second derivative — the rate of change of the
  rate of change:
    Acceleration = Drift(year) - Drift(year-3)
  If Drift is positive and Acceleration is positive, the country is
  improving and that process is accelerating. A very strong signal.

HOW TO IMPLEMENT IN CODE:
  A CountryDriftCalculator:
    1. Check that CII scores exist for both year and year-3
    2. If there's no year-3 data → drift = null, show "N/A"
    3. Compute drift = CII(year) - CII(year-3)
    4. Compute acceleration = drift(year) - drift(year-3) if available
    5. Write to country_cii_scores.drift and .drift_acceleration


──────────────────────────────────────────────────────────────────────────────
  QUESTION 8. How to compute confidence
──────────────────────────────────────────────────────────────────────────────

THE SCIENTIFIC APPROACH (OECD Handbook, chapter 8: Uncertainty Analysis):
  Confidence is not a subjective "how sure are we" judgment.
  It's a formalized measure of data uncertainty.

  Three confidence components:

  Component 1: Data Freshness Score
    Data under 1 year old            → freshness = 1.0
    Data 1–2 years old                → freshness = 0.85
    Data 2–3 years old                → freshness = 0.65
    Data 3–5 years old                → freshness = 0.40
    Data over 5 years old             → freshness = 0.15

  Component 2: Source Reliability Score
    An official source (UN, World Bank, government)     → reliability = 1.0
    A respected independent institution                 → reliability = 0.90
    An expert legal/tax firm                             → reliability = 0.75
    Media / journalistic investigation                   → reliability = 0.55
    Community / forum / Reddit                           → reliability = 0.35
    Synthetic / AI-generated data                         → reliability = 0.10

  Component 3: Coverage Score
    A metric computed from 3+ sources                    → coverage = 1.0
    From 2 sources                                        → coverage = 0.80
    From 1 source                                         → coverage = 0.60
    An expert judgment call (no formal source)            → coverage = 0.30

  THE OVERALL CONFIDENCE FORMULA:
    Confidence(metric) = freshness × reliability × coverage

    Example:
      Data that's 2 years old (0.65) × a World Bank source (1.0) × 1 source (0.60)
      = 0.65 × 1.0 × 0.60 = 0.39  → low confidence, needs an update

  THE OVERALL CII CONFIDENCE (aggregation):
    DON'T take the average! Use a weighted minimum:
      CII_confidence = Σ(weight_i × confidence_i)
    Plus: if any confidence_i < 0.30 → show a warning,
    "Some data needs verification"

HOW TO IMPLEMENT IN CODE:
  In country_metric_values:
    freshness_score   NUMERIC(3,2)
    reliability_score NUMERIC(3,2)
    coverage_score    NUMERIC(3,2)
    confidence        NUMERIC(3,2)  -- a computed product of the three

  Recompute freshness automatically on any data update
  (a database function or a service).


──────────────────────────────────────────────────────────────────────────────
  QUESTION 9. What data do we enter manually for now
──────────────────────────────────────────────────────────────────────────────

ENTER MANUALLY AT MVP (no good automatic source exists):

  1. Residency & Migration Accessibility
     MIPEX has no open API. Henley is a once-a-year dataset.
     A real assessment of residency accessibility depends heavily on
     details that can't be captured in a single number.
     → Enter manually through the admin panel, cite MIPEX + Henley.

  2. Legal Signal Impact Scores
     Every legal signal has an impact_level and an impact_direction.
     This is an editorial judgment, not an algorithm.
     → Enter manually, with a mandatory source link.

  3. User Story Verification Status
     Verifying a user story can't be automated.
     → Manually, by an editor.

  4. Scenario Weights (until PCA is implemented)
     At MVP — the product team sets weights manually.
     → Through admin, with a version recorded.

  5. Affordability Details for specific cities
     Numbeo is paid. Moscow's cost of living ≠ Ufa's ≠ Sochi's.
     → At MVP, use World Bank PPP as a rough estimate, detail it manually
       for priority countries.


──────────────────────────────────────────────────────────────────────────────
  QUESTION 10. Which external sources are we deferring
──────────────────────────────────────────────────────────────────────────────

DEFERRED (reasons noted):

  Numbeo API (~$50/mo)
    Deferred because: it's paid, and World Bank PPP is enough for MVP.
    When to connect it: once there are users and detail is needed.

  Economist Intelligence Unit (EIU)
    Deferred because: very expensive ($5,000+/year).
    When to use it: never as a direct source. Use its public reports as
    an editorial reference.

  Henley Passport Index (detailed data)
    Deferred because: no API, only a quarterly CSV.
    When to connect it: during the auto-ingestion phase, not critical for MVP.

  Speedtest Global Index (Ookla)
    Deferred because: needed for Digital Infrastructure, which isn't MVP.
    When to connect it: when adding the 7th CII dimension.

  Social media sentiment (Reddit, Telegram)
    Deferred because: requires NLP, scraping, AI. That's phase 4+.
    When to connect it: once the project has an AI layer.

CONNECT NOW (free, stable):

  World Bank Open Data API → Political Stability, Rule of Law, Economic
  UNDP HDI API             → Human Development
  Transparency Intl CPI   → a Rule of Law component (annual CSV)
  Heritage Foundation EFI → Economic Freedom (annual CSV)
  Freedom House            → a Political Stability component (annual CSV)


──────────────────────────────────────────────────────────────────────────────
  QUESTION 11. What to show first on the country card
──────────────────────────────────────────────────────────────────────────────

THE SCIENTIFIC APPROACH (UX research, F-pattern / Z-pattern eye-tracking):
  Nielsen Norman Group research shows: a user spends the first 2 seconds
  looking at the upper-left corner, then follows an F-pattern.

  The "Above the Fold" principle — the most valuable real estate.

  What must sit above the scroll line:
  • One big number (the overall CII score)
  • One visual element (a spider chart or a Drift badge)
  • 2–3 key metrics as numbers with icons

RECOMMENDED ORDER on the country card:

  Block 1 (above the fold):
    → Country name + flag
    → CII Score: a big number (e.g. "67 / 100")
    → Country Drift badge: 🚀 +12 "Actively improving"
    → Spider chart: all 6 axes in one glance
    → 3 "hero metrics": Cost of living / Residency difficulty / Safety

  Block 2 (after scroll):
    → Scenario Scores: horizontal bars across 5 scenarios
    → Drift Timeline: a 5-year sparkline
    → The latest legal signals (3 of them)

  Block 3 (behind "Read more"):
    → The full text profile
    → All sources and evidence
    → User stories

WHY THE SPIDER CHART FIRST:
  The radar chart is an instant country profile. In one second, a user sees
  whether a country is uniformly strong or has critical gaps. Text can't
  convey that as fast.


──────────────────────────────────────────────────────────────────────────────
  QUESTION 12. What to show on the decision page
──────────────────────────────────────────────────────────────────────────────

THE SCIENTIFIC APPROACH (Decision Science, Tversky & Kahneman):
  People are bad at evaluating absolute values but good at reading relative
  comparisons. "67 out of 100" is abstract.
  "Uruguay beats Russia on safety by 3.5x" is concrete.

  Principle: the decision page should give a RELATIVE comparison, not a
  set of absolute numbers.

RECOMMENDED STRUCTURE:

  Part 1 — The visual verdict (above the fold):
    → Two spider charts overlaid (each country a different color)
    → A winner banner: "For the Relocation/Residency scenario: Uruguay 74 vs Russia 42"
    → A confidence indicator: "High confidence / 3 sources"

  Part 2 — The dimension-by-dimension breakdown:
    → A grouped bar chart: a bar per country, side by side, for each dimension
    → A 🏆 badge on the winner in each dimension
    → The point-value gap (+/- X)

  Part 3 — Decision factors:
    → Country A's strengths (3–5 points)
    → Country A's weaknesses
    → Risk Warnings (critical legal signals)

  Part 4 — Sources (the third level):
    → Behind a click: where the data for each conclusion came from


──────────────────────────────────────────────────────────────────────────────
  QUESTION 13. Build the world map now or later
──────────────────────────────────────────────────────────────────────────────

ARGUMENTS FOR "NOW":
  + It's the main entry point and the most impressive element
  + Technically simple: react-simple-maps + data from the API
  + Countries with no data just show up gray — that's honest

ARGUMENTS FOR "LATER":
  - At MVP only 2 countries have data — the map would be almost entirely gray
  - That creates a false impression of an empty product
  - Development time is better spent on the spider chart

RECOMMENDATION:
  Build it in Phase 2, not MVP. At launch, it's better to:
  → Focus on the quality of the Russia and Uruguay cards
  → A spider chart delivers more value at 2 countries than an empty map does
  → Launch the map once there are 10+ countries with data


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  PART 2. UNIQUE METRICS NOBODY ELSE HAS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Every standard index (WGI, HDI, GPI, EFI) measures a country's current
state. None of our competitors measure what's described below. This is our
potential moat — unique analytical products.


──────────────────────────────────────────────────────────────────────────────
  UNIQUE METRIC 1: Legal Velocity Index (LVI)
──────────────────────────────────────────────────────────────────────────────

WHAT IT MEASURES:
  The rate of legislative change. A country whose laws change too fast is
  risky for long-term planning, even if the current laws are good.

  A paradox nobody measures: a country with improving laws but high
  volatility is still a poor choice for a long-term life, because it's
  unpredictable.

FORMULA:
  LVI(country, year) =
    count(legal_signal_events in that year) / a historical baseline

  Where baseline = the average number of changes over the past 5 years.

  LVI = 1.0  → a normal rate of change
  LVI > 2.0  → legislative instability (twice the normal rate)
  LVI < 0.5  → legislative freeze (very few changes)

NORMALIZATION:
  The optimal range: 0.5–1.5 (steady reform without chaos)
  Inverted: LVI far from 1.0 in either direction = worse

  Score = 100 × e^(-|LVI - 1.0| × 2)  -- a bell-shaped curve
  At LVI = 1.0 → Score = 100 (ideal)
  At LVI = 0.0 or 2.0 → Score → 0

HOW TO USE IT IN THE PROJECT:
  Data source: our own legal_signal_events table
  (no external API needed — computed from our own data!)

  Show it on: the country card's Risk Indicators block
  Show it on: the decision page's Stability Risk block
  Unique copy: "Legislation is changing 2.3x faster than normal"


──────────────────────────────────────────────────────────────────────────────
  UNIQUE METRIC 2: Expat Reality Gap (ERG)
──────────────────────────────────────────────────────────────────────────────

WHAT IT MEASURES:
  The gap between what official indices say and what people who actually
  relocated experience.

  This is a metric that, by construction, can't be computed without user
  stories. That's what makes it unique to our platform.

  Example: a country's official Rule of Law score = 72/100.
  But entrepreneurs who relocated there describe corruption as a serious
  problem in their user stories. ERG = the gap between these two data
  points.

FORMULA:
  ERG(country, dimension) =
    official_score(dimension) - user_experience_score(dimension)

  user_experience_score is computed as the average rating across user
  stories relevant to that dimension (from the scenario + outcome +
  problems fields)

  ERG = 0    → official data matches reality
  ERG > +15  → official data is inflated ("looks good on paper, isn't in practice")
  ERG < -15  → the country is better than official indices suggest

NORMALIZATION:
  Absolute ERG Score = |ERG| / 100  (how large the gap is)
  ERG direction = the sign (official data over- or under-stated)

HOW TO USE IT IN THE PROJECT:
  Show it as a "Reality Check" indicator on the country card:
    "⚠️ Official data may be inflated: an 18-point gap"
    "✅ The data matches relocated users' real experience"

  Source: our own user stories + official scores
  (again: no external API needed, computed from our own data!)

  As user stories accumulate, the metric gets more precise. This is an
  incentive for users to add their own stories.


──────────────────────────────────────────────────────────────────────────────
  UNIQUE METRIC 3: Bureaucracy Friction Score (BFS)
──────────────────────────────────────────────────────────────────────────────

WHAT IT MEASURES:
  The real time and cost of getting through the key procedures a migrant
  faces. The standard "Ease of Doing Business" measures business
  procedures. We measure the procedures that matter specifically to
  someone relocating.

THE PROCEDURE SET:
  1. Time to get an initial entry visa/permit (days)
  2. Time to get a residency permit after entry (days)
  3. Number of documents required for residency
  4. Number of agencies that must be visited
  5. Whether digital procedures exist (online vs. offline)
  6. Average total process cost (USD)
  7. Whether legal assistance is needed (yes/no)
  8. Time to open a bank account as a non-resident (days)

FORMULA:
  Each procedure is normalized against a global min-max.
  BFS = the average normalized value, inverted (lower = better).

HOW TO USE IT IN THE PROJECT:
  Source: entered manually through admin, updated rarely (once a year)
  Confirmed by: links to official immigration-agency websites

  Show it as: "Bureaucracy score: 3.2/10" + a step-by-step breakdown
  This is concrete and actionable — a user understands what's coming.


──────────────────────────────────────────────────────────────────────────────
  UNIQUE METRIC 4: Openness Momentum (OM)
──────────────────────────────────────────────────────────────────────────────

WHAT IT MEASURES:
  If Country Drift is the rate of change (the first derivative), Openness
  Momentum is the acceleration (the second derivative).

  A physics analogy:
    CII score      = position
    Country Drift  = velocity
    OM             = acceleration

  A finance analogy: MACD (Moving Average Convergence Divergence)

FORMULA:
  OM(country, year) = Drift(year) - Drift(year-3)

  OM > 0: the country is improving and that process is accelerating → "picking up speed"
  OM = 0: the country is improving, but at a steady rate → "steady growth"
  OM < 0: the country is declining and the decline is accelerating → "in free fall"

  ESPECIALLY VALUABLE COMBINATIONS:
    Drift > 0 and OM > 0: the country is accelerating → the best time to relocate
    Drift > 0 and OM < 0: the country is improving but slowing → a peak has been reached
    Drift < 0 and OM > 0: the decline is slowing → a possible turnaround
    Drift < 0 and OM < 0: the decline is accelerating → a dangerous signal

HOW TO USE IT IN THE PROJECT:
  Show it as an additional indicator next to the Drift badge:
    🚀 Drift +12 / Momentum ↑ "Accelerating"
  Or a warning:
    ⚠️ Drift +8 / Momentum ↓ "The rate of improvement is slowing"

  Source: computed from country_cii_scores (our own data)


──────────────────────────────────────────────────────────────────────────────
  UNIQUE METRIC 5: Contradiction Score (CS)
──────────────────────────────────────────────────────────────────────────────

WHAT IT MEASURES:
  How much different sources contradict each other on the same topic.
  When an official site says one thing, a law firm says another, and user
  stories say a third.

  A high Contradiction Score means "the data on this country is unreliable,
  the situation is ambiguous, we recommend double-checking."

FORMULA:
  CS(country, topic) =
    std_dev(scores across different sources on one topic) / the max possible spread

  The higher the standard deviation across sources, the higher the CS.

  CS = 0.0–0.2  → sources agree → high trust
  CS = 0.2–0.5  → moderate disagreement → check the details
  CS > 0.5      → serious contradictions → a red flag

HOW TO USE IT IN THE PROJECT:
  Source: our evidence_items + user_stories tables
  (the contradicts_evidence_id field, which we already planned for)

  Show it as: an indicator on the country card
    "⚠️ Sources contradict each other on taxation"
    [See details] → a list of the sources that contradict each other

  This is one of the most unique features — no competitor shows a user
  when the data contradicts itself.


──────────────────────────────────────────────────────────────────────────────
  UNIQUE METRIC 6: Scenario-Specific Risk Score (SSRS)
──────────────────────────────────────────────────────────────────────────────

WHAT IT MEASURES:
  Standard indices give a single risk score for the whole country.
  But the risk for a digital nomad is fundamentally different from the
  risk for a family with children or for an investor.

  SSRS aggregates only the legal signals and evidence items tagged as
  affecting a specific group.

FORMULA:
  SSRS(country, scenario) =
    Σ(impact_level × recency_weight) for legal_signals
    where affected_groups CONTAINS scenario_group

  Where recency_weight:
    A signal from the last 6 months  → weight = 1.0
    A signal 6–18 months old         → weight = 0.7
    A signal 18–36 months old        → weight = 0.4
    A signal older than 3 years      → weight = 0.1

HOW TO USE IT IN THE PROJECT:
  Source: our own legal_signals with an affected_groups field (already there)
  No external API needed — computed from our own data.

  Show it on the decision page:
    "For your scenario (Relocation/Residency): Risk Score 7.2/10"
    "Main risks: [a list of relevant legal signals]"

  This directly answers the user's question, "so how risky is this for me specifically?"


──────────────────────────────────────────────────────────────────────────────
  UNIQUE METRIC 7: Cross-Border Life Compatibility (CBLC)
──────────────────────────────────────────────────────────────────────────────

WHAT IT MEASURES:
  How easy it is to keep ties to your home country after relocating.
  A question NO existing index asks.

  Many people relocate but want to: visit home regularly, keep accounts
  there, maintain business ties. For them, "origin country + destination
  country" compatibility is critically important.

COMPONENTS:
  1. Visa-free / easy return (can you easily go back home)
  2. Banking compatibility (can you keep accounts in both countries)
  3. Tax treaty existence (is there a double-taxation treaty)
  4. Flight connectivity (direct flights and frequency)
  5. Time zone difference (for remote work)
  6. Internet call quality (can you video call without restrictions)

FORMULA:
  CBLC(origin, destination) =
    a weighted average of the 6 components, normalized to 0–100

A DISTINCT FEATURE:
  This is a pairwise metric — it depends on a PAIR of countries, not one.
  Every (origin, destination) pair has its own CBLC.

HOW TO USE IT IN THE PROJECT:
  Source: partly our own data, partly Henley + public registries
  Show it on: the decision page, once the user has entered an origin country
    "For citizens of Russia → Uruguay: compatibility 62/100"
    "⚠️ No direct flights. ✅ A tax treaty exists."

  This makes the decision engine personalized — the result depends on
  exactly where the user is relocating from.


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  PART 3. HOW TO ROLL ALL OF THIS INTO THE PROJECT PROPERLY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

──────────────────────────────────────────────────────────────────────────────
  3.1 THE LAYERED ROLLOUT PRINCIPLE
──────────────────────────────────────────────────────────────────────────────

Don't roll everything out at once. Order matters:

  LAYER 0 — Data (the absolute priority):
    No data, no metrics. No metrics, no visuals.
    First, fill the database with at least basic values by hand.
    Only then build visualizations.

  LAYER 1 — Standard metrics (CII from external indices):
    Political Stability, Rule of Law, Economic Freedom, HDI, Affordability
    Sources: World Bank, UNDP, Heritage — all free.
    This is what makes CII credible and comparable.

  LAYER 2 — Platform-specific metrics:
    Residency Accessibility (manual), Country Drift (computed),
    Legal Velocity Index (from our own legal signals).
    No external API needed — computed from our own data.

  LAYER 3 — Unique metrics (our differentiator):
    Expat Reality Gap, Contradiction Score, SSRS, CBLC.
    They come online as user stories and evidence accumulate.
    Launch them only once there's enough data to compute them.

  LAYER 4 — AI-enhanced metrics (the future):
    Automatic contradiction detection, NLP sentiment from forums,
    automatic classification of legal signals by affected group.


──────────────────────────────────────────────────────────────────────────────
  3.2 THE TABLE SCHEMA FOR THE ENTIRE METRIC SYSTEM
──────────────────────────────────────────────────────────────────────────────

  -- The registry of all metrics (extensible without ALTER TABLE)
  CREATE TABLE cii_metric_definitions (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    slug             VARCHAR UNIQUE NOT NULL,   -- 'political_stability'
    name_en          VARCHAR NOT NULL,
    name_ru          VARCHAR,
    description_en   TEXT,
    category         VARCHAR,   -- 'stability', 'economy', 'lifestyle', 'unique'
    metric_type      VARCHAR,   -- 'standard', 'computed', 'unique_platform'
    higher_is_better BOOLEAN DEFAULT true,
    value_min        NUMERIC DEFAULT 0,
    value_max        NUMERIC DEFAULT 100,
    data_source      VARCHAR,   -- 'world_bank_wgi', 'computed', 'manual'
    update_frequency VARCHAR,   -- 'annual', 'quarterly', 'real_time'
    is_active        BOOLEAN DEFAULT true,
    display_order    INT,
    introduced_in    VARCHAR,   -- 'v1.0', 'v1.1' — which version added it
    created_at       TIMESTAMPTZ DEFAULT now()
  );

  -- Metric values per country and year
  CREATE TABLE country_metric_values (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    country_id       UUID REFERENCES countries(id) ON DELETE RESTRICT,
    metric_id        UUID REFERENCES cii_metric_definitions(id),
    year             INT NOT NULL,
    value            NUMERIC(7,3),   -- normalized 0–100
    raw_value        NUMERIC(10,4),  -- the original value from the source
    raw_unit         VARCHAR,        -- '%', 'score', 'days', 'USD'
    freshness_score  NUMERIC(3,2) DEFAULT 1.0,
    reliability_score NUMERIC(3,2) DEFAULT 1.0,
    coverage_score   NUMERIC(3,2) DEFAULT 1.0,
    confidence       NUMERIC(3,2) GENERATED ALWAYS AS
                       (freshness_score * reliability_score * coverage_score) STORED,
    source_id        UUID REFERENCES sources(id),
    ingestion_method VARCHAR,  -- 'api', 'manual', 'computed', 'csv_import'
    ingested_at      TIMESTAMPTZ DEFAULT now(),
    ingested_by      VARCHAR,  -- 'world_bank_ingester', 'admin:user_name'
    notes            TEXT,
    deleted_at       TIMESTAMPTZ NULL,
    UNIQUE (country_id, metric_id, year)
  );

  -- Metric weights per scenario (different weights for different scenarios)
  CREATE TABLE scenario_metric_weights (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    scenario_id  UUID REFERENCES scenarios(id),
    metric_id    UUID REFERENCES cii_metric_definitions(id),
    weight       NUMERIC(4,3) NOT NULL,  -- 0.000–1.000
    formula_version VARCHAR NOT NULL,   -- 'v1.0', 'v1.1'
    effective_from DATE NOT NULL,
    effective_to   DATE NULL,           -- NULL = the current version
    created_at     TIMESTAMPTZ DEFAULT now(),
    UNIQUE (scenario_id, metric_id, formula_version)
  );

  -- Final CII scores (a cache of aggregated values)
  CREATE TABLE country_cii_scores (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    country_id        UUID REFERENCES countries(id),
    scenario_id       UUID REFERENCES scenarios(id) NULL, -- NULL = overall
    year              INT NOT NULL,
    cii_score         NUMERIC(5,2),   -- the final 0–100 score
    cii_confidence    NUMERIC(3,2),   -- aggregated confidence
    country_drift     NUMERIC(6,2),   -- delta vs. year-3
    drift_acceleration NUMERIC(6,2),  -- delta drift vs. the previous period
    formula_version   VARCHAR,
    calculated_at     TIMESTAMPTZ DEFAULT now(),
    UNIQUE (country_id, scenario_id, year)
  );

  -- Platform-unique metrics (stored separately)
  CREATE TABLE country_platform_metrics (
    id                     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    country_id             UUID REFERENCES countries(id),
    year                   INT,
    legal_velocity_index   NUMERIC(5,3),  -- LVI
    contradiction_score    NUMERIC(4,3),  -- CS
    bureaucracy_friction   NUMERIC(5,2),  -- BFS
    openness_momentum      NUMERIC(6,2),  -- OM
    calculated_at          TIMESTAMPTZ DEFAULT now()
  );

  -- CBLC — for country pairs
  CREATE TABLE country_pair_compatibility (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    origin_id        UUID REFERENCES countries(id),
    destination_id   UUID REFERENCES countries(id),
    year             INT,
    cblc_score       NUMERIC(5,2),   -- 0–100
    tax_treaty       BOOLEAN,
    direct_flights   BOOLEAN,
    timezone_diff_h  INT,
    banking_compat   VARCHAR,  -- 'easy', 'moderate', 'hard'
    notes            TEXT,
    source_id        UUID REFERENCES sources(id),
    updated_at       TIMESTAMPTZ DEFAULT now(),
    UNIQUE (origin_id, destination_id, year)
  );


──────────────────────────────────────────────────────────────────────────────
  3.3 BACKEND SERVICE ARCHITECTURE
──────────────────────────────────────────────────────────────────────────────

  apps/api/app/services/metrics/
  ├── normalization_service.py       # min-max normalization, zero safeguards
  ├── polarity_service.py            # inverting metrics with higher_is_better=false
  ├── aggregation_service.py         # geometric aggregation
  ├── confidence_service.py          # confidence from the three components
  ├── drift_calculator.py            # Country Drift + Acceleration
  ├── cii_score_aggregator.py        # the main CII orchestrator
  │
  ├── unique_metrics/
  │   ├── legal_velocity_calculator.py   # LVI from legal_signal_events
  │   ├── reality_gap_calculator.py      # ERG from user_stories
  │   ├── contradiction_detector.py      # CS from evidence_items
  │   ├── scenario_risk_calculator.py    # SSRS from legal_signals
  │   └── cblc_calculator.py             # CBLC for country pairs
  │
  └── ingestion/
      ├── base_ingestion_provider.py     # the abstract base class
      ├── world_bank_provider.py         # World Bank API
      ├── undp_provider.py               # UNDP HDI
      ├── transparency_provider.py       # TI CPI (CSV)
      └── heritage_provider.py           # Heritage EFI (CSV)


──────────────────────────────────────────────────────────────────────────────
  3.4 API ENDPOINTS FOR THE VISUAL SYSTEM
──────────────────────────────────────────────────────────────────────────────

  GET /api/v1/countries/{slug}/cii
    → All CII metrics for the country (the current year)
    → Spider chart data: [{metric_slug, value, confidence, label}]
    → Country Drift + Acceleration
    → Scenario scores (all 5 scenarios)

  GET /api/v1/countries/{slug}/cii/history?years=5
    → Historical data for the Drift Timeline
    → [{year, cii_score, drift, metrics: {...}}]

  GET /api/v1/countries/compare?
        countries=russia,uruguay&scenario=relocation_residence
    → CII data for a group of countries in one request
    → For the spider overlay and the grouped bar chart

  GET /api/v1/world-map?scenario=relocation_residence&year=2026
    → A lightweight response: [{iso2, cii_score, drift}] for every country with data
    → Specifically optimized for the map (only the necessary fields)

  GET /api/v1/countries/matrix?
        countries=russia,uruguay,georgia&scenarios=all
    → A matrix for the heatmap: {[country_slug]: {[scenario_slug]: score}}

  GET /api/v1/metrics/definitions
    → The list of active metrics with names, category, display_order
    → The frontend uses this to build chart axes dynamically

  GET /api/v1/countries/{slug}/platform-metrics
    → The unique metrics: LVI, ERG, CS, BFS, OM


──────────────────────────────────────────────────────────────────────────────
  3.5 THE ROLLOUT ORDER FOR UNIQUE METRICS
──────────────────────────────────────────────────────────────────────────────

  STAGE 1 (MVP, now):
    ✓ Legal Velocity Index — computed from our own legal_signal_events
      Minimum data: 10+ legal signals per country
      Implementation: 1–2 days of backend work

    ✓ Scenario-Specific Risk Score — from our own legal_signals
      Depends on: the affected_groups field (already in the model)
      Implementation: 2–3 days backend + 1 day frontend

    ✓ Contradiction Score — from our own evidence_items
      Needs: adding a contradicts_evidence_id field to evidence_items
      Implementation: 2 days of backend work

  STAGE 2 (after 50+ user stories accumulate):
    ✓ Expat Reality Gap
      Depends on: enough user stories with ratings
      Needs: adding dimension_ratings fields to user_stories
      Implementation: 3–4 days

    ✓ Openness Momentum
      Depends on: 3+ years of data
      Implementation: 1 day (Drift already exists, needs a second derivative)

  STAGE 3 (after adding 5+ countries):
    ✓ Cross-Border Life Compatibility
      Depends on: country-pair data
      Needs: filling country_pair_compatibility manually for the top pairs
      Implementation: 3 days backend + 2 days frontend

  STAGE 4 (the future, with AI):
    ✓ Bureaucracy Friction Score (a detailed version, AI-validated)
    ✓ NLP-enhanced Reality Gap (from forums and reviews)


──────────────────────────────────────────────────────────────────────────────
  3.6 HOW TO PRESENT THE METHODOLOGY TO USERS
──────────────────────────────────────────────────────────────────────────────

Trust is the platform's main asset. Every metric must be transparent.

THE /methodology PAGE (add it later):
  • A description of every CII dimension
  • Data sources with links
  • Formulas (simplified, not mathematical notation)
  • The methodology's version history
  • How a user can report a data error

ON EVERY METRIC IN THE UI:
  An ℹ️ icon on hover/click → a tooltip:
    "Political Stability: World Bank Governance Indicators 2024 data.
     Covers: the likelihood of government instability and politically
     motivated violence. Updated annually. Confidence: 0.87"

EXPLICIT DISCLAIMERS:
  • "This data is an analytical estimate, not legal advice"
  • "Stale data is marked ⚠️"
  • "Synthetic data is marked 🔬"


━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  FINAL TABLE: EVERY METRIC AND ITS ROLLOUT PLAN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Metric                       Type         Source                 Stage
  ──────────────────────────────────────────────────────────────────────────
  Political Stability          Standard     World Bank WGI API     MVP
  Rule of Law                  Standard     World Bank + TI CPI    MVP
  Economic Freedom             Standard     Heritage EFI CSV       MVP
  Affordability Index          Standard     World Bank PPP API     MVP
  Human Development (HDI)      Standard     UNDP API               MVP
  Residency Accessibility      Standard     MIPEX + manual         MVP
  Country Drift                Computed     From CII scores        MVP
  ──────────────────────────────────────────────────────────────────────────
  Legal Velocity Index         Unique       Our legal signals      MVP
  Contradiction Score          Unique       Our evidence items     MVP
  Scenario-Specific Risk       Unique       Our legal signals      MVP
  Openness Momentum            Unique       From Drift             Stage 2
  Expat Reality Gap            Unique       Our user stories       Stage 2
  Bureaucracy Friction Score   Unique       Manual + sources       Stage 2
  Cross-Border Compatibility   Unique       Manual + public data   Stage 3
  Digital Infrastructure       Standard     ITU + Ookla            Stage 3
  ──────────────────────────────────────────────────────────────────────────

THE MAIN ROLLOUT PRINCIPLE:
  Three of the seven unique metrics (LVI, CS, SSRS) are computed from data
  the project ALREADY has — legal signals and evidence items. That means
  they can ship with no external API, no new sources, backend effort alone.
  High priority.

================================================================================
  END OF DOCUMENT
  Country Decision Atlas — Methodology & Unique Metrics v1.0
  Prepared: 2026-06-21
================================================================================
