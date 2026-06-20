import type { CountryReadModelResponse } from "../../shared/api/countries";

type CountryUserStoriesSummaryProps = {
  userStoriesSummary: CountryReadModelResponse["user_stories_summary"];
};

export function CountryUserStoriesSummary({
  userStoriesSummary,
}: CountryUserStoriesSummaryProps) {
  return (
    <div className="summaryGrid">
      <div className="summaryItem">
        <span className="summaryValue">{userStoriesSummary.total}</span>
        <span className="summaryLabel">Всего историй</span>
      </div>
      <div className="summaryItem">
        <span className="summaryValue">{userStoriesSummary.synthetic}</span>
        <span className="summaryLabel">Синтетические</span>
      </div>
      {userStoriesSummary.average_satisfaction_score !== null &&
        userStoriesSummary.average_satisfaction_score !== undefined && (
          <div className="summaryItem">
            <span className="summaryValue">
              {userStoriesSummary.average_satisfaction_score}
            </span>
            <span className="summaryLabel">Ср. удовлетворённость</span>
          </div>
        )}
    </div>
  );
}
