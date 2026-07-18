import { useTranslations } from "next-intl";
import { Badge } from "@country-decision-atlas/ui";
import type { DecisionPersonalizationResponse } from "../../shared/api/decision";
import type { SupportedLocale } from "../../shared/lib/locale";
import { useAppLocale } from "../../shared/lib/useAppLocale";
import {
  DECISION_CRITERIA_LABELS,
  type DecisionCriterion,
} from "./decision-criteria-labels";

type DecisionPersonalizationSummaryProps = {
  personalization: DecisionPersonalizationResponse;
};

function labelFor(criterion: string, locale: SupportedLocale): string {
  return criterion in DECISION_CRITERIA_LABELS[locale]
    ? DECISION_CRITERIA_LABELS[locale][criterion as DecisionCriterion]
    : criterion;
}

export function DecisionPersonalizationSummary({
  personalization,
}: DecisionPersonalizationSummaryProps) {
  const t = useTranslations("decisionPersonalization");
  const locale = useAppLocale();
  if (!personalization.custom_weights_applied) {
    return null;
  }

  const sortedWeights = [...(personalization.effective_weights ?? [])].sort(
    (a, b) => b.weight - a.weight,
  );
  const topWeights = sortedWeights.slice(0, 3);

  return (
    <div
      className="flex flex-col gap-3"
      data-testid="decision-personalization-result"
    >
      <p className="text-c2 text-sm">{t("adapted")}</p>
      <div className="flex items-center gap-2">
        <span className="text-c4 text-xs">{t("weightMode")}</span>
        <Badge variant="default">{personalization.weight_mode}</Badge>
      </div>
      {personalization.persona_slug && (
        <div className="flex items-center gap-2">
          <span className="text-c4 text-xs">{t("persona")}</span>
          <strong className="text-c1 text-sm">
            {personalization.persona_slug}
          </strong>
        </div>
      )}
      <p className="font-mono text-c4 text-[9px] tracking-[0.2em] uppercase">
        {t("topPriorities")}
      </p>
      <ul className="text-c3 flex flex-col gap-1 text-sm">
        {topWeights.map((item) => (
          <li key={item.criterion}>
            {labelFor(item.criterion, locale)}: {Math.round(item.weight * 100)}%
          </li>
        ))}
      </ul>
      <details>
        <summary className="font-mono text-c3 hover:text-gold cursor-pointer text-[9px] tracking-[0.15em] uppercase transition-colors duration-300">
          {t("allPriorities")}
        </summary>
        <ul className="text-c3 mt-2 flex flex-col gap-1 text-sm">
          {sortedWeights.map((item) => (
            <li key={item.criterion}>
              {labelFor(item.criterion, locale)}:{" "}
              {Math.round(item.weight * 100)}%
            </li>
          ))}
        </ul>
      </details>
    </div>
  );
}
