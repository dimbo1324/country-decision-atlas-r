import { useTranslations } from "next-intl";
import { Counter } from "@country-decision-atlas/ui";
import type { CountryReadModelResponse } from "../../shared/api/countries";

type CountryUserStoriesSummaryProps = {
  userStoriesSummary: CountryReadModelResponse["user_stories_summary"];
};

function Stat({ value, label }: { value: number; label: string }) {
  return (
    <div className="flex flex-col gap-1">
      <span className="font-display text-gold3 text-3xl font-bold">
        <Counter
          value={value}
          active
        />
      </span>
      <span className="font-mono text-c4 text-[9px] tracking-[0.15em] uppercase">
        {label}
      </span>
    </div>
  );
}

export function CountryUserStoriesSummary({
  userStoriesSummary,
}: CountryUserStoriesSummaryProps) {
  const t = useTranslations("countryUserStories");
  return (
    <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
      <Stat
        value={userStoriesSummary.total}
        label={t("total")}
      />
      <Stat
        value={userStoriesSummary.synthetic}
        label={t("synthetic")}
      />
      {userStoriesSummary.average_satisfaction_score !== null &&
        userStoriesSummary.average_satisfaction_score !== undefined && (
          <Stat
            value={userStoriesSummary.average_satisfaction_score}
            label={t("avgSatisfaction")}
          />
        )}
    </div>
  );
}
