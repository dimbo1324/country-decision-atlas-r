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
          label="Всего доказательств"
        />
        <Stat
          value={evidenceSummary.high_confidence}
          label="Высокая достоверность"
        />
        <Stat
          value={evidenceSummary.medium_confidence}
          label="Средняя достоверность"
        />
        <Stat
          value={evidenceSummary.low_confidence}
          label="Низкая достоверность"
        />
      </div>

      <Kicker>Карточка → оценка → доказательство → источник</Kicker>

      <div className="flex flex-wrap gap-4">
        <Link
          href={routes.legalSignalsForCountry(countrySlug)}
          className="text-gold3 hover:text-gold text-sm transition-colors duration-300"
        >
          Правовые сигналы <ArrowNext />
        </Link>
        <Link
          href={routes.sourcesForCountry(countrySlug)}
          className="text-gold3 hover:text-gold text-sm transition-colors duration-300"
        >
          Все источники <ArrowNext />
        </Link>
      </div>
    </div>
  );
}
