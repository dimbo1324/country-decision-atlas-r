import { useTranslations } from "next-intl";
import {
  Badge,
  Card,
  GaugeArc,
  scoreLabelStyle,
} from "@country-decision-atlas/ui";
import type { CountryReadModelResponse } from "../../shared/api/countries";
import { EmptyState } from "../../shared/ui/EmptyState";
import { LocalizationBadge } from "../../shared/ui/LocalizationBadge";
import { ScoreBreakdown } from "./ScoreBreakdown";

type CountryScoresProps = {
  scores: CountryReadModelResponse["scores"];
  sources: CountryReadModelResponse["sources"];
};

function scoreToLabel(score: number): string {
  if (score >= 65) return "excellent";
  if (score >= 50) return "strong";
  if (score >= 35) return "moderate";
  if (score >= 20) return "limited";
  return "weak";
}

export function CountryScores({ scores, sources }: CountryScoresProps) {
  const t = useTranslations("countryScores");
  const sourcesById = new Map(sources.map((s) => [s.id, s]));

  if (!scores || scores.length === 0) {
    return <EmptyState message={t("empty")} />;
  }

  return (
    <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
      {scores.map((score) => {
        const { accent } = scoreLabelStyle(scoreToLabel(score.score));
        return (
          <Card
            key={score.id}
            accent={accent}
            interactive={false}
            className="flex flex-col gap-4"
          >
            <div className="flex items-center justify-between gap-3">
              <h3 className="font-display text-lg font-semibold">
                {score.scenario_title}
              </h3>
              <LocalizationBadge
                localization={score.localization}
                compact
              />
            </div>
            <GaugeArc
              value={score.score}
              label={t("gaugeLabel")}
              active
              accent={accent}
              width={180}
              mode="static"
            />
            {score.confidence && (
              <Badge variant="trust">
                {t("confidenceLabel", { value: score.confidence })}
              </Badge>
            )}
            {score.explanation && (
              <p className="text-c3 text-sm leading-relaxed">
                {score.explanation}
              </p>
            )}
            {score.breakdowns && score.breakdowns.length > 0 && (
              <details className="group">
                <summary className="font-mono text-c3 hover:text-gold cursor-pointer text-[9px] tracking-[0.15em] uppercase transition-colors duration-300">
                  {t("breakdownToggle")}
                </summary>
                <div className="mt-4">
                  <ScoreBreakdown
                    breakdowns={score.breakdowns}
                    sourcesById={sourcesById}
                  />
                </div>
              </details>
            )}
          </Card>
        );
      })}
    </div>
  );
}
