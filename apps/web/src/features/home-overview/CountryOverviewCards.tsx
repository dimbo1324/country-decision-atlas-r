import Link from "next/link";
import type { LocaleCode } from "../../shared/api/countries";
import type { CountryOverviewCard } from "../../shared/api/home";

export function CountryOverviewCards({
  countries,
  locale,
}: {
  countries: CountryOverviewCard[];
  locale: LocaleCode;
}) {
  return (
    <section className="homeOverviewSection" aria-labelledby="home-countries-title">
      <div className="homeSectionHeading">
        <h2 id="home-countries-title">Обзор стран</h2>
        <Link href={`/countries?locale=${locale}`}>Перейти к странам</Link>
      </div>
      <div className="homeCountryCards" data-testid="home-country-cards">
        {countries.map((country) => (
          <article className="homeOverviewCard" key={country.slug}>
            <div className="homeCountryOverviewHeader">
              <div>
                <h3>{country.name}</h3>
                <span>{country.iso2}</span>
              </div>
              <strong className={scoreClass(country.average_score)}>
                {formatScore(country.average_score)}
              </strong>
            </div>
            <dl className="homeCountryMetrics">
              <div>
                <dt>Сильнейший сценарий</dt>
                <dd>
                  {country.best_scenario_name ?? "Нет данных"}
                  {country.best_score != null && ` · ${country.best_score.toFixed(1)}`}
                </dd>
              </div>
              <div>
                <dt>Слабейший сценарий</dt>
                <dd>
                  {country.weakest_scenario_name ?? "Нет данных"}
                  {country.weakest_score != null &&
                    ` · ${country.weakest_score.toFixed(1)}`}
                </dd>
              </div>
              <div>
                <dt>Уверенность</dt>
                <dd>{confidenceLabel(country.confidence)}</dd>
              </div>
            </dl>
            <Link href={`/countries/${country.slug}?locale=${locale}`}>
              Открыть карточку страны
            </Link>
          </article>
        ))}
      </div>
    </section>
  );
}

function formatScore(score: number | null | undefined) {
  return score == null ? "—" : score.toFixed(1);
}

function scoreClass(score: number | null | undefined) {
  if (score == null) return "homeScoreMissing";
  if (score >= 70) return "homeScoreStrong";
  if (score >= 50) return "homeScoreModerate";
  return "homeScoreWeak";
}

function confidenceLabel(confidence: string | null | undefined) {
  if (confidence === "high") return "Высокая";
  if (confidence === "medium") return "Средняя";
  if (confidence === "low") return "Низкая";
  return "Нет данных";
}
