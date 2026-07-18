import { useTranslations } from "next-intl";
import { Counter, Kicker } from "@country-decision-atlas/ui";
import { Link } from "../../i18n/navigation";
import type { CountryReadModelResponse } from "../../shared/api/countries";
import { routes } from "../../shared/lib/routes";
import { ArrowNext } from "../../shared/ui/LinkArrow";

type CountryEvidenceSummaryProps = {
  evidenceSummary: CountryReadModelResponse["evidence_summary"];
  countrySlug: string;
  sourceSummary?: string | null;
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

export function CountryEvidenceSummary({
  evidenceSummary,
  countrySlug,
  sourceSummary,
}: CountryEvidenceSummaryProps) {
  const t = useTranslations("countryEvidenceSummary");
  return (
    <div
      className="flex flex-col gap-5"
      data-testid="evidence-traceability"
    >
      {sourceSummary && (
        <p className="text-c3 text-sm leading-relaxed">{sourceSummary}</p>
      )}

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <Stat
          value={evidenceSummary.total}
          label={t("statTotal")}
        />
        <Stat
          value={evidenceSummary.high_confidence}
          label={t("statHighConfidence")}
        />
        <Stat
          value={evidenceSummary.medium_confidence}
          label={t("statMediumConfidence")}
        />
        <Stat
          value={evidenceSummary.low_confidence}
          label={t("statLowConfidence")}
        />
      </div>

      <Kicker>{t("pipelineKicker")}</Kicker>

      <div className="flex flex-wrap gap-4">
        <Link
          href={routes.legalSignalsForCountry(countrySlug)}
          className="text-gold3 hover:text-gold text-sm transition-colors duration-300"
        >
          {t("legalSignalsLink")} <ArrowNext />
        </Link>
        <Link
          href={routes.sourcesForCountry(countrySlug)}
          className="text-gold3 hover:text-gold text-sm transition-colors duration-300"
        >
          {t("allSourcesLink")} <ArrowNext />
        </Link>
      </div>
    </div>
  );
}
