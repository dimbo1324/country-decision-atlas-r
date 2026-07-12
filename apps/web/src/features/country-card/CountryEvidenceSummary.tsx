import { Link } from "../../i18n/navigation";
import type { CountryReadModelResponse } from "../../shared/api/countries";
import { routes } from "../../shared/lib/routes";

type CountryEvidenceSummaryProps = {
  evidenceSummary: CountryReadModelResponse["evidence_summary"];
  countrySlug: string;
  sourceSummary?: string | null;
};

export function CountryEvidenceSummary({
  evidenceSummary,
  countrySlug,
  sourceSummary,
}: CountryEvidenceSummaryProps) {
  return (
    <div
      className="evidenceTraceability"
      data-testid="evidence-traceability"
    >
      {sourceSummary && (
        <p className="evidenceSourceSummary">{sourceSummary}</p>
      )}

      <div className="summaryGrid">
        <div className="summaryItem">
          <span className="summaryValue">{evidenceSummary.total}</span>
          <span className="summaryLabel">Всего доказательств</span>
        </div>
        <div className="summaryItem">
          <span className="summaryValue">
            {evidenceSummary.high_confidence}
          </span>
          <span className="summaryLabel">Высокая достоверность</span>
        </div>
        <div className="summaryItem">
          <span className="summaryValue">
            {evidenceSummary.medium_confidence}
          </span>
          <span className="summaryLabel">Средняя достоверность</span>
        </div>
        <div className="summaryItem">
          <span className="summaryValue">{evidenceSummary.low_confidence}</span>
          <span className="summaryLabel">Низкая достоверность</span>
        </div>
      </div>

      <div className="traceChain">
        Трассировка: карточка → оценка → доказательство → источник
      </div>

      <div className="cardActions">
        <Link
          href={routes.legalSignalsForCountry(countrySlug)}
          className="internalLink"
        >
          Правовые сигналы →
        </Link>
        <Link
          href={routes.sourcesForCountry(countrySlug)}
          className="internalLink"
        >
          Все источники →
        </Link>
      </div>
    </div>
  );
}
