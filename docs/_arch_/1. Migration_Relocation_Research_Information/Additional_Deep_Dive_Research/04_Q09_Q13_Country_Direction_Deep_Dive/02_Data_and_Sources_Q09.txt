# 9. Data and Sources

## Key takeaways

- Competitors usually combine official datasets, crowdsourcing, editorial research, commercial APIs, partner content and user-generated experience.
- Crowdsourcing is useful for cost of living, neighbourhood feel, internet reliability and bureaucratic friction, but it is dangerous for legal, tax and visa rules.
- The best product practice is to separate data into source tiers: official law, official statistics, institutional index, expert interpretation, commercial dataset, community signal and anecdote.
- Every important field should have: source URL, source type, jurisdiction, effective date, last checked date, confidence level, update frequency and contradiction flag.

---

## 9.1. Where do competitors get data?

Relocation competitors normally build their databases from several layers:

1. **Official government and intergovernmental data.** Examples: national immigration portals, tax authorities, official gazettes, national statistical offices, Eurostat, OECD, UN DESA, IOM, UNHCR, World Bank and UNODC [S01–S08, S57].
2. **Crowdsourced price and experience data.** Examples: Numbeo, Expatistan and digital nomad communities collect user-submitted prices, rent estimates and local experience [S09–S12].
3. **Commercial datasets and APIs.** These may include cost-of-living APIs, air-quality APIs, weather/climate APIs, real-estate listings, salary aggregators, job boards and insurance/healthcare databases.
4. **Editorial and expert research.** Many relocation sites publish summaries of visas, golden visas, digital nomad permits, tax regimes, country guides and “best country” rankings. The quality varies widely depending on whether they cite official law and update dates.
5. **Community/user behaviour data.** Some platforms use profiles, trip logs, saved locations, reviews, comments, forum posts, check-ins, budget reports and member surveys.
6. **Partner data.** Banks, insurers, tax firms, immigration law firms, relocation companies and investment migration firms often provide country guides or route-specific explanations.

The competitor landscape is therefore not a data scarcity landscape. It is a **data trust and normalisation problem**.

## 9.2. Do they use official sources?

Some do, but unevenly. Serious immigration or investment-migration firms usually cite government portals, official gazettes or legal acts. General relocation products often summarise official rules without linking each claim to a primary source. Cost-of-living platforms generally do not rely primarily on official sources; they rely on user submissions, sometimes combined with market or official data.

For a high-trust platform, official sources should be the top tier:

- immigration ministries and border agencies;
- tax authorities;
- official gazettes;
- EUR-Lex and national law databases in Europe [S41–S42];
- official statistical agencies;
- central banks and finance ministries;
- official real-estate/property authorities;
- labour ministries and official job/occupation lists.

A product should never present a consultant blog as equal to an official source. Expert commentary can explain the rule, but the rule itself should be anchored in the primary source.

## 9.3. Do they use user data?

Yes, especially in consumer relocation, expat and digital-nomad products. User data appears as:

- cost-of-living entries;
- rent and grocery price reports;
- city reviews;
- internet speed reports;
- “safe/unsafe” perceptions;
- forum posts;
- visa experience comments;
- processing-time reports;
- quality-of-life survey answers;
- saved destinations and preference filters;
- travel calendars and residence-day tracking.

Nomads.com explicitly includes community and residence-calendar features; InterNations uses survey responses from expats; Numbeo and Expatistan rely on user-entered prices [S09–S15].

User data is valuable because official sources rarely answer questions like:

- How hard is it to rent an apartment as a foreigner?
- Do landlords demand local guarantors?
- How long does registration actually take?
- Are banks opening accounts for new migrants?
- Does the school accept foreign documents quickly?
- What neighbourhoods feel safe after dark?
- Is the digital nomad visa actually processed smoothly?

But user data is noisy. It must be moderated, normalised and tagged by date, city, lifestyle, family type, income level, visa status and language ability.

## 9.4. Do they use crowdsourcing?

Yes. Crowdsourcing is central to cost-of-living and digital-nomad products. Numbeo says it uses crowdsourcing for cost-of-living data [S09]. Expatistan states that users enter city prices collaboratively [S11]. Nomad List / Nomads.com started from a crowdsourced spreadsheet but recognises consistency challenges in crowdsourced data [S12].

Crowdsourcing works best for:

- food prices;
- informal rent ranges;
- coworking availability;
- internet reliability;
- local bureaucracy stories;
- local language barriers;
- neighbourhood experience;
- real wait times;
- qualitative warnings.

Crowdsourcing works poorly for:

- visa eligibility;
- tax residence;
- citizenship law;
- family reunification rules;
- employment sponsorship rules;
- real-estate legal rights;
- healthcare entitlement;
- school admission law;
- sanctions and banking compliance.

The correct approach is not to avoid crowdsourcing, but to label it honestly: “community signal”, not “official rule”.

## 9.5. Do they show the last update date?

Some do at page level, but few do it properly at field level. Official government pages often show a last-updated date. Some datasets have release dates or revision metadata. Commercial guides often show article dates. But many relocation pages do not show when each data point was last checked.

For this product category, a proper update model should use four dates:

1. **Effective date** — when the rule entered into force.
2. **Publication date** — when the source was published.
3. **Last checked date** — when the platform last verified the source.
4. **Next review date** — when the rule must be rechecked.

For volatile fields, a page-level “updated in 2026” is not enough. The platform should show freshness per field:

- Skilled Worker salary threshold — checked on specific date.
- Digital nomad income threshold — checked on specific date.
- Citizenship residence period — checked on specific date.
- Tax regime — checked on specific date.
- Housing cost — data collection window.
- Safety index — dataset year.
- User review — submission date.

