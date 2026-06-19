import type { CountryReadModelResponse } from "../../shared/api/countries";

type CountryEvidenceSummaryProps = {
  evidenceSummary: CountryReadModelResponse["evidence_summary"];
};

export function CountryEvidenceSummary({
  evidenceSummary,
}: CountryEvidenceSummaryProps) {
  return (
    <div className="summaryGrid">
      <div className="summaryItem">
        <span className="summaryValue">{evidenceSummary.total}</span>
        <span className="summaryLabel">Total</span>
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
  );
}
