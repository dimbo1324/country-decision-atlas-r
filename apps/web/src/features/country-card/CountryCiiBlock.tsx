import {
  Badge,
  Card,
  CriteriaWeightBars,
  ProgressRing,
  RadarChart,
} from "@country-decision-atlas/ui";
import type { CountryReadModelResponse } from "../../shared/api/countries";
import type { SupportedLocale } from "../../shared/lib/locale";
import { EmptyState } from "../../shared/ui/EmptyState";
import { AIExplainNumberButton } from "../ai-assistant";

type CiiData = NonNullable<CountryReadModelResponse["cii"]>;
type CiiMetric = NonNullable<CiiData["metrics"]>[number];

type CountryCiiBlockProps = {
  cii: CiiData | null | undefined;
  countrySlug: string;
  locale: SupportedLocale;
};

const METRIC_LABEL_RU: Record<string, string> = {
  rule_of_law: "Верховенство права",
  economic_freedom: "Экон. свобода",
  political_stability: "Пол. стабильность",
  safety: "Безопасность",
  corruption: "Антикоррупция",
  digital_access: "Цифровой доступ",
};

function scoreAccent(score: number): "sage" | "gold" | "terra" {
  if (score >= 65) return "sage";
  if (score >= 40) return "gold";
  return "terra";
}

function metricLabel(metric: CiiMetric): string {
  return METRIC_LABEL_RU[metric.slug] ?? metric.name_en;
}

export function CountryCiiBlock({
  cii,
  countrySlug,
  locale,
}: CountryCiiBlockProps) {
  if (!cii) {
    return (
      <EmptyState message="CII-данные для этой страны ещё не рассчитаны." />
    );
  }

  const metrics = cii.metrics ?? [];
  const overallAccent = scoreAccent(cii.overall_score);

  return (
    <div data-testid="cii-block">
      <Card
        accent={overallAccent}
        interactive={false}
        className="flex flex-col gap-6"
      >
        <div className="flex flex-wrap items-center justify-between gap-4">
          <ProgressRing
            value={Math.round(cii.overall_score)}
            label="CII из 100"
            size={128}
            accent={overallAccent}
            active
            mode="static"
          />
          <div className="flex flex-1 flex-wrap items-center gap-2">
            <Badge variant="trust">
              Уверенность: {cii.confidence ?? "н/д"}
            </Badge>
            <Badge
              variant={
                cii.drift != null && cii.drift > 0 ? "positive" : "default"
              }
            >
              Динамика:{" "}
              {cii.drift != null
                ? `${cii.drift > 0 ? "+" : ""}${cii.drift.toFixed(1)}`
                : "н/д"}
            </Badge>
            <Badge variant="default">Версия {cii.version}</Badge>
            {cii.aggregation_method && (
              <Badge variant="default">{cii.aggregation_method}</Badge>
            )}
          </div>
          <AIExplainNumberButton
            numberType="cii_score"
            countrySlug={countrySlug}
            value={cii.overall_score}
            locale={locale}
          />
        </div>

        {metrics.length > 0 && (
          <div className="grid grid-cols-1 gap-8 md:grid-cols-2">
            <div className="aspect-square w-full max-w-[320px] justify-self-center">
              <RadarChart
                axes={metrics.map(metricLabel)}
                series={[
                  {
                    label: "CII",
                    values: metrics.map((m) => m.score),
                    accent: overallAccent,
                  },
                ]}
                active
                mode="static"
              />
            </div>
            <CriteriaWeightBars
              active
              criteria={metrics.map((m) => ({
                label: metricLabel(m),
                contribution: Math.round(m.score - 50),
                accent: scoreAccent(m.score),
              }))}
            />
          </div>
        )}

        <p className="text-c4 font-mono text-[9px] leading-relaxed tracking-[0.05em] uppercase">
          CII — составной индекс: верховенство права, экон. свобода, полит.
          стабильность, безопасность, антикоррупция, цифровой доступ. Выше =
          лучше.
        </p>
      </Card>
    </div>
  );
}