## 9.6. Do they show links to primary sources?

Often not enough. Legal, tax and visa information should link to primary sources: official law, ministry page, official gazette, tax authority or immigration authority. Many consumer tools instead link to their own guide or to a law-firm interpretation.

A reliable platform should show a source hierarchy:

- **Primary source**: official law, official gazette, government portal, tax authority.
- **Secondary expert source**: law firm, Big Four advisory, migration firm, policy institute.
- **Statistical source**: OECD, World Bank, UN, Eurostat, national statistics.
- **Commercial data source**: paid API, salary database, real-estate listing dataset.
- **Community source**: forum, user review, survey, comment.

The user should be able to click from a summary to the original rule, not only to another summary.

## 9.7. How often are the data updated?

Update frequency depends on the data type:

| Data type | Typical update pattern | Product recommendation |
|---|---:|---|
| Visa and residence rules | Ad hoc; sometimes several times per year | Monitor weekly/monthly for priority countries; alert on official changes |
| Salary thresholds / occupation lists | Often annual or policy-driven | Track official tables and statements |
| Tax rules | Annual budget cycles plus ad hoc reforms | Track tax authority, budget laws, PwC/KPMG/EY updates |
| Citizenship law | Less frequent but high-impact | Track official gazettes and parliamentary bills |
| Property rules for foreigners | Ad hoc; often housing-politics driven | Track land/property authorities and official gazettes |
| Migration flows | Annual or quarterly depending on country | Use OECD, national statistics, Eurostat |
| Cost of living | Continuous but noisy if crowdsourced | Store collection windows and sample size |
| Rent availability | Daily/weekly if listing-based | Needs local listing data and seasonality |
| Safety/crime | Annual official statistics; perception data continuous | Separate official crime from perceived safety |
| Governance/risk indexes | Annual | Use time series, not one-year ranking |
| Community experience | Continuous | Moderate, timestamp and classify by user scenario |

## 9.8. Which data is hardest to obtain and maintain accurately?

The hardest data is not macro data. It is the intersection of law, local practice and personal scenario.

Hardest categories:

1. **Actual processing times.** Official pages often publish formal deadlines, but actual waiting time varies by consulate, office, nationality, backlog and document quality.
2. **Local administrative practice.** Two offices in the same country may interpret the same rule differently.
3. **Rental access for foreigners.** Official housing data rarely captures guarantor requirements, discrimination, cash deposits, local contract norms and short-term supply constraints.
4. **Tax residence and social-security interaction.** Digital nomads, remote employees, freelancers and company owners can easily misread 183-day rules.
5. **Banking access.** New migrants may face KYC, sanctions, proof-of-address and residence-card barriers.
6. **Healthcare access.** Legal entitlement may differ from practical waiting times and private-insurance affordability.
7. **School admission.** Families need age, language, documents, vaccination, district and private/public availability data.
8. **Citizenship route reliability.** Formal residence periods do not capture language exams, integration tests, administrative delays or policy reversal risk.
9. **Safety by neighbourhood.** National homicide rates do not answer where a migrant will actually live.
10. **Contradictory community advice.** People with different passports, income levels, languages and family structures report different realities.

## 9.9. Most reliable sources for migration

Best migration source stack:

- National immigration authorities and official consular portals.
- OECD International Migration Outlook and OECD migration databases [S02, S07].
- UN DESA International Migrant Stock [S01].
- IOM World Migration Report and Migration Data Portal [S03, S08].
- UNHCR for forced displacement, asylum and refugees [S04].
- Eurostat for EU migration and residence statistics.
- National statistical offices.
- Migration Policy Institute for analytical context and official portal directories [S06].

Use advisory/law-firm sources only as interpretation, not as the authoritative rule.

## 9.10. Most reliable sources for laws

Best law source stack:

- Official gazettes and parliamentary databases.
- Ministries of justice, interior, migration, labour, tax and finance.
- EUR-Lex for EU law and Official Journal material [S41].
- N-Lex for EU national-law portals [S42].
- ILO NATLEX for labour/social-security/human-rights legislation [S43].
- FAOLEX for land, environment, natural-resource and property-adjacent law [S44].
- Official court and constitutional-court decisions.
- Official tax authority guidance.
- Official immigration rule statements and consolidated rules.

The product should keep the original legal text, an English summary, a plain-language migrant summary and an expert-risk note separate from each other.

## 9.11. Most reliable sources for cost of living, safety, taxes, work and quality of life

### Cost of living

Best: national statistics, Eurostat, OECD, central-bank inflation/rent data, official housing-cost indicators, real listing data and crowdsourced data used cautiously. Crowdsourced tools such as Numbeo and Expatistan are useful for early estimates but should be labelled as crowd data [S09–S11].

### Safety

Best: UNODC homicide data, national police/crime statistics, Global Peace Index, local city crime data and travel advisories [S56–S57]. Perceived safety should be shown separately.

### Taxes

Best: official tax authorities, official budget laws, OECD tax datasets and Big Four tax summaries such as PwC Worldwide Tax Summaries [S40, S45].

### Work

Best: official labour statistics, World Bank unemployment data, OECD labour-market data, national vacancy statistics, LinkedIn/job-board trend data and salary databases [S59]. Job-board data is useful but biased toward online white-collar jobs.

### Quality of life

Best: OECD Better Life Index, UN/World Bank indicators, healthcare and education statistics, Eurostat, InterNations survey data and local experience reports [S14–S15, S58, S60]. Subjective quality of life should not be mixed blindly with objective indicators.
