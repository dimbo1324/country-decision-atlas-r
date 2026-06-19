import Link from "next/link";
import type { CountryReadModelResponse } from "../../shared/api/countries";
import { routes } from "../../shared/lib/routes";

type CountryEvidenceSummaryProps = {
  evidenceSummary: CountryReadModelResponse["evidence_summary"];
  countrySlug: string;
  locale: string;
  sourceSummary?: string | null;
};

export function CountryEvidenceSummary({
  evidenceSummary,
  countrySlug,
  locale,
  sourceSummary,
}: CountryEvidenceSummaryProps) {
  return (
    <div className="evidenceTraceability" data-testid="evidence-traceability">
      {sourceSummary && <p className="evidenceSourceSummary">{sourceSummary}</p>}

      <div className="summaryGrid">
        <div className="summaryItem">
          <span className="summaryValue">{evidenceSummary.total}</span>
          <span className="summaryLabel">Total evidence</span>
        </div>
        <div className="summaryItem">
          <span className="summaryValue">{evidenceSummary.high_confidence}</span>
          <span className="summaryLabel">High confidence</span>
        </div>
        <div className="summaryItem">
          <span className="summaryValue">{evidenceSummary.medium_confidence}</span>
          <span className="summaryLabel">Medium confidence</span>
        </div>
        <div className="summaryItem">
          <span className="summaryValue">{evidenceSummary.low_confidence}</span>
          <span className="summaryLabel">Low confidence</span>
        </div>
      </div>

      <div className="traceChain">
        Trace: country card → score breakdown → evidence → source
      </div>

      <div className="cardActions">
        <Link
          href={routes.legalSignalsForCountry(countrySlug, locale)}
          className="internalLink"
        >
          Browse legal signals →
        </Link>
        <Link
          href={routes.sourcesForCountry(countrySlug, locale)}
          className="internalLink"
        >
          Browse all sources →
        </Link>
      </div>
    </div>
  );
}
