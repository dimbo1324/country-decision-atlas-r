import Link from "next/link";
import type { HomeKeyInsight } from "../../shared/api/home";

const severityLabels: Record<string, string> = {
  info: "Информация",
  positive: "Сильная сторона",
  warning: "Требует внимания",
  risk: "Риск",
};

export function KeyInsightsPanel({ insights }: { insights: HomeKeyInsight[] }) {
  return (
    <section className="homeOverviewSection" aria-labelledby="home-insights-title">
      <div className="homeSectionHeading">
        <h2 id="home-insights-title">Ключевые выводы</h2>
      </div>
      <div className="homeKeyInsights" data-testid="home-key-insights">
        {insights.length === 0 ? (
          <span>Выводы появятся после обновления аналитических данных.</span>
        ) : (
          insights.map((insight) => (
            <article
              className={`homeInsight homeInsight${capitalize(insight.severity)}`}
              key={`${insight.kind}:${insight.target_url}`}
            >
              <span>{severityLabels[insight.severity] ?? insight.severity}</span>
              <h3>{insight.title}</h3>
              <p>{insight.summary}</p>
              <Link href={insight.target_url}>Подробнее</Link>
            </article>
          ))
        )}
      </div>
    </section>
  );
}

function capitalize(value: string) {
  return `${value.charAt(0).toUpperCase()}${value.slice(1)}`;
}
