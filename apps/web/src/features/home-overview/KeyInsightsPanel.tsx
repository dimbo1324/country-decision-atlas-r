import { useTranslations } from "next-intl";
import { Badge, Card, type BadgeVariant } from "@country-decision-atlas/ui";
import { Link } from "../../i18n/navigation";
import type { HomeKeyInsight } from "../../shared/api/home";

const SEVERITY_KEY: Record<string, string> = {
  info: "severityInfo",
  positive: "severityPositive",
  warning: "severityWarning",
  risk: "severityRisk",
};

const SEVERITY_VARIANT: Record<string, BadgeVariant> = {
  info: "info",
  positive: "positive",
  warning: "warning",
  risk: "negative",
};

export function KeyInsightsPanel({ insights }: { insights: HomeKeyInsight[] }) {
  const t = useTranslations("home");
  return (
    <section aria-labelledby="home-insights-title">
      <h2
        id="home-insights-title"
        className="font-display mb-5 text-2xl font-semibold"
      >
        {t("keyInsightsTitle")}
      </h2>
      <div
        className="flex flex-col gap-3"
        data-testid="home-key-insights"
      >
        {insights.length === 0 ? (
          <p className="text-c3 text-sm">{t("keyInsightsEmpty")}</p>
        ) : (
          insights.map((insight) => (
            <Link
              key={`${insight.kind}:${insight.target_url}`}
              href={insight.target_url}
            >
              <Card
                interactive={false}
                className="flex flex-col gap-2"
              >
                <Badge
                  variant={SEVERITY_VARIANT[insight.severity] ?? "default"}
                >
                  {SEVERITY_KEY[insight.severity]
                    ? t(SEVERITY_KEY[insight.severity])
                    : insight.severity}
                </Badge>
                <h3 className="font-display text-base font-semibold">
                  {insight.title}
                </h3>
                <p className="text-c3 text-sm leading-relaxed">
                  {insight.summary}
                </p>
              </Card>
            </Link>
          ))
        )}
      </div>
    </section>
  );
}
