import { useTranslations } from "next-intl";
import {
  Badge,
  Card,
  CriteriaWeightBars,
  ProgressRing,
  RadarChart,
} from "@country-decision-atlas/ui";
import type { CountryReadModelResponse } from "../../shared/api/countries";
import type { SupportedLocale } from "../../shared/lib/locale";
import { useAppLocale } from "../../shared/lib/useAppLocale";
import { EmptyState } from "../../shared/ui/EmptyState";
import { GlossaryTerm } from "../../shared/ui/GlossaryTerm";
import { AIExplainNumberButton } from "../ai-assistant";

type CiiData = NonNullable<CountryReadModelResponse["cii"]>;
type CiiMetric = NonNullable<CiiData["metrics"]>[number];

type CountryCiiBlockProps = {
  cii: CiiData | null | undefined;
  countrySlug: string;
  locale: SupportedLocale;
};

const METRIC_LABELS: Record<SupportedLocale, Record<string, string>> = {
  en: {
    rule_of_law: "Rule of law",
    economic_freedom: "Econ. freedom",
    political_stability: "Political stability",
    safety: "Safety",
    corruption: "Anti-corruption",
    digital_access: "Digital access",
  },
  ru: {
    rule_of_law: "Верховенство права",
    economic_freedom: "Экон. свобода",
    political_stability: "Пол. стабильность",
    safety: "Безопасность",
    corruption: "Антикоррупция",
    digital_access: "Цифровой доступ",
  },
  es: {
    rule_of_law: "Estado de derecho",
    economic_freedom: "Libertad económica",
    political_stability: "Estabilidad política",
    safety: "Seguridad",
    corruption: "Anticorrupción",
    digital_access: "Acceso digital",
  },
};

// This block's own score→accent bands -- CountryScores.tsx's
// scoreToLabel() below draws the same 0-100 CII score with different cut
// points (65/50/35/20 vs. this block's 65/40); a pre-existing divergence,
// not something introduced here, named rather than left as bare numbers.
const SCORE_ACCENT_SAGE_THRESHOLD = 65;
const SCORE_ACCENT_GOLD_THRESHOLD = 40;

function scoreAccent(score: number): "sage" | "gold" | "terra" {
  if (score >= SCORE_ACCENT_SAGE_THRESHOLD) return "sage";
  if (score >= SCORE_ACCENT_GOLD_THRESHOLD) return "gold";
  return "terra";
}

function metricLabel(metric: CiiMetric, uiLocale: SupportedLocale): string {
  return METRIC_LABELS[uiLocale][metric.slug] ?? metric.name_en;
}

export function CountryCiiBlock({
  cii,
  countrySlug,
  locale,
}: CountryCiiBlockProps) {
  const t = useTranslations("countryCii");
  const uiLocale = useAppLocale();
  if (!cii) {
    return <EmptyState message={t("empty")} />;
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
            label={t("progressLabel")}
            size={128}
            accent={overallAccent}
            active
            mode="static"
          />
          <div className="flex flex-1 flex-wrap items-center gap-2">
            <Badge variant="trust">
              {t("confidenceLabel", { value: cii.confidence ?? t("na") })}
            </Badge>
            <Badge
              variant={
                cii.drift != null && cii.drift > 0 ? "positive" : "default"
              }
            >
              {t("driftLabel", {
                value:
                  cii.drift != null
                    ? `${cii.drift > 0 ? "+" : ""}${cii.drift.toFixed(1)}`
                    : t("na"),
              })}
            </Badge>
            <Badge variant="default">
              {t("versionLabel", { version: cii.version })}
            </Badge>
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
                axes={metrics.map((m) => metricLabel(m, uiLocale))}
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
                label: metricLabel(m, uiLocale),
                contribution: Math.round(m.score - 50),
                accent: scoreAccent(m.score),
              }))}
            />
          </div>
        )}

        <p className="text-c4 font-mono text-[9px] leading-relaxed tracking-[0.05em] uppercase">
          <GlossaryTerm slug="cii">CII</GlossaryTerm> — {t("description")}
        </p>
      </Card>
    </div>
  );
}
